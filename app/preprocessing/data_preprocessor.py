import pandas as pd
from app.utils.logger import get_logger

logger = get_logger("preprocessor")


def preprocess_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    logger.info("🧹 Cleaning and preprocessing data...")

    if df.empty:
        logger.warning("⚠️ Received empty DataFrame to preprocess.")
        return df

    # Normalize column names
    df.columns = [col.lower().strip() for col in df.columns]

    # Drop rows with missing essentials
    required_cols = ["close", "open", "high", "low", "volume"]
    df = df.dropna(subset=[col for col in required_cols if col in df.columns])

    # Format timestamp
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
        df = df.sort_values("timestamp")

    logger.info("✅ Data cleaning completed.")
    return df
