import pytest

pd = pytest.importorskip("pandas")
from app.feature.labeler import apply_labeling_strategy


def test_apply_labeling_strategy_trend():
    df = pd.DataFrame({"close": [1, 2, 3], "timestamp": pd.date_range("2024-01-01", periods=3)})
    config = {"labels": {"trend": {"horizon": 1}}}
    out = apply_labeling_strategy(df, config)
    assert "trend" in out.columns
