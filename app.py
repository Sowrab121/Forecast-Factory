# app.py — ForecastFactory — AI-Driven Scenario Simulator (quiet + deprecation-free)

import warnings
import logging

# ── Silence noisy libs ──────────────────────────────────────────────────────────
logging.getLogger("cmdstanpy").disabled = True        # Prophet backend logs
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)

# ── App imports ─────────────────────────────────────────────────────────────────
import streamlit as st
import pandas as pd
import yaml
from pathlib import Path

from forecastfactory.io_sql import get_engine, init_demo, read_tables
from forecastfactory.models import baseline_forecast
from forecastfactory.scenario import apply_scenario
from forecastfactory.explain import quick_narrative
from forecastfactory.viz import plot_baseline, plot_scenario, plot_delta

# ── Streamlit config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ForecastFactory, Scenario Simulator",
    page_icon="🧪",
    layout="wide",
)

st.title("🧪 ForecastFactory, AI-Driven Scenario Simulator")
st.caption("Baseline forecasts + what-if scenarios (price, ad spend, promo, inventory) with deltas vs baseline.")

# ── Config & Inputs ─────────────────────────────────────────────────────────────
cfg = yaml.safe_load(open("config.yaml"))
db_url = st.text_input("Database URL (SQLAlchemy)", value=cfg.get("database_url", "sqlite:///:memory:"))
horizon = st.slider("Forecast horizon (days)", 30, 365, int(cfg.get("forecast_horizon_days", 90)))
kpi_name = st.selectbox("KPI", ["revenue"], index=0)

# ── Data load ───────────────────────────────────────────────────────────────────
engine = get_engine(db_url)
if "sqlite:///:memory:" in db_url:
    init_demo(engine)

kpi, drv = read_tables(engine)
hist = kpi[kpi["kpi_name"] == kpi_name][["date", "value"]].copy()

# ── Baseline forecast (Prophet if available; fallback MA) ───────────────────────
fc = baseline_forecast(hist, horizon=horizon)

# ── UI: Baseline view ───────────────────────────────────────────────────────────
c1, c2 = st.columns([2, 1], gap="large")
with c1:
    st.subheader("Baseline Forecast")
    fig_base = plot_baseline(hist, fc)
    # Use new Streamlit API: width="stretch" (no deprecated use_container_width)
    st.plotly_chart(fig_base, config={"displayModeBar": False})
with c2:
    last_val = hist["value"].iloc[-1] if len(hist) else 0.0
    st.metric("Last value", f"{last_val:,.0f}")
    # 30-day mean of forecast (guard for short horizons)
    window = min(30, len(fc))
    fc_avg_30 = fc["yhat"].tail(window).mean() if window > 0 else 0.0
    st.metric("Forecast avg (next 30d)", f"{fc_avg_30:,.0f}")

st.divider()

# ── Scenario builder ────────────────────────────────────────────────────────────
st.subheader("Scenario Builder")
col1, col2, col3, col4 = st.columns(4)
with col1:
    price_pct = st.number_input("Price change (%)", value=0.0, step=1.0) / 100.0
with col2:
    spend_pct = st.number_input("Ad spend change (%)", value=0.0, step=5.0) / 100.0
with col3:
    promo = st.toggle("Promo active", value=False)
with col4:
    cap = st.number_input("Inventory cap (0 = none)", value=0.0, step=100.0)

cap_val = None if cap <= 0 else cap

# Forecast window for scenario
date_from = fc["ds"].iloc[0]
date_to = fc["ds"].iloc[-1]
win = (date_from, date_to)

# Apply scenario
scenario = apply_scenario(
    fc,
    drv,
    win,
    price_pct=price_pct,
    spend_pct=spend_pct,
    promo=promo,
    cap=cap_val,
)

# ── UI: Scenario results ────────────────────────────────────────────────────────
st.subheader("Scenario vs Baseline")
fig_cmp = plot_scenario(fc, scenario)
st.plotly_chart(fig_cmp,  config={"displayModeBar": False})

fig_delta = plot_delta(scenario)
st.plotly_chart(fig_delta, config={"displayModeBar": False})

st.info(quick_narrative(scenario["delta"]))

# ── Export ──────────────────────────────────────────────────────────────────────
if st.button("Export scenario to CSV"):
    out = Path("output/exports")
    out.mkdir(parents=True, exist_ok=True)
    fn = out / f"scenario_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv"
    scenario.to_csv(fn, index=False)
    st.success(f"Saved: {fn}")
