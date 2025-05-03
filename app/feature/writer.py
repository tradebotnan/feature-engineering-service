from datetime import datetime
from pathlib import Path
import pandas as pd
from sqlalchemy.exc import SQLAlchemyError
from app.utils.logger import get_logger
from app.db.connector import get_db_session
from app.db.models import FeatureDispatchLog, StatusEnum

logger = get_logger("writer")

def write_features(df: pd.DataFrame, feature_path: str) -> bool:
    try:
        path = Path(feature_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(path, index=False)
        logger.info(f"✅ Features written to {feature_path}")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to write features to {feature_path}: {e}")
        return False


def update_feature_status(symbol: str = None, date: str = None, data_type: str = None,
                          row_id: int = None, status: str = "pending",
                          path: str = "", error_message: str = ""):
    session = get_db_session()
    try:
        if row_id is not None:
            job = session.query(FeatureDispatchLog).filter_by(id=row_id).first()
        else:
            job = session.query(FeatureDispatchLog).filter_by(symbol=symbol, date=date, data_type=data_type).first()

        if job:
            job.status = status
            job.feature_path = path or job.feature_path
            job.error_message = None if error_message in [None, "none", "None", ""] else error_message
            job.updated_at = datetime.utcnow()
            session.commit()
            logger.info(f"✅ FeatureDispatchLog updated → {status}")
        else:
            logger.warning("⚠️ No dispatch log entry found")

    except SQLAlchemyError as e:
        logger.error(f"❌ DB update failed: {e}")
        session.rollback()
    finally:
        session.close()

