# app/indicators/accumulation_distribution.py

import pandas as pd
from ta.volume import AccDistIndexIndicator

def add_accumulation_distribution(df: pd.DataFrame, config: dict) -> pd.DataFrame:
    """
    Adds Accumulation/Distribution (A/D) line to the dataframe.
    """
    df = df.copy()
    if config.get("enabled", False):
        ad = AccDistIndexIndicator(
            high=df["high"],
            low=df["low"],
            close=df["close"],
            volume=df["volume"]
        )
        df["accum_dist"] = ad.acc_dist_index()
    return df
