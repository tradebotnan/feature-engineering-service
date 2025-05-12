# Source file: tests\conftest.py

from pathlib import Path

from dotenv import load_dotenv


def pytest_configure():
    # This runs before any tests
    env_path = Path(__file__).resolve().parents[1] / ".env"
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
    else:
        raise RuntimeError(f".env file not found at expected path: {env_path}")
