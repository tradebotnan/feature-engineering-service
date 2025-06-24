# Source file: app\indicators\donchian_channel.py

import pytest

pd = pytest.importorskip("pandas")

from app.indicators.donchian_channel import add_donchian_channel


def test_add_donchian_channel():
    df = pd.DataFrame({
        "high": [1, 2, 3],
        "low": [0, 1, 2],
    })
    result = add_donchian_channel(df, {"periods": [2]})
    assert "donchian_high" in " ".join(result.columns)

