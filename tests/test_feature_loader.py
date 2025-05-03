import pytest
from pathlib import Path
import pandas as pd
from unittest.mock import patch, MagicMock
from app.feature.loader import load_and_process


@pytest.fixture
def mock_config():
    return {
        "price_indicators": {
            "sma": {"periods": [2]}
        },
        "engineered_features": {
            "return": {"include": ["return_1d"]}
        }
    }


@patch("app.feature.loader.get_env_variable")
@patch("app.feature.loader.update_feature_status")
@patch("app.feature.loader.write_features")
@patch("app.feature.loader.apply_labeling_strategy")
@patch("app.feature.loader.generate_features")
@patch("app.feature.loader.preprocess_dataframe")
@patch("app.feature.loader.pd.read_parquet")
def test_load_and_process_success(mock_read, mock_pre, mock_feat, mock_label, mock_write, mock_update, mock_env, mock_config):
    dummy_df = pd.DataFrame({"close": [100, 101, 102], "timestamp": pd.date_range("2024-01-01", periods=3)})
    mock_read.return_value = dummy_df
    mock_pre.return_value = dummy_df
    mock_feat.return_value = dummy_df
    mock_label.return_value = dummy_df
    mock_env.side_effect = lambda k, default=None: "data/filtered" if "INPUT" in k else "data/features"

    result = load_and_process(Path("data/filtered/stocks/AAPL/2024-01-01.parquet"), "AAPL", "2024-01-01", "day", mock_config)

    assert result is True
    mock_write.assert_called_once()
    mock_update.assert_called_with("AAPL", "2024-01-01", "day", "completed", Path("data/features/stocks/AAPL/2024-01-01.parquet"))


@patch("app.feature.loader.get_env_variable")
@patch("app.feature.loader.update_feature_status")
@patch("app.feature.loader.pd.read_parquet")
def test_load_and_process_failure(mock_read, mock_update, mock_env):
    mock_read.side_effect = Exception("Test failure")
    mock_env.side_effect = lambda k, default=None: "data/filtered" if "INPUT" in k else "data/features"

    result = load_and_process(Path("data/filtered/stocks/FAIL.parquet"), "FAIL", "2024-01-01", "day", {})

    assert result is False
    mock_update.assert_called_with("FAIL", "2024-01-01", "day", "error", "", "Test failure")
