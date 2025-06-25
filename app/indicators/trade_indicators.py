# Source file: app/enrichment/trade_indicators.py

import numpy as np
import pandas as pd


def add_all_trade_indicators(df: pd.DataFrame, features: list, window: int = 5) -> pd.DataFrame:
    """
    Adds selected trade-level indicators to a DataFrame.
    Expects `tick_direction` and `price_diff` to be already present.
    """
    df = df.copy()
    df.sort_values("timestamp", inplace=True)

    # Sanitize and validate inputs
    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    df["size"] = pd.to_numeric(df["size"], errors="coerce")
    df.dropna(subset=["price", "size", "timestamp"], inplace=True)

    if not pd.api.types.is_datetime64_any_dtype(df["timestamp"]):
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

    # ✅ Enforce dependencies
    if "tick_imbalance" in features and "tick_direction" not in df.columns:
        raise ValueError("❌ tick_direction must be precomputed by microstructure_enricher")

    if "price_diff" in features and "price_diff" not in df.columns:
        raise ValueError("❌ price_diff must be precomputed by microstructure_enricher")

    if "tick_imbalance" in features:
        df["tick_imbalance"] = (
            df["tick_direction"].map({"uptick": 1, "downtick": -1, "neutral": 0})
            .rolling(window=window, min_periods=1)
            .sum()
        )

    if "micro_price" in features:
        df["micro_price"] = (df["price"] * df["size"]) / df["size"].replace(0, np.nan)

    if "trade_count_per_second" in features:
        df["trade_count_per_second"] = (
            df["price"].rolling(window=window, min_periods=1).count() / window
        )

    if "volume_per_second" in features:
        df["volume_per_second"] = (
            df["size"].rolling(window=window, min_periods=1).sum() / window
        )

    return df
