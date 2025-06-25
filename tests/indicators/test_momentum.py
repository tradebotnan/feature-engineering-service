# Source file: app\indicators\momentum.py

import pytest

pd = pytest.importorskip("pandas")

from app.indicators.momentum import add_momentum_features


def test_add_momentum_features():
    df = pd.DataFrame({
        "close": [1, 2, 3, 4, 5],
        "high": [1, 2, 3, 4, 5],
        "low": [0.5, 1.5, 2.5, 3.5, 4.5],
    })
    cfg = {"rsi": {"periods": [2]}}
    result = add_momentum_features(df, cfg)
    assert "rsi_2" in result.columns

