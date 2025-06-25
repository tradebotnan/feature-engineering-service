# Source file: app\indicators\trend.py

import pytest

pd = pytest.importorskip("pandas")

from app.indicators.trend import add_trend_features


def test_add_trend_features():
    df = pd.DataFrame({"close": [1, 2, 3, 4, 5]})
    cfg = {"sma": {"periods": [2]}}
    result = add_trend_features(df, cfg)
    assert "sma_2" in result.columns

