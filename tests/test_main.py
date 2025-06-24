# Source file: app\main.py

import importlib
import types


def test_main_exists():
    module = importlib.import_module("app.main")
    assert isinstance(module, types.ModuleType)

