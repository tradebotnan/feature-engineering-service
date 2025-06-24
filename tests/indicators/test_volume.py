# Source file: app\indicators\volume.py

import pytest

pd = pytest.importorskip("pandas")

from app.indicators.volume import add_volume_features


def test_add_volume_features():
    df = pd.DataFrame({
        "high": [1, 2, 3],
        "low": [0, 1, 2],
        "close": [1, 2, 3],
        "volume": [10, 20, 30],
    })
    cfg = {"obv": {"enabled": True}}
    result = add_volume_features(df, cfg)
    assert "obv" in result.columns

