import pandas as pd
import pytest

from app.indicators import trend

@pytest.fixture
def sample_trend_data():
    data = {
        "timestamp": pd.date_range(start="2024-01-01", periods=10, freq="D"),
        "open": [100 + i for i in range(10)],
        "high": [101 + i for i in range(10)],
        "low": [99 + i for i in range(10)],
        "close": [100 + i for i in range(10)],
        "volume": [1000 + 10 * i for i in range(10)],
    }
    return pd.DataFrame(data)

def test_add_trend_features_all(sample_trend_data):
    config = {
        "ema": {"periods": [3]},
        "sma": {"periods": [3]},
        "macd": {"enabled": True},
        "trix": {"periods": [3]},
        "vortex": {"periods": [3]},
    }

    df = trend.add_trend_features(sample_trend_data.copy(), config)

    expected_cols = [
        "ema_3", "sma_3", "macd", "macd_signal", "trix_3",
        "vortex_pos_3", "vortex_neg_3"
    ]

    for col in expected_cols:
        assert col in df.columns, f"Missing column: {col}"
        assert df[col].isnull().sum() < len(df), f"All values null in {col}"
