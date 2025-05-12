# app/indicators/fundamentals.py

import pandas as pd
import numpy as np

def add_fundamental_features(df: pd.DataFrame, config: dict) -> pd.DataFrame:
    """
    Adds fundamental ratios as placeholders.
    In production, these should be joined from your fundamentals DB table or API feed.
    """
    df = df.copy()
    include = config.get("include", [])

    np.random.seed(42)  # for reproducible dummy data

    if "pe_ratio" in include:
        df["pe_ratio"] = np.random.uniform(10, 25, size=len(df))

    if "eps" in include:
        df["eps"] = np.random.uniform(0.5, 5.0, size=len(df))

    if "dividend_yield" in include:
        df["dividend_yield"] = np.random.uniform(0, 3, size=len(df))

    if "revenue_growth" in include:
        df["revenue_growth"] = np.random.uniform(-0.1, 0.3, size=len(df))

    return df
