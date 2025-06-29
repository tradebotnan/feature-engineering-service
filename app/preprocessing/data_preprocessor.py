# Source file: app\preprocessing\data_preprocessor.py

import pandas as pd
from common.logging.logger import setup_logger

logger = setup_logger()


def preprocess_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    logger.info("🧹 Cleaning and preprocessing level...")

    if df.empty:
        logger.warning("⚠️ Received empty DataFrame to preprocess.")
        return df

    # Normalize column names
    df.columns = [col.lower().strip() for col in df.columns]

    # ✅ New (recommended) → force numeric types
    numeric_columns = ["open", "high", "low", "close", "volume"]
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Drop rows with missing essentials
    df = df.dropna(subset=[col for col in numeric_columns if col in df.columns])

    # Format timestamp
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"]).dt.tz_convert("America/New_York")
        df = df.sort_values("timestamp")

    logger.info("✅ Data cleaning completed.")
    return df
