from .features import moving_average_baseline

def try_prophet_forecast(df, horizon=90):
    try:
        from prophet import Prophet
    except Exception:
        return None
    m = Prophet(weekly_seasonality=True, yearly_seasonality=True, seasonality_mode='additive')
    m.fit(df.rename(columns={'date':'ds','value':'y'})[['ds','y']])
    fut = m.make_future_dataframe(periods=horizon, freq='D')
    fc = m.predict(fut)
    return fc[['ds','yhat','yhat_lower','yhat_upper']]

def baseline_forecast(df, horizon=90):
    fc = try_prophet_forecast(df, horizon=horizon)
    if fc is not None:
        return fc
    s = df.set_index('date')['value']
    return moving_average_baseline(s, window=14, horizon=horizon)
