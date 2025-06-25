import os
from pathlib import Path
import pytest

pd = pytest.importorskip("pandas")
from app.utils.common_file_utils import (
    get_previous_and_next_file_paths,
    extract_suffix,
    generate_year_paths,
    generate_month_paths,
    generate_day_paths,
)


def test_get_previous_and_next_file_paths(tmp_path):
    base = tmp_path / "base"
    current = base / "filtered" / "us" / "stocks" / "day" / "AAPL" / "2022" / "filtered_us_stocks_day_AAPL_2022.parquet"
    current.parent.mkdir(parents=True)
    current.touch()

    prev, next_ = get_previous_and_next_file_paths(current, level="day", window=1)
    assert prev[0].name.endswith("2021.parquet")
    assert next_[0].name.endswith("2023.parquet")


def test_extract_suffix():
    dt = extract_suffix("foo_2023-05-01", "%Y-%m-%d")
    assert dt.year == 2023 and dt.month == 5 and dt.day == 1


def test_generate_year_month_day_paths(tmp_path):
    base = tmp_path
    paths = generate_year_paths(base, "filtered", "us", "stocks", "day", "AAPL", "pfx_", pd.Timestamp("2024"), -1, 1)
    assert paths[0].name.endswith("2023.parquet")
    mpaths = generate_month_paths(base, "filtered", "us", "stocks", "minute", "AAPL", "pfx_", pd.Timestamp("2024-05"), 1, 1)
    assert mpaths[0].name.endswith("2024-06.parquet")
    dpaths = generate_day_paths(base, "filtered", "us", "stocks", "trades", "AAPL", "pfx_", pd.Timestamp("2024-05-05"), 1, 1)
    assert dpaths[0].name.endswith("2024-05-06.parquet")
