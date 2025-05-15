# app/utils/file_stitcher.py

import pandas as pd
from pathlib import Path
from typing import List, Optional
from common.logging.logger import setup_logger

logger = setup_logger()

def get_previous_file(current_file: Path, all_files: List[Path]) -> Optional[Path]:
    """
    Get the previous file (chronologically) from a list of files.
    Assumes all_files are sorted by date ascending.
    """
    sorted_files = sorted(all_files)
    try:
        index = sorted_files.index(current_file)
        if index > 0:
            return sorted_files[index - 1]
    except ValueError:
        pass
    return None

def stitch_with_previous(df: pd.DataFrame, current_file: Path, all_files: List[Path], data_type: str) -> pd.DataFrame:
    """
    If applicable, append last N rows from previous file to current df for continuity.
    """
    buffer_size = {"day": 30, "minute": 50, "trades": 30}.get(data_type, 0)

    if buffer_size == 0:
        return df

    previous_file = get_previous_file(current_file, all_files)
    if previous_file and previous_file.exists():
        try:
            prev_df = pd.read_parquet(previous_file)
            if not prev_df.empty:
                rows_to_append = prev_df.tail(buffer_size)
                stitched_df = pd.concat([rows_to_append, df], ignore_index=True)
                logger.info(f"✅ Stitch applied: {previous_file.name} → {current_file.name} (added {len(rows_to_append)} rows)")
                return stitched_df
        except Exception as e:
            logger.warning(f"⚠️ Could not stitch from {previous_file}: {e}")

    return df
