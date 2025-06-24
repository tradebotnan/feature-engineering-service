import pandas as pd
from app.preprocessing.data_preprocessor import preprocess_dataframe


def test_preprocess_dataframe_basic():
    df = pd.DataFrame({
        "timestamp": pd.date_range("2024-01-01", periods=3, freq="h", tz="UTC"),
        "open": [1, 2, 3],
        "high": [1, 2, 3],
        "low": [1, 2, 3],
        "close": [1, 2, 3],
        "volume": [10, 20, 30],
    })
    out = preprocess_dataframe(df)
    assert len(out) == 3
