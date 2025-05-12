# Source file: app\indicators\trend.py
import pandas as pd
from ta.trend import SMAIndicator, EMAIndicator, WMAIndicator, MACD, VortexIndicator


def add_trend_features(df: pd.DataFrame, config: dict) -> pd.DataFrame:
    df = df.copy()

    # =========================
    # Moving Averages
    # =========================
    for period in config.get("sma", {}).get("periods", []):
        df[f"sma_{period}"] = SMAIndicator(df["close"], window=period, fillna=True).sma_indicator()

    for period in config.get("ema", {}).get("periods", []):
        df[f"ema_{period}"] = EMAIndicator(df["close"], window=period, fillna=True).ema_indicator()

    for period in config.get("wma", {}).get("periods", []):
        df[f"wma_{period}"] = WMAIndicator(df["close"], window=period, fillna=True).wma()

    # =========================
    # MACD
    # =========================
    if config.get("macd", {}).get("enabled", False):
        macd = MACD(df["close"].ffill())
        df["macd"] = macd.macd()
        df["macd_signal"] = macd.macd_signal()

    # =========================
    # TRIX
    # =========================
    # TRIX
    for period in config.get("trix", {}).get("periods", []):
        df[f"trix_{period}"] = calculate_trix(df["close"].ffill(), period)

    # =========================
    # Vortex
    # =========================
    for period in config.get("vortex", {}).get("periods", []):
        vortex = VortexIndicator(df["high"], df["low"], df["close"], window=period, fillna=True)
        df[f"vortex_pos_{period}"] = vortex.vortex_indicator_pos()
        df[f"vortex_neg_{period}"] = vortex.vortex_indicator_neg()

    return df


def calculate_trix(series: pd.Series, period: int) -> pd.Series:
    """
    Calculate TRIX (Triple Exponential Average).
    """
    ema1 = series.ewm(span=period, adjust=False).mean()
    ema2 = ema1.ewm(span=period, adjust=False).mean()
    ema3 = ema2.ewm(span=period, adjust=False).mean()
    trix = 100 * (ema3.diff() / ema3.shift(1))
    return trix
