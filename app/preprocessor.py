import pandas as pd
from app.utils.logger import get_logger

logger = get_logger(__name__)

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    logger.info("Cleaning and preprocessing data...")
    try:
        df = df.dropna()
        df = df.sort_values(by='timestamp')
        logger.info("Data cleaning completed successfully.")
    except Exception as e:
        logger.error(f"Error during data cleaning: {e}")
    return df
