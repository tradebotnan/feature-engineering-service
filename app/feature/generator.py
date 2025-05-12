import pandas as pd

# Core indicators
from app.indicators import (
    momentum, trend, volatility, volume,
    engineered, candles, options, sentiment
)

# Newly added stubs
from app.indicators import (
    crosses, sequence_id, time_features,
    event_flags, fundamentals, accumulation_distribution,
    chaikin_money_flow, ichimoku, donchian_channel
)

from common.logging.logger import setup_logger

logger = setup_logger()

# Try to load TA-Lib
try:
    import talib
    TALIB_AVAILABLE = True
    logger.info("✅ TA-Lib detected, optional TA-Lib support enabled.")
except ImportError:
    TALIB_AVAILABLE = False
    logger.info("ℹ️ TA-Lib not found, using default TA-Library (ta package).")


def generate_features(df: pd.DataFrame, config: dict) -> pd.DataFrame:
    """
    Master feature generation function.
    """
    try:
        df = df.copy()
        config = config.get('features', {})

        # =========================
        # Base Candlestick Features
        # =========================
        candle_cfg = config.get("candle_features", {})
        if candle_cfg.get("patterns", {}).get("enabled", False) or candle_cfg.get("engineered.py", {}).get("include"):
            df = candles.add_candlestick_features(df, candle_cfg)

        # ===================
        # Technical Indicators
        # ===================
        if "momentum_indicators" in config:
            df = momentum.add_momentum_features(df, config["momentum_indicators"])

        if "trend_indicators" in config:
            df = trend.add_trend_features(df, config["trend_indicators"])

        if "volatility_indicators" in config:
            df = volatility.add_volatility_features(df, config["volatility_indicators"])

        if "volume_indicators" in config:
            df = volume.add_volume_features(df, config["volume_indicators"])

        if "options_indicators" in config:
            df = options.add_options_features(df, config["options_indicators"])

        if "sentiment_indicators" in config:
            df = sentiment.add_sentiment_features(df, config["sentiment_indicators"])

        # ================
        # New placeholder modules (safely skip if configs not used yet)
        # ================
        if "cross_features" in config:
            df = crosses.add_cross_features(df, config["cross_features"])

        if config.get("sequence_id", {}).get("enabled", False):
            df = sequence_id.add_sequence_id(df)

        if "time_features" in config:
            df = time_features.add_time_features(df, config["time_features"])

        if "event_flags.py" in config:
            df = event_flags.add_event_flags(df, config["event_flags.py"])

        if "fundamentals.py" in config:
            df = fundamentals.add_fundamental_features(df, config["fundamentals.py"])

        if "accumulation_distribution" in config:
            df = accumulation_distribution.add_accumulation_distribution(df, config["accumulation_distribution"])

        if "chaikin_money_flow" in config:
            df = chaikin_money_flow.add_chaikin_money_flow(df, config["chaikin_money_flow"])

        if "ichimoku.py" in config:
            df = ichimoku.add_ichimoku_features(df, config["ichimoku.py"])

        if "donchian_channel" in config:
            df = donchian_channel.add_donchian_channel(df, config["donchian_channel"])

        # ================
        # Engineered Features
        # ================
        if "engineered_features" in config:
            df = engineered.add_engineered_features(df, config["engineered_features"])

        # Clean final dataframe
        df = df.dropna().reset_index(drop=True)
        logger.info(f"✅ Features generated: {list(df.columns)}")
        return df

    except Exception as e:
        logger.error(f"❌ Error generating features: {e}")
        return df
