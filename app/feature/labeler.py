import pandas as pd
import numpy as np
from app.utils.logger import get_logger

logger = get_logger("feature_labeler")

def apply_labeling_strategy(df: pd.DataFrame, config: dict) -> pd.DataFrame:
    try:
        df = df.copy()
        labels = config.get("labels", {})

        if "trend" in labels:
            horizon = labels["trend"].get("horizon", 1)
            df["trend"] = np.where(df["close"].shift(-horizon) > df["close"], 1, 0)

        if "future_return" in labels:
            horizon = labels["future_return"].get("horizon", 1)
            df["future_return"] = df["close"].shift(-horizon) / df["close"] - 1

        if "return_bin" in labels:
            bins = labels["return_bin"].get("bins", [-1.0, 0.0, 0.5, 1.0])
            df["return_bin"] = pd.cut(df["future_return"], bins=bins, labels=False, include_lowest=True)

        df = df.dropna().reset_index(drop=True)
        logger.info(f"✅ Labels generated: {list(df.columns)}")
        return df

    except Exception as e:
        logger.error(f"❌ Labeling failed: {e}")
        return df
