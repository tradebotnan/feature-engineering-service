# Source file: app/enrichment/trades_enricher.py

import pandas as pd
from pathlib import Path

from common.logging.logger import setup_logger
from common.env.env_loader import get_env_variable

from app.enrichment.news_enricher import enrich_with_news
from app.enrichment.microstructure_enricher import enrich_with_microstructure
from app.enrichment.trade_side_inference import infer_trade_side
from app.indicators.trade_indicators import add_all_trade_indicators

logger = setup_logger()


def enrich_trades(df: pd.DataFrame, market: str, asset: str, symbol: str) -> pd.DataFrame:
    """
    Enrich tick-level trades with:
    - News sentiment (timestamp-aligned)
    - Microstructure features (tick_direction, price_diff, vwap_Xs)
    - Trade side inference (buy/sell)
    - Trade indicators (imbalance, micro_price, volume rates, etc.)
    """
    try:
        df = df.copy()
        preserved_attrs = df.attrs.copy()

        if df.empty or "timestamp" not in df.columns:
            logger.warning(f"⚠️ Skipping enrichment for {symbol} trades: missing timestamp or empty frame.")
            # Add empty columns
            empty_columns = [
                "tick_direction",
                "price_diff",
                "vwap_1s",
                "vwap_5s",
                "vwap_10s",
                "micro_price",
                "tick_imbalance",
                "trade_count_per_second",
                "volume_per_second",
            ]
            for col in empty_columns:
                df[col] = None
            return df

        # Step 1: Ensure timestamp is timezone-aware UTC
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")
        df = df.dropna(subset=["timestamp"])

        # Step 2: Convert to NYSE time for trading-day alignment
        df["timestamp"] = df["timestamp"].dt.tz_convert("America/New_York")

        # Step 3: Extract normalized NYSE date (timezone-naive)
        df["date"] = df["timestamp"].dt.normalize().dt.tz_localize(None)

        year = df["timestamp"].dt.year.min()

        # ✅ Timestamp-level news enrichment
        if year:
            df = enrich_with_news(df, symbol=symbol, year=year, market=market, asset=asset)

        # ✅ Add microstructure features (tick_direction, price_diff, VWAP)
        df = enrich_with_microstructure(df)

        # ✅ Add trade side inference (buy/sell)
        df = infer_trade_side(df)

        # ✅ Add additional rolling trade indicators
        trade_features = [
            "micro_price",
            "tick_imbalance",
            "trade_count_per_second",
            "volume_per_second",
        ]
        df = add_all_trade_indicators(df, features=trade_features)

        df.attrs.update(preserved_attrs)
        logger.info(f"✅ Trades enrichment completed for {symbol} ({len(df)} rows)")
        return df

    except Exception as e:
        logger.error(f"❌ Failed to enrich trades for {symbol}: {e}", exc_info=True)
        return df