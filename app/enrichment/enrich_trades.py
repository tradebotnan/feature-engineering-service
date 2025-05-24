# Source file: app/enrichment/trades_enricher.py

import pandas as pd
from pathlib import Path
from common.logging.logger import setup_logger
from common.env.env_loader import get_env_variable
from app.enrichment.news_enricher import enrich_with_news


logger = setup_logger()

def enrich_trades(df: pd.DataFrame, market: str, asset: str, symbol: str) -> pd.DataFrame:
    """
    Enrich tick-level trades data with timestamp-aligned sentiment from news and optionally other overlays.
    """
    try:
        df = df.copy()
        preserved_attrs = df.attrs.copy()

        if df.empty or "timestamp" not in df.columns:
            logger.warning(f"⚠️ Skipping enrichment for {symbol} trades: missing timestamp or empty frame.")
            return df

        # Step 1: Ensure timestamp is timezone-aware UTC
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")
        df = df.dropna(subset=["timestamp"])

        # Step 2: Convert to NYSE time for trading-day alignment
        df["timestamp"] = df["timestamp"].dt.tz_convert("America/New_York")

        # Step 3: Extract normalized NYSE date (timezone-naive)
        df["date"] = df["timestamp"].dt.normalize().dt.tz_localize(None)

        year = df["timestamp"].dt.year.min()

        # ✅ Enrich with timestamp-level news sentiment
        if year:
            df = enrich_with_news(df, symbol=symbol, year=year, market=market, asset=asset)

        # 🛑 SKIP: fundamentals, dividends, splits, events (not relevant for trades-level granularity)

        df.attrs.update(preserved_attrs)
        logger.info(f"✅ Trades enrichment completed for {symbol} ({len(df)} rows)")
        return df

    except Exception as e:
        logger.error(f"❌ Failed to enrich trades for {symbol}: {e}", exc_info=True)
        return df
