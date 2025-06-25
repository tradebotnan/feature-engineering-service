# Source file: app/enrichment/enrichment_utils.py

import numpy as np


def calculate_days_since(dates, indicator_series):
    last_date = None
    days_since = []
    for flag, current in zip(indicator_series, dates):
        if flag:
            last_date = current
        days_since.append((current - last_date).days if last_date else np.nan)
    return days_since


def calculate_days_until(dates, future_dates):
    future_dates = sorted(set(future_dates))
    j = 0
    days_until = []
    for d in dates:
        while j < len(future_dates) and future_dates[j] < d:
            j += 1
        days_until.append((future_dates[j] - d).days if j < len(future_dates) else np.nan)
    return days_until
