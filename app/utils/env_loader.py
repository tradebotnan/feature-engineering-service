import os
from dotenv import load_dotenv
from pathlib import Path

# Load from .env at root
env_path = Path(__file__).resolve().parents[2] / '.env'
load_dotenv(dotenv_path=env_path)

import yaml
from pathlib import Path


def load_yaml_config(config_path: str = "config/settings.yaml") -> dict:
    """
    Loads a YAML configuration file.

    :param config_path: Path to the YAML file.
    :return: Parsed configuration as a dictionary.
    """
    config_file = Path(config_path)
    if not config_file.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_file, "r") as f:
        return yaml.safe_load(f)

def get_env_variable(key: str, required: bool = True, default=None):
    value = os.getenv(key)
    if value is None:
        if required:
            raise EnvironmentError(f"Missing required environment variable: {key}")
        return default
    return value

def load_env_list(key: str, delimiter: str = ",") -> list[str]:
    raw = os.getenv(key, "")
    return [item.strip() for item in raw.split(delimiter) if item.strip()]


def resolve_env_path(key: str, required: bool = True, default: str = None) -> str:
    raw_value = os.getenv(key)

    if raw_value is None:
        if required:
            raise EnvironmentError(f"Missing required environment variable: {key}")
        return default

    base_dir = os.getenv("BASE_DIR", "")
    resolved = raw_value.replace("${BASE_DIR}", base_dir)
    return resolved



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
BASE_DIR = get_env_variable("BASE_DIR")
FEATURE_INPUT_PATH = resolve_env_path("FEATURE_INPUT_PATH")
FEATURE_OUTPUT_PATH = resolve_env_path("FEATURE_OUTPUT_PATH")

# Logging
LOG_DIR = resolve_env_path("LOG_DIR")
LOG_INFO_FILE = get_env_variable("LOG_INFO_FILE", default="info.log")
LOG_ERROR_FILE = get_env_variable("LOG_ERROR_FILE", default="error.log")
LOG_DEBUG_FILE = get_env_variable("LOG_DEBUG_FILE", default="debug.log")
LOG_WARNING_FILE = get_env_variable("LOG_WARNING_FILE", default="warning.log")
LOG_NAME = get_env_variable("LOG_NAME", default="feature_engineering")
LOG_LEVEL = get_env_variable("LOG_LEVEL", default="INFO")
LOG_FORMAT = get_env_variable("LOG_FORMAT", default="[%(asctime)s] [%(levelname)s] %(message)s")
