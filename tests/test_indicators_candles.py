import pytest
import pandas as pd
from app.feature.generator import generate_features


@pytest.fixture
def sample_dataframe():
    return pd.DataFrame({
        "timestamp": pd.date_range(start="2024-01-01", periods=10, freq="D"),
        "open": range(100, 110),
        "high": [x + 2 for x in range(100, 110)],
        "low": [x - 2 for x in range(100, 110)],
        "close": range(101, 111),
        "volume": [1000 + x * 10 for x in range(10)]
    })


@pytest.fixture
def rich_config():
    return {
        "candle_features": {
            "patterns": {"enabled": True, "include": ["doji", "engulfing"]},
            "engineered": {"include": ["body_size"]}
        },
        "momentum_indicators": {
            "sma": {"periods": [5]},
            "ema": {"periods": [5]},
            "macd": {"enabled": True},
            "trix": {"periods": [5]},
            "vortex": {"periods": [5]},
            "rsi": {"periods": [5]},
            "roc": {"periods": [5]},
            "stochastic": {"periods": [5]}
        },
        "volatility_indicators": {
            "atr": {"periods": [5]},
            "bollinger": {"periods": [5]}
        },
        "volume_indicators": {
            "obv": {"enabled": True},
            "mfi": {"periods": [5]},
            "volume_ema": {"periods": [5]},
            "volume_roc": {"periods": [5]},
            "vwap": {"enabled": True},
            "price_vwap_ratio": {"enabled": True}
        },
        "engineered_features": {
            "returns": {"periods": [1, 5]},
            "log_return": True,
            "volatility": {"periods": [5]},
            "trend_strength": {"periods": [5]},
            "zscore_close": {"enabled": True}
        }
    }



def test_generate_features_success(sample_dataframe, rich_config):
    result = generate_features(sample_dataframe, rich_config)

    expected = [
        "sma_5", "ema_5", "macd", "macd_signal", "trix_5", "vortex_pos_5", "rsi_5", "roc_5",
        "stoch_k_5", "stoch_d_5", "atr_5", "bollinger_h_5", "bollinger_l_5",
        "obv", "mfi_5", "volume_ema_5", "volume_roc_5", "vwap", "price_vwap_ratio",
        "return_1d", "return_5d", "log_return", "volatility_5", "trend_strength_5", "zscore_close",
        "pattern_doji", "pattern_engulfing", "body_size"
    ]
    actual_columns = set(result.columns)
    matched = [col for col in expected if col in actual_columns]

    assert len(matched) >= 15
    assert result.shape[0] >= 1


def test_generate_features_handles_empty_df():
    empty_df = pd.DataFrame(columns=["timestamp", "open", "high", "low", "close", "volume"])
    config = {
        "price_indicators": {},
        "volume_indicators": {},
        "engineered_features": {},
        "candle_features": {}
    }
    result = generate_features(empty_df, config)
    assert isinstance(result, pd.DataFrame)
    assert result.empty
