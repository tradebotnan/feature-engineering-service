# Source file: app\indicators\time_features.py

import pytest

pd = pytest.importorskip("pandas")

from app.indicators.time_features import add_time_features


def test_add_time_features():
    df = pd.DataFrame({"timestamp": pd.date_range("2024-01-01", periods=2, freq="H")})
    result = add_time_features(df)
    assert {"hour", "minute", "day_of_week"}.issubset(result.columns)

