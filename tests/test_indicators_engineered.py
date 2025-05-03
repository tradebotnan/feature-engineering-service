import numpy as np
import pytest
import pandas as pd
from app.indicators import engineered


@pytest.fixture
def sample_df():
    return pd.DataFrame({
        "timestamp": pd.date_range(start="2024-01-01", periods=10),
        "close": range(100, 110)
    })


def test_add_returns(sample_df):
    result = engineered.add_returns(sample_df.copy(), ["return_1d", "return_5d", "log_return"])
    assert "return_1d" in result.columns
    assert "return_5d" in result.columns
    assert "log_return" in result.columns


def test_add_volatility(sample_df):
    result = engineered.add_volatility(sample_df.copy(), [3])
    assert "volatility_3" in result.columns


def test_add_trend_strength(sample_df):
    result = engineered.add_trend_strength(sample_df.copy(), [3])
    assert "trend_strength_3" in result.columns


def test_add_zscore(sample_df):
    sample_df["rsi_14"] = range(100, 110)
    result = engineered.add_zscore(sample_df.copy(), ["close", "rsi_14"], window=3)
    assert "zscore_close" in result.columns
    assert "zscore_rsi_14" in result.columns

    @pytest.fixture
    def sample_data():
        return pd.DataFrame({
            "timestamp": pd.date_range(start="2024-01-01", periods=10, freq="D"),
            "close": np.linspace(100, 110, 10)
        })

    def test_add_engineered_features(sample_data):
        config = {
            "return": {"include": ["return_1d", "return_5d", "log_return"]}
        }

        df = engineered.add_engineered_features(sample_data.copy(), config)

        expected_cols = ["return_1d", "return_5d", "log_return"]
        for col in expected_cols:
            assert col in df.columns, f"Missing column: {col}"
            assert df[col].isnull().sum() < len(df), f"All values null in {col}"
