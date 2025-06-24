# Source file: app\indicators\candles.py

import pytest

pd = pytest.importorskip("pandas")

from app.indicators.candles import add_body_size


def test_add_body_size():
    df = pd.DataFrame({"open": [1, 2], "close": [2, 3]})
    result = add_body_size(df)
    assert "body_size" in result.columns

