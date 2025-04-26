import pandas as pd
from app.utils.logger import get_logger

logger = get_logger(__name__)

def label_trend(df: pd.DataFrame) -> pd.DataFrame:
    logger.info("Labeling trends...")
    try:
        df['trend_label'] = (df['close'].shift(-1) > df['close']).astype(int)
        logger.info("Trend labeling completed successfully.")
    except Exception as e:
        logger.error(f"Error during trend labeling: {e}")
    return df
