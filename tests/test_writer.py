import os
import pandas as pd
from app.feature.writer import write_features
from pathlib import Path

def test_write_features(tmp_path):
    df = pd.DataFrame({
        "close": [100, 101, 102],
        "volume": [1000, 1050, 980]
    })

    feature_file = tmp_path / "AAPL_2023-01-01.parquet"
    success = write_features(df, str(feature_file))

    assert success is True
    assert feature_file.exists()

    df_loaded = pd.read_parquet(feature_file)
    assert df_loaded.equals(df)
