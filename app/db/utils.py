import time
from functools import wraps
from sqlalchemy.exc import OperationalError
from app.utils.logger import get_logger

logger = get_logger("db_utils")

def retry_on_failure(retries=3, delay=2, backoff=2):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0
            current_delay = delay
            e = None
            while attempts < retries:
                try:
                    return func(*args, **kwargs)
                except OperationalError as err:
                    e = err
                    logger.warning(f"⚠️ DB operation failed: {str(e)} — Retrying in {current_delay}s...")
                    time.sleep(current_delay)
                    attempts += 1
                    current_delay *= backoff
            logger.error("❌ All retry attempts failed.")
            raise e
        return wrapper
    return decorator
