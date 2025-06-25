# Source file: app\indicators\accumulation_distribution.py

import pytest

pd = pytest.importorskip("pandas")

from app.indicators.accumulation_distribution import add_accumulation_distribution


def test_add_accumulation_distribution():
    df = pd.DataFrame({
        "high": [1, 2, 3],
        "low": [0, 1, 2],
        "close": [1, 2, 3],
        "volume": [10, 20, 30],
    })
    cfg = {"enabled": True}
    result = add_accumulation_distribution(df, cfg)
    assert "accum_dist" in result.columns

