# Source file: app\constants\indicator_types.py

import importlib


def test_indicator_types_module_exists():
    mod = importlib.import_module("app.constants.indicator_types")
    assert hasattr(mod, "IndicatorType") or mod  # basic existence check

