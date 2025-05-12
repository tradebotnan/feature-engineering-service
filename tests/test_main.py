import sys
import os
import pytest
from app.main import main

@pytest.fixture(autouse=True)
def set_env(monkeypatch):
    monkeypatch.setenv("SYMBOLS", "AAPL")
    monkeypatch.setenv("DATA_TYPES", "minute")
    monkeypatch.setenv("START_DATE", "2024-01-01")
    monkeypatch.setenv("END_DATE", "2024-01-01")
    monkeypatch.setenv("FEATURE_DIR", "data/filtered")
    monkeypatch.setenv("FEATURE_OUTPUT_PATH", "data/features")
    monkeypatch.setenv("MAIN_LOGGER", "preprocessor")

def test_main_cli_flow():
    main()  # Should now run cleanly using env vars
