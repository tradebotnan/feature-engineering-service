# Source file: app\indicators\trade_indicators.py

import pytest

pd = pytest.importorskip("pandas")

from app.indicators.trade_indicators import add_all_trade_indicators


def test_add_all_trade_indicators():
    df = pd.DataFrame({
        "timestamp": pd.date_range("2024-01-01", periods=3, freq="s"),
        "price": [1.0, 1.1, 1.2],
        "size": [10, 20, 30],
        "tick_direction": ["uptick", "downtick", "neutral"],
        "price_diff": [0.1, -0.1, 0.1],
    })
    result = add_all_trade_indicators(df, ["tick_imbalance"], window=2)
    assert "tick_imbalance" in result.columns

