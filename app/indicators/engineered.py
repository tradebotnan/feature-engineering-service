import pandas as pd
import numpy as np


def add_returns(df: pd.DataFrame, include: list):
    if "return_1d" in include:
        df["return_1d"] = df["close"].pct_change()
    if "return_5d" in include:
        df["return_5d"] = df["close"].pct_change(5)
    if "log_return" in include:
        df["log_return"] = np.log(df["close"] / df["close"].shift(1))
    return df


def add_volatility(df: pd.DataFrame, windows: list):
    for window in windows:
        df[f"volatility_{window}"] = df["close"].rolling(window=window).std()
    return df


def add_trend_strength(df: pd.DataFrame, periods: list):
    for period in periods:
        df[f"trend_strength_{period}"] = (df["close"] - df["close"].rolling(period).mean()) / df["close"].rolling(period).std()
    return df


def add_zscore(df: pd.DataFrame, apply_to: list, window: int = 20):
    for column in apply_to:
        if column in df.columns:
            rolling_mean = df[column].rolling(window).mean()
            rolling_std = df[column].rolling(window).std()
            df[f"zscore_{column}"] = (df[column] - rolling_mean) / rolling_std
    return df

def add_engineered_features(df: pd.DataFrame, config: dict) -> pd.DataFrame:
    df = df.copy()

    if "return" in config:
        returns = config["return"].get("include", [])
        if "return_1d" in returns:
            df["return_1d"] = df["close"].pct_change(periods=1)
        if "return_5d" in returns:
            df["return_5d"] = df["close"].pct_change(periods=5)
        if "log_return" in returns:
            df["log_return"] = (df["close"] / df["close"].shift(1)).apply(
                lambda x: np.nan if x <= 0 else np.log(x)
            )

    return df
