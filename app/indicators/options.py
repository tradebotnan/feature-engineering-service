import pandas as pd
import numpy as np

def add_options_features(df: pd.DataFrame, config: dict) -> pd.DataFrame:
    df = df.copy()

    # Add Put/Call Ratio if present
    if config.get("put_call_ratio", {}).get("enabled", False):
        df["put_call_ratio"] = df.get("put_volume", np.nan) / df.get("call_volume", np.nan)

    # Add Implied Volatility Normalized
    if config.get("iv_normalized", {}).get("enabled", False):
        df["iv_normalized"] = df.get("implied_volatility", np.nan) / df["close"]

    if config.get("put_call_ratio", {}).get("enabled", False):
        if "put_call_ratio" not in df.columns:
            df["put_call_ratio"] = None  # Optional fallback

    if "open_interest_trend" in config:
        periods = config["open_interest_trend"].get("periods", [])
        for period in periods:
            col_name = f"open_interest_trend_{period}"
            if "open_interest" in df.columns:
                df[col_name] = df["open_interest"].rolling(window=period).mean()

    return df
