import os
from dotenv import load_dotenv
from pathlib import Path

# Load from .env at root
env_path = Path(__file__).resolve().parents[2] / '.env'
load_dotenv(dotenv_path=env_path)

def get_env_variable(key: str, required: bool = True, default=None):
    value = os.getenv(key)
    if value is None:
        if required:
            raise EnvironmentError(f"Missing required environment variable: {key}")
        return default
    return value

# Database
DATABASE_URL = get_env_variable("DATABASE_URL")
DB_HOST = get_env_variable("HOST")
DB_PORT = get_env_variable("PORT")
DB_NAME = get_env_variable("NAME")
DB_USER = get_env_variable("USER")
DB_PASSWORD = get_env_variable("PASSWORD")
DB_POOL_SIZE = int(get_env_variable("POOL_SIZE", default=10))
DB_MAX_OVERFLOW = int(get_env_variable("MAX_OVERFLOW", default=20))
DB_POOL_TIMEOUT = int(get_env_variable("POOL_TIMEOUT", default=30))
DB_POOL_RECYCLE = int(get_env_variable("POOL_RECYCLE", default=1800))
SQLALCHEMY_ECHO = get_env_variable("SQLALCHEMY_ECHO", default="false").lower() == "true"

# Paths
FEATURE_INPUT_PATH = get_env_variable("FEATURE_ENGINEERING_INPUT_PATH")
FEATURE_OUTPUT_PATH = get_env_variable("FEATURE_ENGINEERING_OUTPUT_PATH")

# Logging
LOG_DIR = get_env_variable("LOG_DIR")
LOG_INFO_FILE = get_env_variable("LOG_INFO_FILE", default="info.log")
LOG_ERROR_FILE = get_env_variable("LOG_ERROR_FILE", default="error.log")
LOG_DEBUG_FILE = get_env_variable("LOG_DEBUG_FILE", default="debug.log")
LOG_WARNING_FILE = get_env_variable("LOG_WARNING_FILE", default="warning.log")
LOG_NAME = get_env_variable("LOG_NAME", default="feature_engineering")
LOG_LEVEL = get_env_variable("LOG_LEVEL", default="INFO")
LOG_FORMAT = get_env_variable("LOG_FORMAT", default="[%(asctime)s] [%(levelname)s] %(message)s")
