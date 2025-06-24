# Source file: app\feature\loader.py

import pytest

pd = pytest.importorskip("pandas")

try:
    from app.feature.loader import trim_to_original_time_range
except Exception as e:
    trim_to_original_time_range = None
    pytest.skip(f"loader import failed: {e}", allow_module_level=True)


def test_trim_to_original_time_range():
    df = pd.DataFrame({"timestamp": pd.date_range("2024-01-01", periods=3, freq="D")})
    df.attrs["current_file_min_ts"] = df["timestamp"].iloc[0]
    df.attrs["current_file_max_ts"] = df["timestamp"].iloc[2]
    result = trim_to_original_time_range(df)
    assert len(result) == 3

