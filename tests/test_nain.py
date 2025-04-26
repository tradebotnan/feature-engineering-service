import pytest
import sys
from app.main import main

def test_main_cli(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["main.py", "--input-dir=./", "--output-dir=./", "--symbols=AAPL", "--start-date=2023-01-01", "--end-date=2023-01-01"])
    main()
