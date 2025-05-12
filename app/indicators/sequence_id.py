# app/indicators/sequence_id.py

import pandas as pd

def add_sequence_id(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds a monotonically increasing sequence id (useful for some ML models).
    """
    df = df.copy()
    df["sequence_id"] = range(1, len(df) + 1)
    return df
