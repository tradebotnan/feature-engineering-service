# Source file: app\indicators\volume.py
import numpy as np
import pandas as pd
from ta.volume import OnBalanceVolumeIndicator, MFIIndicator


def compute_vwap(df: pd.DataFrame) -> pd.Series:
    return (df['close'] * df['volume']).cumsum() / df['volume'].cumsum()


def compute_price_vwap_ratio(df: pd.DataFrame) -> pd.Series:
    vwap = compute_vwap(df)
    return df['close'] / vwap


def compute_volume_ema(df: pd.DataFrame, period: int) -> pd.Series:
    return df['volume'].ewm(span=period, adjust=False).mean()


def compute_volume_roc(df: pd.DataFrame, period: int) -> pd.Series:
    return df['volume'].pct_change(periods=period)


def detect_volume_anomalies(df: pd.DataFrame, threshold: float = 2.0) -> pd.Series:
    mean = df['volume'].rolling(window=20).mean()
    std = df['volume'].rolling(window=20).std()
    zscore = (df['volume'] - mean) / std
    return pd.Series(np.where(np.abs(zscore) > threshold, 1, 0), index=zscore.index)


def add_vwap(df: pd.DataFrame) -> pd.DataFrame:
    price = (df["high"] + df["low"] + df["close"]) / 3
    vwap = (price * df["volume"]).cumsum() / df["volume"].cumsum()
    df["vwap"] = vwap
    return df


def add_price_vwap_ratio(df: pd.DataFrame) -> pd.DataFrame:
    if "vwap" not in df.columns:
        df = add_vwap(df)
    df["price_vwap_ratio"] = df["close"] / df["vwap"]
    return df


def add_volume_ema(df: pd.DataFrame, period: int) -> pd.DataFrame:
    df[f"volume_ema_{period}"] = df["volume"].ewm(span=period, adjust=False).mean()
    return df


def add_volume_roc(df: pd.DataFrame, period: int) -> pd.DataFrame:
    df[f"volume_roc_{period}"] = df["volume"].pct_change(periods=period)
    return df


def add_volume_features(df: pd.DataFrame, config: dict) -> pd.DataFrame:
    """
    Adds volume indicators like OBV, MFI, VWAP ratio, volume EMA/ROC.
    Expected config format:
    {
        "obv": {"enabled": True},
        "mfi": {"periods": [14]},
        "volume_ema": {"periods": [5]},
        "volume_roc": {"periods": [5]},
        "price_vwap_ratio": {"enabled": True}
    }
    """
    if "obv" in config and config["obv"].get("enabled", False):
        df["obv"] = OnBalanceVolumeIndicator(close=df["close"], volume=df["volume"]).on_balance_volume()

    if "mfi" in config:
        for period in config["mfi"].get("periods", []):
            df[f"mfi_{period}"] = MFIIndicator(
                high=df["high"], low=df["low"], close=df["close"], volume=df["volume"], window=period
            ).money_flow_index()

    if "volume_ema" in config:
        for period in config["volume_ema"].get("periods", []):
            df[f"volume_ema_{period}"] = df["volume"].ewm(span=period, adjust=False).mean()

    if "volume_roc" in config:
        for period in config["volume_roc"].get("periods", []):
            df[f"volume_roc_{period}"] = df["volume"].pct_change(periods=period)

    if "price_vwap_ratio" in config and config["price_vwap_ratio"].get("enabled", False):
        typical_price = (df["high"] + df["low"] + df["close"]) / 3
        vwap = (typical_price * df["volume"]).cumsum() / df["volume"].cumsum()
        df["vwap"] = vwap
        df["price_vwap_ratio"] = df["close"] / vwap

    return df
