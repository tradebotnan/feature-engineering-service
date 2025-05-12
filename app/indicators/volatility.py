# Source file: app\indicators\volatility.py
import pandas as pd
import ta


def add_atr(df: pd.DataFrame, periods: list) -> pd.DataFrame:
    for period in periods:
        atr = ta.volatility.AverageTrueRange(
            high=df["high"], low=df["low"], close=df["close"], window=period
        ).average_true_range()
        df[f"atr_{period}"] = atr
    return df


def add_bollinger_bands(df: pd.DataFrame, configs: list[dict]) -> pd.DataFrame:
    for config in configs:
        period = config.get("periods", 20)
        stddev = config.get("stddev", 2)
        bb = ta.volatility.BollingerBands(close=df["close"], window=period, window_dev=stddev)
        df[f"bollinger_h_{period}"] = bb.bollinger_hband()
        df[f"bollinger_l_{period}"] = bb.bollinger_lband()
    return df


def add_true_range_pct(df: pd.DataFrame, periods: list) -> pd.DataFrame:
    for period in periods:
        tr = df["high"] - df["low"]
        prev_close = df["close"].shift(1)
        true_range_pct = (tr / prev_close) * 100
        df[f"true_range_pct_{period}"] = true_range_pct.rolling(window=period).mean()
    return df


def add_volatility_burst(df: pd.DataFrame, zscore_window: int = 20) -> pd.DataFrame:
    df["rolling_std"] = df["close"].rolling(window=zscore_window).std()
    mean = df["rolling_std"].rolling(window=zscore_window).mean()
    std = df["rolling_std"].rolling(window=zscore_window).std()
    z = (df["rolling_std"] - mean) / std
    df["volatility_burst_z"] = z
    df.drop(columns=["rolling_std"], inplace=True)
    return df


import pandas as pd
from ta.volatility import AverageTrueRange, BollingerBands


def add_volatility_features(df: pd.DataFrame, config: dict) -> pd.DataFrame:
    df = df.copy()

    if "atr" in config:
        for period in config["atr"].get("periods", []):
            atr = AverageTrueRange(df["high"], df["low"], df["close"], window=period)
            df[f"atr_{period}"] = atr.average_true_range()

    if "bollinger" in config:
        for period in config["bollinger"].get("periods", []):
            bb = BollingerBands(close=df["close"], window=period, window_dev=2)
            df[f"bollinger_h_{period}"] = bb.bollinger_hband()
            df[f"bollinger_l_{period}"] = bb.bollinger_lband()

    if config.get("volatility", {}).get("enabled", False):
        df["volatility_5"] = df["close"].pct_change().rolling(window=5).std()

    if config.get("zscore", {}).get("enabled", False):
        df["zscore_close"] = (
                (df["close"] - df["close"].rolling(5).mean()) / df["close"].rolling(5).std()
        )

    return df
