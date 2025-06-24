# Source file: app\feature\generator.py

import pytest

pd = pytest.importorskip("pandas")

try:
    from app.feature.generator import generate_features
except Exception as e:  # pragma: no cover - skip if dependencies missing
    generate_features = None
    pytest.skip(f"generator import failed: {e}", allow_module_level=True)


def test_generate_features_basic():
    df = pd.DataFrame({
        "open": [1],
        "high": [1],
        "low": [1],
        "close": [1],
        "volume": [1],
        "timestamp": pd.date_range("2024-01-01", periods=1, freq="D"),
    })
    cfg = {"features": {"volume_indicators": {"obv": {"enabled": False}}}}
    result = generate_features(df, cfg, level="day")
    assert isinstance(result, pd.DataFrame)

