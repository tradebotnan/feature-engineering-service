import pandas as pd
import talib
from app.utils.logger import get_logger

logger = get_logger(__name__)

def generate_features(df: pd.DataFrame) -> pd.DataFrame:
    logger.info("Generating technical indicators...")
    try:
        df['rsi_14'] = talib.RSI(df['close'], timeperiod=14)
        df['ema_10'] = talib.EMA(df['close'], timeperiod=10)
        df['ema_50'] = talib.EMA(df['close'], timeperiod=50)
        df['macd'], df['macd_signal'], df['macd_hist'] = talib.MACD(df['close'])
        logger.info("Feature generation completed successfully.")
    except Exception as e:
        logger.error(f"Error generating features: {e}")
    return df
