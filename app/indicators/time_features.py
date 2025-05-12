import pandas as pd

def add_time_features(df: pd.DataFrame, config: dict) -> pd.DataFrame:
    """
    Extract time features like hour, minute, day of week, session buckets.
    """
    df = df.copy()
    if "timestamp" in df.columns:
        df["hour"] = df["timestamp"].dt.hour
        df["minute"] = df["timestamp"].dt.minute
        df["day_of_week"] = df["timestamp"].dt.dayofweek
    return df
