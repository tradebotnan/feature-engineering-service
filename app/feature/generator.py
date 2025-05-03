import pandas as pd
import numpy as np

from app.indicators import momentum, trend, volatility, volume, engineered, candles, options, sentiment
from app.indicators.candles import add_pattern_features
from app.utils.logger import get_logger

logger = get_logger("feature_generator")

def add_pattern_features(df: pd.DataFrame, patterns: list) -> pd.DataFrame:
    df = df.copy()

    if "doji" in patterns:
        df["pattern_doji"] = np.where(
            np.abs(df["open"] - df["close"]) <= 0.1 * (df["high"] - df["low"]), 1, 0
        )

    if "engulfing" in patterns:
        df["pattern_engulfing"] = 0
        prev_open = df["open"].shift(1)
        prev_close = df["close"].shift(1)

        bullish = (prev_close < prev_open) & (df["close"] > df["open"]) & (df["close"] > prev_open) & (df["open"] < prev_close)
        bearish = (prev_close > prev_open) & (df["close"] < df["open"]) & (df["open"] > prev_close) & (df["close"] < prev_open)

        df.loc[bullish | bearish, "pattern_engulfing"] = 1

    return df

def generate_features(df: pd.DataFrame, config: dict) -> pd.DataFrame:
    try:
        df = df.copy()

        # Candlestick patterns
        patterns_cfg = config.get("candle_features", {}).get("patterns", {})
        if patterns_cfg.get("enabled", False):
            pattern_list = patterns_cfg.get("include", [])
            df = add_pattern_features(df, pattern_list)

        # Technical indicators
        if "momentum_indicators" in config:
            df = momentum.add_momentum_features(df, config["momentum_indicators"])

        if "trend_indicators" in config:
            df = trend.add_trend_features(df, config["trend_indicators"])

        if "volatility_indicators" in config:
            df = volatility.add_volatility_features(df, config["volatility_indicators"])

        if "volume_indicators" in config:
            df = volume.add_volume_features(df, config["volume_indicators"])

        if "engineered_features" in config:
            df = engineered.add_engineered_features(df, config["engineered_features"])

        # Other optional domains
        if "candlestick_patterns" in config and config["candlestick_patterns"].get("enabled", False):
            df = candles.add_candlestick_features(df, config["candlestick_patterns"])

        if "options_indicators" in config and config["options_indicators"].get("enabled", False):
            df = options.add_options_features(df, config["options_indicators"])

        if "sentiment_indicators" in config and config["sentiment_indicators"].get("enabled", False):
            df = sentiment.add_sentiment_features(df, config["sentiment_indicators"])

        df = df.dropna().reset_index(drop=True)
        logger.info(f"✅ Features generated: {list(df.columns)}")
        return df

    except Exception as e:
        logger.error(f"❌ Error generating features: {e}")
        return df
