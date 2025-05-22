# Source file: app\feature\writer.py
from datetime import datetime
from pathlib import Path

import pandas as pd
from common.db.db_writer import update_record
from common.io.parquet_utils import save_parquet
from common.logging.logger import setup_logger
from common.schema.models import FeatureDispatchLog

logger = setup_logger()


def write_features(df: pd.DataFrame, feature_path: str) -> bool:
    try:
        path = Path(feature_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        save_parquet(df, path)
        # ✅ safest way to convert parquet → csv path
        new_path = path.with_suffix(".csv")
        df.to_csv(new_path, index=False)
        logger.info(f"✅ Features written to {feature_path}")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to write features to {feature_path}: {e}")
        logger.error("Traceback:", exc_info=True)
        return False


def update_feature_status(*, symbol: str = None, date: str = None, level: str = None,
                          row_id: int = None, status: str = "pending",
                          path: str = "", error_message: str = ""):
    filters = {"id": row_id} if row_id else {"symbol": symbol, "date": date, "level": level}
    updates = {
        "status": status,
        "feature_file": str(Path(path).stem),
        "error_message": None if error_message in [None, "none", "None", ""] else error_message,
        "updated_ts": datetime.now()
    }
    return update_record(FeatureDispatchLog, filters, updates)
