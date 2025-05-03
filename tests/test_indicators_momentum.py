import pandas as pd
import pytest

from app.indicators import momentum

@pytest.fixture
def sample_df():
    data = {
        "timestamp": pd.date_range("2024-01-01", periods=10),
        "open": [100 + i for i in range(10)],
        "high": [102 + i for i in range(10)],
        "low": [98 + i for i in range(10)],
        "close": [101 + i for i in range(10)],
        "volume": [1000 + 100 * i for i in range(10)],
    }
    return pd.DataFrame(data)

def test_add_momentum_features(sample_df):
    config = {
        "rsi": {"periods": [5]},
        "roc": {"periods": [5]},
        "stochastic": {"periods": [5]},
    }

    df = momentum.add_momentum_features(sample_df.copy(), config)

    expected_cols = ["rsi_5", "roc_5", "stoch_k_5", "stoch_d_5"]
    for col in expected_cols:
        assert col in df.columns, f"{col} not found in output"
