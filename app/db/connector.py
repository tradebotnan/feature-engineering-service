from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from app.db.config import get_db_settings, build_sqlalchemy_url
from app.utils.logger import get_logger

logger = get_logger("db_connector")

engine = None
Session = None

def get_db_session():
    global engine, Session
    if engine is not None and Session is not None:
        return Session()

    try:
        config = get_db_settings()
        db_url = build_sqlalchemy_url(config)

        engine = create_engine(
            db_url,
            pool_size=config["POOL_SIZE"],
            max_overflow=config["MAX_OVERFLOW"],
            pool_timeout=config["POOL_TIMEOUT"],
            pool_recycle=config["POOL_RECYCLE"],
            echo=config["ECHO"],
        )

        Session = scoped_session(sessionmaker(bind=engine))
        logger.info("✅ Successfully connected to the database.")
        return Session()

    except Exception as e:
        logger.error(f"❌ Failed to connect to database: {e}")
        raise