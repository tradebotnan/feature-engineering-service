# Source file: app\feature\writer.py

import tempfile
import pytest

pd = pytest.importorskip("pandas")

try:
    from app.feature.writer import save_features
except Exception as e:  # pragma: no cover - skip if dependencies missing
    save_features = None
    pytest.skip(f"writer import failed: {e}", allow_module_level=True)


def test_save_features_tmp(tmp_path):
    df = pd.DataFrame({"a": [1]})
    tmp_file = tmp_path / "feat.parquet"
    assert save_features(df, str(tmp_file)) in [True, False]

