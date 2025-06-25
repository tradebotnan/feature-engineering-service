# Source file: app/indicators/momentum.py
import pandas as pd
from ta.momentum import (
    RSIIndicator,
    ROCIndicator,
    StochasticOscillator

)

from ta.trend import (
    ADXIndicator,
    CCIIndicator
)


def add_momentum_features(df: pd.DataFrame, config: dict) -> pd.DataFrame:
    df = df.copy()

    # =========================
    # RSI
    # =========================
    if "rsi" in config:
        for period in config["rsi"].get("periods", []):
            rsi = RSIIndicator(close=df["close"], window=period)
            df[f"rsi_{period}"] = rsi.rsi()

    # =========================
    # ROC
    # =========================
    if "roc" in config:
        for period in config["roc"].get("periods", []):
            roc = ROCIndicator(close=df["close"], window=period)
            df[f"roc_{period}"] = roc.roc()

    # =========================
    # ADX
    # =========================
    if "adx" in config:
        for period in config["adx"].get("periods", []):
            adx = ADXIndicator(
                high=df["high"], low=df["low"], close=df["close"], window=period
            )
            df[f"adx_{period}"] = adx.adx()

    # =========================
    # CCI
    # =========================
    if "cci" in config:
        for period in config["cci"].get("periods", []):
            cci = CCIIndicator(
                high=df["high"], low=df["low"], close=df["close"], window=period
            )
            df[f"cci_{period}"] = cci.cci()

    # =========================
    # Stochastic Oscillator
    # =========================
    if "stochastic" in config:
        for period in config["stochastic"].get("periods", []):
            so = StochasticOscillator(
                high=df["high"], low=df["low"], close=df["close"], window=period
            )
            df[f"stoch_k_{period}"] = so.stoch()
            df[f"stoch_d_{period}"] = so.stoch_signal()

    return df
