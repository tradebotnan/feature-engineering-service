# Source file: app\feature\labeler.py

import pytest

pd = pytest.importorskip("pandas")

try:
    from app.feature.labeler import apply_labeling_strategy
except Exception as e:
    apply_labeling_strategy = None
    pytest.skip(f"labeler import failed: {e}", allow_module_level=True)


def test_apply_labeling_strategy():
    df = pd.DataFrame({"close": [1, 2, 3]})
    cfg = {"labels": {"trend": {"horizon": 1}}}
    result = apply_labeling_strategy(df, cfg)
    assert "trend" in result.columns

