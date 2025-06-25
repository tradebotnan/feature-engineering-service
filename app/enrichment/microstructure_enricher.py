# Source file: app/enrichment/microstructure_enricher.py

import pandas as pd
from common.logging.logger import setup_logger

logger = setup_logger()


def enrich_with_microstructure(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds microstructure features to tick-level trades:
    - Tick direction (up/down/same)
    - Price difference (tick delta)
    - VWAP over 1s, 5s, 10s rolling windows
    """
    try:
        required_columns = ["timestamp", "price", "size"]
        if df.empty or not all(col in df.columns for col in required_columns):
            logger.warning("⚠️ Cannot enrich microstructure: missing timestamp, price, or size columns.")
            # Add empty columns
            empty_columns = ["tick_direction", "price_diff", "vwap_1s", "vwap_5s", "vwap_10s"]
            for col in empty_columns:
                df[col] = None
            return df

        df = df.sort_values("timestamp").copy()

        # Tick direction: +1 (up), -1 (down), 0 (flat)
        df["tick_direction"] = df["price"].diff().apply(lambda x: 1 if x > 0 else (-1 if x < 0 else 0))

        # Price diff
        df["price_diff"] = df["price"].diff()

        # Set timestamp index for rolling
        df.set_index("timestamp", inplace=True)

        # Rolling VWAP calculations (1s, 5s, 10s)
        for sec in [1, 5, 10]:
            window = f"{sec}s"
            vwap_col = f"vwap_{sec}s"
            df[vwap_col] = (
                (df["price"] * df["size"]).rolling(window).sum()
                / df["size"].rolling(window).sum()
            )

        df.reset_index(inplace=True)
        logger.info(f"✅ Microstructure enrichment applied: {len(df)} rows, {df.columns[-5:].tolist()}")
        return df

    except Exception as e:
        logger.exception(f"❌ Failed microstructure enrichment: {e}")
        return df