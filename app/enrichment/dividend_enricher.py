# Source file: app/enrichment/dividend_enricher.py

from pathlib import Path

import pandas as pd
from common.io.parquet_utils import read_parquet_to_df
from common.logging.logger import setup_logger

from app.enrichment.enrichment_utils import calculate_days_since, calculate_days_until

logger = setup_logger()


def enrich_with_dividends(df: pd.DataFrame, path: Path) -> pd.DataFrame:
    if not path.exists():
        logger.warning(f"⚠️ Dividend file missing: {path}")
        empty_columns = [
            "is_dividend_day",
            "dividend_amount",
            "days_since_last_dividend",
            "next_dividend_in_X_days",
        ]
        for col in empty_columns:
            df[col] = None
        return df

    try:
        dividends = read_parquet_to_df(path)
        dividends["ex_date"] = pd.to_datetime(dividends["ex_dividend_date"]).dt.date
        df["is_dividend_day"] = df["date"].isin(dividends["ex_date"]).astype(int)

        df = df.merge(dividends[["ex_date", "cash_amount"]], how="left", left_on="date", right_on="ex_date")
        df.rename(columns={"cash_amount": "dividend_amount"}, inplace=True)
        df.drop(columns=["ex_date"], inplace=True)

        df["days_since_last_dividend"] = calculate_days_since(df["date"], df["is_dividend_day"])
        df["next_dividend_in_X_days"] = calculate_days_until(df["date"], dividends["ex_date"].unique())

        logger.info(f"✅ Dividend enrichment applied for {path.stem}")
        return df
    except Exception as e:
        logger.exception(f"❌ Failed to enrich dividends from {path.stem}: {e}")
        return df
