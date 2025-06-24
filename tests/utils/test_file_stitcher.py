from pathlib import Path
from unittest.mock import patch
import pandas as pd
from app.utils.file_stitcher import collect_buffer_rows, set_time_range_attrs


def dummy_reader(path: Path):
    return pd.DataFrame({"timestamp": [1, 2, 3]})


def test_collect_buffer_rows(tmp_path):
    files = [tmp_path / f"file{i}.parquet" for i in range(2)]
    for f in files:
        f.touch()
    with patch("app.utils.file_stitcher.read_parquet_to_df", dummy_reader):
        chunks = collect_buffer_rows(files, "prev", rows_needed=2)
    assert len(chunks) == 1
    assert len(chunks[0]) == 2


def test_set_time_range_attrs():
    ref = pd.DataFrame({"timestamp": [1, 2, 3]})
    stitched = pd.DataFrame({"timestamp": [0, 1, 2, 3, 4]})
    set_time_range_attrs(stitched, ref)
    assert stitched.attrs["current_file_min_ts"] == 1
    assert stitched.attrs["current_file_max_ts"] == 3
