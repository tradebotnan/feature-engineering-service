import pandas as pd
from app.preprocessing.data_preprocessor import preprocess_dataframe

def test_preprocess_dataframe_normalizes_columns():
    df = pd.DataFrame({
        "TimeStamp": ["2024-01-01", "2024-01-02"],
        "Open ": [100, 101],
        "CLOSE": [101, 102],
        "HIGH": [102, 103],
        "LOW": [99, 100],
        "Volume": [1000, 1100]
    })
    result = preprocess_dataframe(df)
    assert all(col in result.columns for col in ["timestamp", "open", "close", "high", "low", "volume"])
    assert pd.api.types.is_datetime64_any_dtype(result["timestamp"])