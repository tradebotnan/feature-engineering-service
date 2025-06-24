# Source file: app\indicators\chaikin_money_flow.py

import pytest

pd = pytest.importorskip("pandas")

from app.indicators.chaikin_money_flow import add_chaikin_money_flow


def test_add_chaikin_money_flow():
    df = pd.DataFrame({
        "high": [1, 2, 3],
        "low": [0, 1, 2],
        "close": [0.5, 1.5, 2.5],
        "volume": [10, 20, 30],
    })
    cfg = {"periods": [2]}
    result = add_chaikin_money_flow(df, cfg)
    assert "cmf_2" in result.columns

