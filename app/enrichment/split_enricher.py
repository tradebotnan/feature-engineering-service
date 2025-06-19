# Source file: app/enrichment/split_enricher.py

from pathlib import Path

import pandas as pd
from common.io.parquet_utils import read_parquet_to_df
from common.logging.logger import setup_logger

logger = setup_logger()


def enrich_with_splits(df: pd.DataFrame, path: Path) -> pd.DataFrame:
    if not path.exists():
        logger.warning(f"⚠️ Splits file missing: {path}")
        # Add empty columns to the DataFrame
        empty_columns = ["is_split_day", "split_ratio"]
        for col in empty_columns:
            df[col] = None
        return df

    try:
        splits = read_parquet_to_df(path)
        splits["execution_date"] = pd.to_datetime(splits["execution_date"]).dt.date
        df["is_split_day"] = df["date"].isin(splits["execution_date"]).astype(int)

        df = df.merge(splits[["execution_date", "split_ratio"]], how="left", left_on="date", right_on="execution_date")
        df.drop(columns=["execution_date"], inplace=True)
        return df
    except Exception as e:
        logger.exception(f"❌ Failed to enrich splits from {path}: {e}")
        return df
