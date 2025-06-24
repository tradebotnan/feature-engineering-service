# Source file: app\indicators\engineered.py

import pytest

pd = pytest.importorskip("pandas")
np = pytest.importorskip("numpy")

from app.indicators.engineered import add_engineered_features


def test_add_engineered_features():
    df = pd.DataFrame({"close": np.arange(10)})
    cfg = {"return": {"include": ["return_1d"]}}
    result = add_engineered_features(df, cfg)
    assert "return_1d" in result.columns

