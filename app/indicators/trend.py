# Source file: app/indicators/trend.py
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
    for period in config.get("trix", {}).get("periods", []):
        df[f"trix_{period}"] = calculate_trix(df["close"].ffill(), period)

    # =========================
    # Vortex
    # =========================
    for period in config.get("vortex", {}).get("periods", []):
        vortex = VortexIndicator(df["high"], df["low"], df["close"], window=period, fillna=True)
        df[f"vortex_pos_{period}"] = vortex.vortex_indicator_pos()
        df[f"vortex_neg_{period}"] = vortex.vortex_indicator_neg()

    # =========================
    # Donchian Channel
    # =========================
    for period in config.get("donchian_channel", {}).get("periods", []):
        df[f"donchian_high_{period}"] = df["high"].rolling(window=period).max()
        df[f"donchian_low_{period}"] = df["low"].rolling(window=period).min()

    # =========================
    # Ichimoku Cloud
    # =========================
    if config.get("ichimoku", {}).get("enabled", False):
        nine_high = df["high"].rolling(window=9).max()
        nine_low = df["low"].rolling(window=9).min()
        df["tenkan_sen"] = (nine_high + nine_low) / 2

        period26_high = df["high"].rolling(window=26).max()
        period26_low = df["low"].rolling(window=26).min()
        df["kijun_sen"] = (period26_high + period26_low) / 2

        df["senkou_span_a"] = ((df["tenkan_sen"] + df["kijun_sen"]) / 2).shift(26)

        period52_high = df["high"].rolling(window=52).max()
        period52_low = df["low"].rolling(window=52).min()
        df["senkou_span_b"] = ((period52_high + period52_low) / 2).shift(26)

        df["chikou_span"] = df["close"].shift(-26)

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
