import os
import pytest
from app.utils import env_loader
from pathlib import Path

def test_database_env_vars_loaded():
    assert env_loader.DB_HOST == "localhost"
    assert env_loader.DB_NAME == "tradebotnan"
    assert env_loader.DB_POOL_SIZE == 10
    assert isinstance(env_loader.SQLALCHEMY_ECHO, bool)

def test_feature_paths_loaded():
    assert env_loader.FEATURE_INPUT_PATH.startswith("D:/")
    assert env_loader.FEATURE_OUTPUT_PATH.startswith("D:/")

def test_logging_vars():
    # Normalize to POSIX format and remove trailing slashes
    log_dir = Path(env_loader.LOG_DIR).as_posix().rstrip("/")
    assert log_dir.endswith("/logs")

def test_optional_var_fallback():
    os.environ.pop("NON_EXISTENT_KEY", None)
    from app.utils.env_loader import get_env_variable
    assert get_env_variable("NON_EXISTENT_KEY", required=False, default="fallback") == "fallback"

def test_required_var_missing_raises():
    with pytest.raises(EnvironmentError):
        from app.utils.env_loader import get_env_variable
        get_env_variable("MISSING_KEY", required=True)
