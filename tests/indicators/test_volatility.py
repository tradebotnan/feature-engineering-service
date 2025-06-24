# Source file: app\indicators\volatility.py

import pytest

pd = pytest.importorskip("pandas")

from app.indicators.volatility import add_volatility_features


def test_add_volatility_features():
    df = pd.DataFrame({
        "high": [1, 2, 3, 4],
        "low": [0.5, 1.5, 2.5, 3.5],
        "close": [1, 2, 3, 4],
    })
    cfg = {"atr": {"periods": [2]}}
    result = add_volatility_features(df, cfg)
    assert "atr_2" in result.columns

