import pandas as pd
from .elasticity import apply_price_elasticity, media_response

def apply_scenario(baseline_df, drivers_df, win, price_pct=0.0, spend_pct=0.0, promo=False, cap=None):
    df = baseline_df.copy()
    drv = drivers_df.set_index('date').reindex(df['ds']).ffill().bfill()
    effect = pd.Series(0.0, index=df.index)

    if price_pct != 0.0:
        effect += apply_price_elasticity(df['yhat'], price_pct).values - df['yhat'].values

    if spend_pct != 0.0:
        spend = drv['ad_spend'].copy()
        spend.loc[win[0]:win[1]] = spend.loc[win[0]:win[1]] * (1+spend_pct)
        effect += media_response(spend).values - media_response(drv['ad_spend']).values

    if promo:
        promo_uplift = 0.08
        mask = (df['ds']>=win[0]) & (df['ds']<=win[1])
        effect.loc[mask] += df.loc[mask,'yhat'] * promo_uplift

    scen = df.copy()
    scen['yhat'] = df['yhat'] + effect
    if cap is not None and cap>0:
        scen['yhat'] = scen['yhat'].clip(upper=cap)
    scen['delta'] = scen['yhat'] - df['yhat']
    return scen
