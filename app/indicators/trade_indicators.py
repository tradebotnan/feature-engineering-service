import numpy as np
import pandas as pd


def add_all_trade_indicators(df: pd.DataFrame, features: list, window: int = 5) -> pd.DataFrame:
    """
    Adds selected trades-specific indicators based on features list.
    Assumes df has columns: ['symbol', 'price', 'size', 'timestamp'].
    """
    df = df.copy()
    df.sort_values("timestamp", inplace=True)

    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    df["size"] = pd.to_numeric(df["size"], errors="coerce")

    # =========================
    # Basic helpers
    # =========================
    df["price_diff"] = df["price"].diff()

    # =========================
    # Feature: micro_price
    # =========================
    if "micro_price" in features:
        df["micro_price"] = (df["price"] * df["size"]) / df["size"].replace(0, np.nan)

    # =========================
    # Feature: tick_imbalance
    # =========================
    if "tick_imbalance" in features:
        df["tick_direction"] = np.sign(df["price_diff"]).replace({0: np.nan})
        df["tick_direction"] = df["tick_direction"].map({1.0: "uptick", -1.0: "downtick", np.nan: "neutral"})
        df["tick_imbalance"] = (
            df["tick_direction"].map({"uptick": 1, "downtick": -1, "neutral": 0})
            .rolling(window=window)
            .sum()
        )

    # =========================
    # Feature: trade_count_per_second
    # =========================
    if "trade_count_per_second" in features:
        df["trade_count_window"] = df["price"].rolling(window=window).count()
        if pd.api.types.is_datetime64_any_dtype(df["timestamp"]):
            df["seconds"] = (df["timestamp"] - df["timestamp"].iloc[0]).dt.total_seconds()
            df["seconds"] = df["seconds"].ffill()
            df["trade_count_per_second"] = df["trade_count_window"] / window
            df.drop(columns=["seconds", "trade_count_window"], inplace=True)

    # =========================
    # Feature: volume_per_second
    # =========================
    if "volume_per_second" in features:
        df["volume_window"] = df["size"].rolling(window=window).sum()
        if pd.api.types.is_datetime64_any_dtype(df["timestamp"]):
            df["seconds"] = (df["timestamp"] - df["timestamp"].iloc[0]).dt.total_seconds()
            df["seconds"] = df["seconds"].ffill()
            df["volume_per_second"] = df["volume_window"] / window
            df.drop(columns=["seconds", "volume_window"], inplace=True)

    return df
