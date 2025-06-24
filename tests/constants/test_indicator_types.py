# Source file: app\constants\indicator_types.py

import importlib
import pytest


def test_indicator_types_module_missing():
    with pytest.raises(ModuleNotFoundError):
        importlib.import_module("app.constants.indicator_types")

