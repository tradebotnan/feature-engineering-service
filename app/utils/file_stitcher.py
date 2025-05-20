# app/utils/file_stitcher.py

from common.io.parquet_utils import read_parquet_to_df
from common.logging.logger import setup_logger

logger = setup_logger()

from pathlib import Path
from typing import List
import pandas as pd


def stitch_with_previous_and_next(df: pd.DataFrame, current_file: Path, all_files: List[Path],
                                  data_type: str) -> pd.DataFrame:
    """
    Stitch previous and next files to current file for continuity.
    - previous: add last N rows from older files for rolling indicators
    - next: add first M rows from newer files for Ichimoku Chikou span
    """
    buffer_size = {"day": 300, "minute": 300, "trades": 300}.get(data_type, 0)
    forward_look = 26 if data_type == "day" else 0  # Only day data has Ichimoku applied

    if not all_files or (buffer_size == 0 and forward_look == 0):
        return df

    all_files_sorted = sorted(all_files)
    try:
        current_index = all_files_sorted.index(current_file)
    except ValueError:
        logger.warning(f"⚠️ Current file {current_file} not found in all_files list.")
        return df

    # ================
    # Step 1: previous files
    # ================
    collected_prev = []
    rows_needed = buffer_size
    i = current_index - 1

    while i >= 0 and rows_needed > 0:
        prev_file = all_files_sorted[i]
        if prev_file.exists():
            try:
                prev_df = read_parquet_to_df(prev_file)
                if not prev_df.empty:
                    take_rows = min(rows_needed, len(prev_df))
                    rows_to_append = prev_df.tail(take_rows)
                    collected_prev.insert(0, rows_to_append)  # prepend to preserve order
                    rows_needed -= take_rows
                    logger.info(f"✅ Stitch (prev): {take_rows} rows from {prev_file.name}")
            except Exception as e:
                logger.warning(f"⚠️ Could not stitch prev file {prev_file.name}: {e}")
        i -= 1

    # ================
    # Step 2: next files
    # ================
    collected_next = []
    rows_needed = forward_look
    i = current_index + 1

    while i < len(all_files_sorted) and rows_needed > 0:
        next_file = all_files_sorted[i]
        if next_file.exists():
            try:
                next_df = read_parquet_to_df(next_file)
                if not next_df.empty:
                    take_rows = min(rows_needed, len(next_df))
                    rows_to_append = next_df.head(take_rows)
                    collected_next.append(rows_to_append)  # append maintains order
                    rows_needed -= take_rows
                    logger.info(f"✅ Stitch (next): {take_rows} rows from {next_file.name}")
            except Exception as e:
                logger.warning(f"⚠️ Could not stitch next file {next_file.name}: {e}")
        i += 1

    # ================
    # Step 3: combine
    # ================
    stitched_parts = collected_prev + [df] + collected_next
    stitched_df = pd.concat(stitched_parts, ignore_index=True)

    # Store min/max timestamps for reference
    stitched_df.attrs["current_file_min_ts"] = df["timestamp"].min()
    stitched_df.attrs["current_file_max_ts"] = df["timestamp"].max()

    logger.info(
        f"✅ Stitch complete for {current_file.name}: "
        f"added {buffer_size - rows_needed if buffer_size else 0} prev rows, "
        f"{forward_look - rows_needed if forward_look else 0} next rows."
    )

    return stitched_df
