import numpy as np
def quick_narrative(delta_series):
    total = float(np.nansum(delta_series.values))
    avg = float(np.nanmean(delta_series.values))
    sign = "increase" if total>=0 else "decrease"
    return f"Scenario yields a net {sign} of {total:,.0f} over the horizon (avg {avg:,.0f} per day)."
