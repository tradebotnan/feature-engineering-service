# app/feature/generator.py
import os

import pandas as pd
from common.logging.logger import setup_logger

# Newly added stubs
from app.indicators import (
    crosses, sequence_id, time_features,
    accumulation_distribution,
    chaikin_money_flow, ichimoku, donchian_channel
)
# Core indicators
from app.indicators import (
    momentum, trend, volatility, volume,
    engineered, candles, options
)
# ✅ NEW trades module
from app.indicators import trade_indicators

logger = setup_logger()

# Try to load TA-Lib
try:
    import talib

    TALIB_AVAILABLE = True
    logger.info("✅ TA-Lib detected, optional TA-Lib support enabled.")
except ImportError:
    TALIB_AVAILABLE = False
    logger.info("ℹ️ TA-Lib not found, using default TA-Library (ta package).")


def generate_features(df: pd.DataFrame, config: dict, level: str) -> pd.DataFrame:
    """
    Master feature generation pipeline for feature-engineering-service.
    """
    try:
        df = df.copy()
        features_config = config.get('features', {})

        # =====================
        # ✅ Special case: Trades dataset
        # =====================
        if level == "trades":
            trades_cfg = features_config.get("trades", {}).get("indicators", {})
            if trades_cfg.get("enabled", False):
                features_list = trades_cfg.get("features", [])
                df = trade_indicators.add_all_trade_indicators(df, features=features_list)
                logger.info("✅ Trades indicators applied.")
            else:
                logger.info("ℹ️ Trades indicators disabled by config.")
            return df

        # =====================
        # ✅ Candlestick + engineered bars dataset
        # =====================
        candle_cfg = features_config.get("candle_features", {})
        if candle_cfg.get("patterns", {}).get("enabled", False) or candle_cfg.get("engineered", {}).get("include"):
            df = candles.add_candlestick_features(df, candle_cfg)

        if "momentum_indicators" in features_config:
            df = momentum.add_momentum_features(df, features_config["momentum_indicators"])

        if "trend_indicators" in features_config:
            df = trend.add_trend_features(df, features_config["trend_indicators"])

        if "volatility_indicators" in features_config:
            df = volatility.add_volatility_features(df, features_config["volatility_indicators"])

        if "volume_indicators" in features_config:
            df = volume.add_volume_features(df, features_config["volume_indicators"])

        if "options_indicators" in features_config:
            df = options.add_options_features(df, features_config["options_indicators"])

        if "cross_features" in features_config:
            df = crosses.add_cross_features(df, features_config["cross_features"])

        if features_config.get("sequence_id", {}).get("enabled", False):
            df = sequence_id.add_sequence_id(df)

        if "time_features" in features_config:
            df = time_features.add_time_features(df, features_config["time_features"])

        if "accumulation_distribution" in features_config:
            df = accumulation_distribution.add_accumulation_distribution(df,
                                                                         features_config["accumulation_distribution"])

        if "chaikin_money_flow" in features_config:
            df = chaikin_money_flow.add_chaikin_money_flow(df, features_config["chaikin_money_flow"])

        if "ichimoku" in features_config and level == "day":
            df = ichimoku.add_ichimoku_features(df, features_config["ichimoku"])

        if "donchian_channel" in features_config:
            df = donchian_channel.add_donchian_channel(df, features_config["donchian_channel"])

        # =====================
        # ✅ Final engineered features
        # =====================
        if "engineered_features" in features_config:
            df = engineered.add_engineered_features(df, features_config["engineered_features"])

        required_columns = ["symbol", "open", "high", "low", "close", "volume", "timestamp"]
        rows_with_nan = df[df[required_columns].isnull().any(axis=1)]

        # ✅ Log and save them if any exist
        if not rows_with_nan.empty:
            logger.warning(f"🚨 {len(rows_with_nan)} rows will be dropped due to NaNs.")

            # Save to CSV for inspection
            output_dir = "D:/level/debug_nan_records"
            os.makedirs(output_dir, exist_ok=True)
            output_file = os.path.join(output_dir, f"dropped_nan_rows_{level}.csv")
            rows_with_nan.to_csv(output_file, index=False)
            logger.info(f"📝 Dropped rows saved to: {output_file}")

            # Also log individual rows for traceability
            for idx, row in rows_with_nan.iterrows():
                logger.debug(f"Dropping row index {idx}: {row.to_dict()}")

        # ✅ Drop the rows and reset index
        df = df.dropna(subset=required_columns).reset_index(drop=True)

        logger.info(f"✅ Features generated: {list(df.columns)}")
        return df

    except Exception as e:
        logger.error(f"❌ Error generating features: {e}")
        logger.error("Traceback:", exc_info=True)
        return df
