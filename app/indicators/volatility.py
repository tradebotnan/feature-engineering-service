# Source file: app/indicators/volatility.py
import pandas as pd
import numpy as np
from ta.volatility import AverageTrueRange, BollingerBands

def add_volatility_features(df: pd.DataFrame, config: dict) -> pd.DataFrame:
    df = df.copy()

    # =========================
    # ATR
    # =========================
    if "atr" in config:
        for period in config["atr"].get("periods", []):
            atr = AverageTrueRange(df["high"], df["low"], df["close"], window=period)
            df[f"atr_{period}"] = atr.average_true_range()

    # =========================
    # Bollinger Bands
    # =========================
    if "bollinger" in config:
        period = config["bollinger"].get("periods", [20])[0]
        stddev = config["bollinger"].get("stddev", 2)
        bb = BollingerBands(close=df["close"], window=period, window_dev=stddev)
        df[f"bollinger_h_{period}"] = bb.bollinger_hband()
        df[f"bollinger_l_{period}"] = bb.bollinger_lband()

    # =========================
    # True Range Percentage
    # =========================
    if "true_range_pct" in config:
        for period in config["true_range_pct"].get("periods", []):
            tr = df["high"] - df["low"]
            prev_close = df["close"].shift(1)
            true_range_pct = (tr / prev_close) * 100
            df[f"true_range_pct_{period}"] = true_range_pct.rolling(window=period).mean()

    # =========================
    # Engineered volatility
    # =========================
    vol_cols = []
    if config.get("volatility", {}).get("windows", []):
        for window in config["volatility"]["windows"]:
            col = f"volatility_{window}"
            df[col] = df["close"].pct_change().rolling(window=window).std()
            vol_cols.append(col)

    # =========================
    # Volatility Score (mean of all vol windows)
    # =========================
    if vol_cols:
        df["volatility_score"] = df[vol_cols].mean(axis=1).fillna(0.0)

    # =========================
    # Z-Score
    # =========================
    if config.get("zscore", {}).get("apply_to", []):
        for column in config["zscore"]["apply_to"]:
            if column in df.columns:
                rolling_mean = df[column].rolling(20).mean()
                rolling_std = df[column].rolling(20).std()
                df[f"zscore_{column}"] = (df[column] - rolling_mean) / rolling_std

    return df