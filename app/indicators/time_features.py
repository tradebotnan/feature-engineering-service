# app/indicators/time_features.py

import pandas as pd

def add_time_features(df: pd.DataFrame, config: dict = None) -> pd.DataFrame:
    """
    Adds basic datetime decomposition features.
    """
    df = df.copy()
    if "timestamp" in df.columns:
        df["hour"] = pd.to_datetime(df["timestamp"]).dt.hour
        df["minute"] = pd.to_datetime(df["timestamp"]).dt.minute
        df["day_of_week"] = pd.to_datetime(df["timestamp"]).dt.dayofweek
    return df
