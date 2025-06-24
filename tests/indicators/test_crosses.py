# Source file: app\indicators\crosses.py

import pytest

pd = pytest.importorskip("pandas")

from app.indicators.crosses import add_cross_features


def test_add_cross_features_basic():
    df = pd.DataFrame({"fast": [1, 2, 0], "slow": [0, 1, 2]})
    result = add_cross_features(df, {"include": ["fast_vs_slow"]})
    assert "cross_fast_slow" in result.columns
