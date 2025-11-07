import numpy as np
def apply_price_elasticity(series, pct_change, epsilon=-1.2):
    return series * (1 + epsilon * pct_change)

def media_response(spend, alpha=0.3, beta=0.001):
    spend = np.maximum(spend, 0)
    return alpha * np.log1p(beta * spend)
