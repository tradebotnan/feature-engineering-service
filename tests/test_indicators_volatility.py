import pytest
import pandas as pd
from app.indicators.volatility import (
    add_atr,
    add_bollinger_bands,
    add_true_range_pct,
    add_volatility_burst,
)


@pytest.fixture
def sample_vol_data():
    return pd.DataFrame({
        "timestamp": pd.date_range(start="2024-01-01", periods=30, freq="D"),
        "open": range(100, 130),
        "high": [x + 2 for x in range(100, 130)],
        "low": [x - 2 for x in range(100, 130)],
        "close": range(101, 131),
        "volume": [1000 + x * 10 for x in range(30)]
    })


def test_add_atr(sample_vol_data):
    df = add_atr(sample_vol_data.copy(), periods=[5])
    assert "atr_5" in df.columns


def test_add_bollinger_bands(sample_vol_data):
    df = add_bollinger_bands(sample_vol_data.copy(), configs=[{"periods": 20, "stddev": 2}])
    assert "bollinger_h_20" in df.columns
    assert "bollinger_l_20" in df.columns


def test_add_true_range_pct(sample_vol_data):
    df = add_true_range_pct(sample_vol_data.copy(), periods=[5])
    assert "true_range_pct_5" in df.columns


def test_add_volatility_burst(sample_vol_data):
    df = add_volatility_burst(sample_vol_data.copy(), zscore_window=5)
    assert "volatility_burst_z" in df.columns
