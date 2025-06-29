# Source file: app\feature\labeler.py
import numpy as np
import pandas as pd
from common.logging.logger import setup_logger

logger = setup_logger()


def apply_labeling_strategy(df: pd.DataFrame, config: dict) -> pd.DataFrame:
    try:
        df = df.copy()
        labels = config.get("labels", {})

        if "trend" in labels:
            horizon = labels["trend"].get("horizon")
            df["trend"] = np.where(df["close"].shift(-horizon) > df["close"], 1, 0)

        if "future_return" in labels:
            horizon = labels["future_return"].get("horizon", 1)
            df["future_return"] = df["close"].shift(-horizon) / df["close"] - 1

        if "return_bin" in labels:
            bins = labels["return_bin"].get("bins")
            df["return_bin"] = pd.cut(df["future_return"], bins=bins, labels=False, include_lowest=True)

        # Inside apply_labeling_strategy
        required_columns = ["symbol", "timestamp"]
        if all(col in df.columns for col in ["open", "high", "low", "close", "volume"]):
            required_columns += ["open", "high", "low", "close", "volume"]
        elif all(col in df.columns for col in ["price", "size"]):
            required_columns += ["price", "size"]

        # ✅ Drop the rows and reset index
        df = df.dropna(subset=required_columns).reset_index(drop=True)

        logger.info(f"✅ Labels generated: {list(df.columns)}")
        return df

    except Exception as e:
        logger.error(f"❌ Labeling failed: {e}")
        logger.error("Traceback:", exc_info=True)
        return df
