# Source file: app\preprocessing\data_preprocessor.py

import pytest

pd = pytest.importorskip("pandas")

from app.preprocessing.data_preprocessor import preprocess_dataframe


def test_preprocess_dataframe():
    df = pd.DataFrame({
        "Open": [1, 2],
        "High": [1, 2],
        "Low": [1, 2],
        "Close": [1, 2],
        "Volume": [10, 20],
        "Timestamp": pd.date_range("2024-01-01", periods=2, freq="D", tz="UTC"),
    })
    result = preprocess_dataframe(df)
    assert list(result.columns) == ["open", "high", "low", "close", "volume", "timestamp"]

