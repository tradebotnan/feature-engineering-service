import os
from dotenv import load_dotenv
from app.utils.logger import get_logger

logger = get_logger(__name__)

def load_env():
    logger.info("Loading environment variables...")
    load_dotenv()
    config = {
        "INPUT_PATH": os.getenv("FEATURE_ENGINEERING_INPUT_PATH", "./data/filtered/"),
        "OUTPUT_PATH": os.getenv("FEATURE_ENGINEERING_OUTPUT_PATH", "./data/features/"),
        "LOG_LEVEL": os.getenv("LOG_LEVEL", "INFO"),
    }
    logger.info(f"Environment loaded: {config}")
    return config

