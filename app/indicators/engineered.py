# Source file: app/indicators/engineered.py
import numpy as np
import pandas as pd
from common.logging.logger import setup_logger

logger = setup_logger()

def add_engineered_features(df: pd.DataFrame, config: dict) -> pd.DataFrame:
    df = df.copy()

    # =====================
    # 1. Return Features
    # =====================
    if "return" in config:
        include = config["return"].get("include", [])
        if "return_1d" in include:
            df["return_1d"] = df["close"].pct_change(periods=1)
        if "return_5d" in include:
            df["return_5d"] = df["close"].pct_change(periods=5)
        if "log_return" in include:
            df["log_return"] = np.log(df["close"] / df["close"].shift(1)).replace([-np.inf, np.inf], np.nan)

    # =====================
    # 2. Trend Strength Features
    # =====================
    if "trend_strength" in config:
        periods = config["trend_strength"].get("periods", [])
        for period in periods:
            roc = df["close"].pct_change(periods=period)
            volatility = df["close"].pct_change().rolling(window=period).std()
            trend_strength = roc / volatility.replace(0, np.nan)
            df[f"trend_strength_{period}"] = trend_strength

    # =====================
    # 3. Z-Score Features
    # =====================
    if "zscore" in config:
        apply_cols = config["zscore"].get("apply_to", [])
        for col in apply_cols:
            if col in df.columns:
                rolling_mean = df[col].rolling(window=20).mean()
                rolling_std = df[col].rolling(window=20).std()
                df[f"zscore_{col}"] = (df[col] - rolling_mean) / rolling_std

    logger.info(f"✅ Engineered features generated: {list(df.columns)}")
    return df