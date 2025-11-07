import pandas as pd

def moving_average_baseline(s, window=14, horizon=90, freq='D'):
    ma = s.rolling(window).mean()
    last = ma.dropna().iloc[-1]
    idx = pd.date_range(s.index.max() + pd.Timedelta(days=1), periods=horizon, freq=freq)
    return pd.DataFrame({'ds': idx, 'yhat': last, 'yhat_lower': last*0.9, 'yhat_upper': last*1.1})
