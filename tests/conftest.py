# Source file: tests\conftest.py

from pathlib import Path

import os

try:
    from dotenv import load_dotenv
except Exception:  # pragma: no cover - fallback when python-dotenv is missing
    def load_dotenv(dotenv_path):
        """Simple .env loader used when python-dotenv is unavailable."""
        with open(dotenv_path) as fh:
            for line in fh:
                if not line.strip() or line.strip().startswith("#"):
                    continue
                key, _, value = line.partition("=")
                os.environ.setdefault(key.strip(), value.strip())


def pytest_configure():
    # This runs before any tests
    env_path = Path(__file__).resolve().parents[1] / ".env"
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
    else:
        raise RuntimeError(f".env file not found at expected path: {env_path}")
