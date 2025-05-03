from sqlalchemy.exc import SQLAlchemyError
from app.db.connector import get_db_session
from app.db.models import FeatureDispatchLog
from app.utils.logger import get_logger

logger = get_logger("dispatcher")

def fetch_pending_jobs(limit=10):
    session = get_db_session()
    try:
        jobs = session.query(FeatureDispatchLog).filter_by(status='pending').limit(limit).all()
        logger.info(f"✅ Fetched {len(jobs)} pending jobs")
        return jobs
    except SQLAlchemyError as e:
        logger.error(f"❌ Failed to fetch jobs: {e}")
        return []
    finally:
        session.close()