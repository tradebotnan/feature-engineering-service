import pytest

pd = pytest.importorskip("pandas")
from app.feature.loader import trim_to_original_time_range


def test_trim_to_original_time_range():
    df = pd.DataFrame({"timestamp": pd.date_range("2024-01-01", periods=5, freq="D", tz="UTC")})
    df.attrs["current_file_min_ts"] = df["timestamp"].iloc[1]
    df.attrs["current_file_max_ts"] = df["timestamp"].iloc[3]
    trimmed = trim_to_original_time_range(df)
    assert len(trimmed) == 3
