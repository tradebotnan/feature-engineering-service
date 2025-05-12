# Source file: app/indicators/volume.py
import pandas as pd
from ta.volume import (
    OnBalanceVolumeIndicator,
    MFIIndicator,
    AccDistIndexIndicator,
    ChaikinMoneyFlowIndicator
)


def add_volume_features(df: pd.DataFrame, config: dict) -> pd.DataFrame:
    df = df.copy()

    # =========================
    # OBV
    # =========================
    if config.get("obv", {}).get("enabled", False):
        obv = OnBalanceVolumeIndicator(close=df["close"], volume=df["volume"])
        df["obv"] = obv.on_balance_volume()

    # =========================
    # MFI
    # =========================
    if "mfi" in config:
        for period in config["mfi"].get("periods", []):
            mfi = MFIIndicator(
                high=df["high"], low=df["low"],
                close=df["close"], volume=df["volume"], window=period
            )
            df[f"mfi_{period}"] = mfi.money_flow_index()

    # =========================
    # Accumulation / Distribution Index
    # =========================
    if config.get("accumulation_distribution", {}).get("enabled", False):
        adi = AccDistIndexIndicator(
            high=df["high"], low=df["low"], close=df["close"], volume=df["volume"]
        )
        df["accum_dist"] = adi.acc_dist_index()

    # =========================
    # Chaikin Money Flow
    # =========================
    if "chaikin_money_flow" in config:
        for period in config["chaikin_money_flow"].get("periods", []):
            cmf = ChaikinMoneyFlowIndicator(
                high=df["high"], low=df["low"],
                close=df["close"], volume=df["volume"], window=period
            )
            df[f"cmf_{period}"] = cmf.chaikin_money_flow()

    # =========================
    # Volume ROC
    # =========================
    if "volume_roc" in config:
        for period in config["volume_roc"].get("periods", []):
            df[f"volume_roc_{period}"] = df["volume"].pct_change(periods=period)

    # =========================
    # VWAP + Price VWAP Ratio
    # =========================
    if config.get("vwap", {}).get("enabled", False):
        price = (df["high"] + df["low"] + df["close"]) / 3
        vwap = (price * df["volume"]).cumsum() / df["volume"].cumsum()
        df["vwap"] = vwap

    if config.get("price_vwap_ratio", {}).get("enabled", False):
        if "vwap" not in df.columns:
            price = (df["high"] + df["low"] + df["close"]) / 3
            vwap = (price * df["volume"]).cumsum() / df["volume"].cumsum()
            df["vwap"] = vwap
        df["price_vwap_ratio"] = df["close"] / df["vwap"]

    return df
