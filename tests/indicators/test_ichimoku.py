# Source file: app\indicators\ichimoku.py

import pytest

pd = pytest.importorskip("pandas")

from app.indicators.ichimoku import add_ichimoku_features


def test_add_ichimoku_features():
    df = pd.DataFrame({
        "high": range(60, 120),
        "low": range(30, 90),
        "close": range(60)
    })
    result = add_ichimoku_features(df, {})
    expected = {"tenkan_sen", "kijun_sen", "senkou_span_a", "senkou_span_b", "chikou_span"}
    assert expected.issubset(result.columns)

