# Source file: app/enrichment/generate_enrichment_overlay.py

from pathlib import Path

import pandas as pd
from common.env.env_loader import get_env_variable
from common.logging.logger import setup_logger

from app.enrichment.dividend_enricher import enrich_with_dividends
from app.enrichment.event_enricher import enrich_with_events
from app.enrichment.fundamentals_enricher import enrich_with_fundamentals
from app.enrichment.split_enricher import enrich_with_splits

logger = setup_logger()


def generate_enrichment_overlay(df: pd.DataFrame, market, asset, symbol: str) -> pd.DataFrame:
    try:
        preserved_attrs = df.attrs.copy()
        base_dir = Path(get_env_variable("BASE_DIR")) / get_env_variable("ENRICHMENT_DIR")

        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")
        df["date"] = df["timestamp"].dt.date

        df = enrich_with_dividends(df, base_dir / "dividends" / market / asset / symbol / f"{symbol}_dividends.parquet")
        df = enrich_with_splits(df, base_dir / "splits" / market / asset / symbol / f"{symbol}_splits.parquet")
        df = enrich_with_events(df, base_dir / "events" / market / asset / symbol / f"{symbol}_events.parquet")
        df = enrich_with_fundamentals(df,
                                      base_dir / "financials" / market / asset / symbol / f"{symbol}_financials.parquet")

        df.attrs.update(preserved_attrs)
        return df

    except Exception as e:
        logger.error(f"❌ Enrichment failed for {symbol}: {e}", exc_info=True)
        raise
