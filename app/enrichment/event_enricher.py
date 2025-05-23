# Source file: app/enrichment/event_enricher.py

from pathlib import Path

import pandas as pd
from common.io.parquet_utils import read_parquet_to_df
from common.logging.logger import setup_logger

from app.enrichment.enrichment_utils import calculate_days_since

logger = setup_logger()


def enrich_with_events(df: pd.DataFrame, path: Path) -> pd.DataFrame:
    if not path.exists():
        logger.warning(f"⚠️ Events file missing: {path}")
        return df

    try:
        events = read_parquet_to_df(path)
        events["event_date"] = pd.to_datetime(events["date"]).dt.date

        df["has_event"] = df["date"].isin(events["event_date"]).astype(int)
        df["has_ticker_change"] = df["date"].isin(events.query("type == 'ticker_change'")["event_date"]).astype(int)
        df["has_merger_or_acquisition"] = df["date"].isin(
            events.query("type in ['merger', 'acquisition']")["event_date"]).astype(int)
        df["has_name_change"] = df["date"].isin(events.query("type == 'name_change'")["event_date"]).astype(int)

        df["days_since_last_event"] = calculate_days_since(df["date"], df["has_event"])
        return df
    except Exception as e:
        logger.exception(f"❌ Failed to enrich events from {path}: {e}")
        return df
