import pandas as pd
from app.enrichment.enrichment_utils import calculate_days_since, calculate_days_until


def test_calculate_days_since():
    dates = pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03"]).date
    flags = [0, 1, 0]
    result = calculate_days_since(dates, flags)
    assert result == [float('nan'), 0, 1]


def test_calculate_days_until():
    dates = pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03"]).date
    future = pd.to_datetime(["2024-01-02", "2024-01-05"]).date
    result = calculate_days_until(dates, future)
    assert result[0] == 1 and result[1] == 0 and result[2] == 2
