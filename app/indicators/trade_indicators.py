# Source file: app\indicators\trade_indicators.py
# app/indicators/trade_indicators.py
import numpy as np
import pandas as pd


def add_all_trade_indicators(df: pd.DataFrame, window: int = 5) -> pd.DataFrame:
    """
    Add standard trades indicators.
    Assumes df has columns: ['symbol', 'price', 'size', 'timestamp']
    """
    df = df.copy()
    df.sort_values("timestamp", inplace=True)

    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    df["size"] = pd.to_numeric(df["size"], errors="coerce")

    # 🪄 Basic price + size indicators
    if "price" in df.columns:
        df["price_diff"] = df["price"].diff()

    if "size" in df.columns:
        df["size_cumsum"] = df["size"].cumsum()

    # 🪄 Trades per rolling window
    df["trade_count_window"] = df["price"].rolling(window=window).count()

    # 🪄 Volume (size) per rolling window
    df["volume_window"] = df["size"].rolling(window=window).sum()

    # 🪄 Rolling VWAP over window
    try:
        df["vwap_window"] = (
                (df["price"] * df["size"]).rolling(window=window).sum() /
                df["size"].rolling(window=window).sum()
        )
    except ZeroDivisionError:
        df["vwap_window"] = np.nan

    # 🪄 Tick Direction (uptick/downtick)
    df["tick_direction"] = np.sign(df["price_diff"]).replace({0: np.nan})
    df["tick_direction"] = df["tick_direction"].map({1.0: "uptick", -1.0: "downtick", np.nan: "neutral"})

    return df
