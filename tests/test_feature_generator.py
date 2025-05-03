import pandas as pd
import pytest

from app.feature.generator import generate_features

@pytest.fixture
def sample_df():
    return pd.DataFrame({
        "timestamp": pd.date_range(start="2024-01-01", periods=10, freq="D"),
        "open": [100, 101, 102, 103, 104, 105, 106, 107, 108, 109],
        "high": [102, 103, 104, 105, 106, 107, 108, 109, 110, 111],
        "low": [98, 99, 100, 101, 102, 103, 104, 105, 106, 107],
        "close": [101, 102, 103, 104, 105, 106, 107, 108, 109, 110],
        "volume": [1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900]
    })

@pytest.fixture
def test_config():
    return {
        "momentum_indicators": {"rsi": {"periods": [5]}},
        "trend_indicators": {"ema": {"periods": [5]}},
        "volatility_indicators": {"atr": {"periods": [5]}},
        "volume_indicators": {"obv": {"enabled": True}},
        "engineered_features": {"return": {"include": ["return_1d", "log_return"]}},
        "candle_features": {"patterns": {"enabled": True, "include": ["doji", "engulfing"]}}
    }

def test_generate_features_pattern_detection(sample_df, test_config):
    df = generate_features(sample_df, test_config)

    expected = [
        "rsi_5", "ema_5", "atr_5", "obv", "return_1d", "log_return",
        "pattern_doji", "pattern_engulfing"
    ]

    for col in expected:
        assert col in df.columns, f"Missing expected feature column: {col}"

    assert len(df) > 0
