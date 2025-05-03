import pytest
import pandas as pd
from app.feature.labeler import apply_labeling_strategy


@pytest.fixture
def sample_label_data():
    return pd.DataFrame({
        "timestamp": pd.date_range(start="2024-01-01", periods=5, freq="D"),
        "close": [100, 102, 101, 104, 103],
    })


def test_apply_labeling_strategy_with_config(sample_label_data):
    config = {
        "labels": {
            "trend": {"horizon": 1},
            "future_return": {"horizon": 1},
            "return_bin": {"bins": [-1.0, 0.0, 0.01, 0.03]}
        }
    }
    df = apply_labeling_strategy(sample_label_data, config)
    assert "trend" in df.columns
    assert "future_return" in df.columns
    assert "return_bin" in df.columns
    assert not df.empty


def test_apply_labeling_strategy_handles_empty_df():
    df_empty = pd.DataFrame(columns=["timestamp", "close"])
    config = {"labels": {"trend": {"horizon": 1}}}
    result = apply_labeling_strategy(df_empty, config)
    assert isinstance(result, pd.DataFrame)
