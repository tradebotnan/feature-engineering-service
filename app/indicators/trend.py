import pandas as pd
from ta.trend import EMAIndicator, SMAIndicator, MACD, TRIXIndicator, VortexIndicator

def add_trend_features(df: pd.DataFrame, config: dict) -> pd.DataFrame:
    """
    Adds trend indicators like EMA, SMA, MACD, TRIX, Vortex.
    Expected config format:
    {
        "ema": {"periods": [5, 20]},
        "sma": {"periods": [10]},
        "macd": {"enabled": True},
        "trix": {"periods": [5]},
        "vortex": {"periods": [5]}
    }
    """
    if "ema" in config:
        for period in config["ema"].get("periods", []):
            df[f"ema_{period}"] = EMAIndicator(close=df["close"], window=period).ema_indicator()

    if "sma" in config:
        for period in config["sma"].get("periods", []):
            df[f"sma_{period}"] = SMAIndicator(close=df["close"], window=period).sma_indicator()

    if "macd" in config and config["macd"].get("enabled", False):
        macd = MACD(df["close"].fillna(method="ffill"))
        df["macd"] = macd.macd().fillna(0)
        df["macd_signal"] = macd.macd_signal().fillna(0)

    if "trix" in config:
        for period in config["trix"].get("periods", []):
            df[f"trix_{period}"] = TRIXIndicator(close=df["close"], window=period).trix()

    if "vortex" in config:
        for period in config["vortex"].get("periods", []):
            vortex = VortexIndicator(high=df["high"], low=df["low"], close=df["close"], window=period)
            df[f"vortex_pos_{period}"] = vortex.vortex_indicator_pos()
            df[f"vortex_neg_{period}"] = vortex.vortex_indicator_neg()

    return df
