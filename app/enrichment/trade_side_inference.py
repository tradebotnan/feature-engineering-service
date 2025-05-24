# Source file: app/enrichment/trade_side_inference.py

import pandas as pd
from common.logging.logger import setup_logger

logger = setup_logger()


def infer_trade_side(df: pd.DataFrame) -> pd.DataFrame:
    """
    Infers trade direction (buy/sell) using tick rule:
    - If current price > previous price → buy (1)
    - If current price < previous price → sell (-1)
    - Else, inherit last known direction

    Adds:
    - `trade_side`: 1 (buy), -1 (sell)
    - `tick_direction`: optional fallback if not already set
    """
    try:
        if df.empty or "price" not in df.columns or "timestamp" not in df.columns:
            logger.warning("⚠️ Cannot infer trade side: missing required columns.")
            return df

        df = df.sort_values("timestamp").copy()

        # Reuse or calculate tick_direction
        if "tick_direction" not in df.columns:
            df["tick_direction"] = df["price"].diff().apply(lambda x: 1 if x > 0 else (-1 if x < 0 else 0))

        # Fill neutral ticks with previous direction
        df["trade_side"] = df["tick_direction"].mask(df["tick_direction"] == 0).ffill().fillna(0).astype(int)

        logger.info(f"✅ Trade side inferred for {len(df)} rows.")
        return df

    except Exception as e:
        logger.exception(f"❌ Failed trade side inference: {e}")
        return df
