# Source file: app\indicators\fundamentals.py

import importlib
import pytest


def test_fundamentals_module_missing():
    with pytest.raises(ModuleNotFoundError):
        importlib.import_module("app.indicators.fundamentals")

