# Source file: app/utils/file_stitcher.py

from pathlib import Path
from typing import List

import pandas as pd
from common.io.parquet_utils import read_parquet_to_df
from common.logging.logger import setup_logger
from pandas import DataFrame

from utils.common_file_utils import get_previous_and_next_file_paths

logger = setup_logger()


def stitch_with_previous_and_next(
        df: pd.DataFrame,
        current_file: Path,
        level: str
) -> DataFrame | None:
    """
    Stitch previous and next files to current file for continuity.
    """
    buffer_size = {"day": 300, "minute": 300, "trades": 300}.get(level, 0)
    forward_look = 26 if level in ["day", "minute", "trades"] else 0

    prev_files, next_files = get_previous_and_next_file_paths(current_file, level=level, window=2)

    prev_chunks = collect_buffer_rows(prev_files, direction="prev", rows_needed=buffer_size)
    next_chunks = collect_buffer_rows(next_files, direction="next", rows_needed=forward_look)

    if not next_chunks:
        logger.warning(f"✅ No next files to stitch for {current_file.name}. Returning empty DataFrame.")
        return None

    stitched_df = pd.concat(prev_chunks + [df] + next_chunks, ignore_index=True)
    set_time_range_attrs(stitched_df, df)

    logger.info(
        f"✅ Stitch complete for {current_file.name}: "
        f"{len(prev_chunks)} prev files, {len(next_chunks)} next files."
    )
    return stitched_df


def collect_buffer_rows(files: List[Path], direction: str, rows_needed: int) -> List[pd.DataFrame]:
    """
    Collects row chunks from provided files up to the desired row count.
    direction: 'prev' (tail) or 'next' (head)
    """
    collected = []
    iterable = reversed(files) if direction == "next" else files

    for file in iterable:
        if rows_needed <= 0:
            break
        if not file.exists():
            continue

        try:
            df = read_parquet_to_df(file)
            if df.empty:
                continue

            take_rows = min(rows_needed, len(df))
            chunk = df.tail(take_rows) if direction == "prev" else df.head(take_rows)
            collected = ([chunk] + collected) if direction == "prev" else (collected + [chunk])
            rows_needed -= take_rows
            logger.info(f"✅ Stitch ({direction}): {take_rows} rows from {file.name}")
        except Exception as e:
            logger.warning(f"⚠️ Could not stitch {direction} file {file.name}: {e}")

    return collected


def set_time_range_attrs(stitched_df: pd.DataFrame, reference_df: pd.DataFrame):
    """
    Annotates the stitched DataFrame with timestamp bounds from the original file.
    """
    if "timestamp" in reference_df.columns:
        stitched_df.attrs["current_file_min_ts"] = reference_df["timestamp"].min()
        stitched_df.attrs["current_file_max_ts"] = reference_df["timestamp"].max()
