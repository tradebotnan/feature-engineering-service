# Source file: app\indicators\options.py

import pytest

pd = pytest.importorskip("pandas")

from app.indicators.options import add_options_features


def test_add_options_features():
    df = pd.DataFrame({"put_volume": [1], "call_volume": [2], "close": [5]})
    cfg = {"put_call_ratio": {"enabled": True}}
    result = add_options_features(df, cfg)
    assert "put_call_ratio" in result.columns

