# Source file: app/enrichment/news_enricher.py

from pathlib import Path
import pandas as pd
from common.io.parquet_utils import read_parquet_to_df
from common.env.env_loader import get_env_variable
from common.logging.logger import setup_logger

logger = setup_logger()

def enrich_with_news(df: pd.DataFrame, symbol: str, year: int, market: str = "us", asset: str = "stocks", include_columns: list = None) -> pd.DataFrame:
    try:
        base_dir = Path(get_env_variable("BASE_DIR"))
        external_dir = get_env_variable("EXTERNAL_DIR")
        news_dir = get_env_variable("NEWS_DIR")
        processed_dir = get_env_variable("PROCESSED_DIR")
        gdlet_dir = get_env_variable("GDLET_DIR")
        file_path = base_dir / external_dir / news_dir / processed_dir / gdlet_dir / market / asset / symbol / str(year) / f"{symbol}_sentiment_{year}.parquet"

        if not file_path.exists():
            logger.warning(f"⚠️ News sentiment file not found for {symbol} {year}: {file_path}")
            # Add empty columns to the DataFrame
            empty_columns = [
                "sentiment_avg",
                "sentiment_count",
                "sentiment_std",
                "sentiment_3d_avg",
                "sentiment_5d_avg",
                "sentiment_3d_momentum",
                "buzz_score_5d",
                "sentiment_trend_up",
            ]
            for col in empty_columns:
                df[col] = None
            return df

        sentiment_df = read_parquet_to_df(file_path)
        sentiment_df["date"] = pd.to_datetime(sentiment_df["date"]).dt.date
        df["date"] = pd.to_datetime(df["date"]).dt.date

        # Explicit list of sentiment columns to keep
        selected_columns = [
            "sentiment_avg",
            "sentiment_count",
            "sentiment_std",
            "sentiment_3d_avg",
            "sentiment_5d_avg",
            "sentiment_3d_momentum",
            "buzz_score_5d",
            "sentiment_trend_up",
        ]
        sentiment_df = sentiment_df[["date"] + selected_columns]

        enriched_df = df.merge(sentiment_df, on="date", how="left")
        logger.info(f"✅ News sentiment enrichment applied for {symbol} {year}")
        return enriched_df

    except Exception as e:
        logger.exception(f"❌ Failed to enrich with news sentiment for {symbol} {year}: {e}")
        return df
