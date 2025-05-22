from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Tuple

from dateutil.relativedelta import relativedelta


def get_previous_and_next_file_paths(
        current_file: Path, level: str, window: int = 2
) -> Tuple[List[Path], List[Path]]:
    """
    Given a current file path and level (day/minute/trades),
    return (previous_files, next_files) with up to `window` files each.
    """
    stem = current_file.stem
    parent = current_file.parent
    symbol = parent.parts[-2]
    level = level.lower()

    # base_dir / filtered / market / asset / level / symbol / ...
    try:
        base_dir = parent.parents[5]
        filtered_dir, market, asset = parent.parts[-6], parent.parts[-5], parent.parts[-4]
    except IndexError as e:
        raise ValueError(f"❌ Unexpected file path structure: {current_file}") from e

    prefix = f"{market}_{asset}_{level}_{symbol}_"
    previous, next_ = [], []

    if level == "day":
        current_year = extract_suffix(stem, "%Y")
        previous = generate_year_paths(base_dir, filtered_dir, market, asset, level, symbol, prefix, current_year, -1,
                                       window)
        next_ = generate_year_paths(base_dir, filtered_dir, market, asset, level, symbol, prefix, current_year, +1,
                                    window)

    elif level == "minute":
        current_ym = extract_suffix(stem, "%Y-%m")
        previous = generate_month_paths(base_dir, filtered_dir, market, asset, level, symbol, prefix, current_ym, -1,
                                        window)
        next_ = generate_month_paths(base_dir, filtered_dir, market, asset, level, symbol, prefix, current_ym, +1,
                                     window)

    elif level == "trades":
        current_ymd = extract_suffix(stem, "%Y-%m-%d")
        previous = generate_day_paths(base_dir, filtered_dir, market, asset, level, symbol, prefix, current_ymd, -1,
                                      window)
        next_ = generate_day_paths(base_dir, filtered_dir, market, asset, level, symbol, prefix, current_ymd, +1,
                                   window)

    else:
        raise ValueError(f"Unsupported level: {level}")

    return previous, next_


# === Helper functions ===

def extract_suffix(stem: str, date_format: str) -> datetime:
    try:
        suffix = stem.split("_")[-1]
        return datetime.strptime(suffix, date_format)
    except Exception as e:
        raise ValueError(f"❌ Failed to extract timestamp from {stem} using {date_format}") from e


def generate_year_paths(base, filtered, market, asset, level, symbol, prefix, current_year, direction, window):
    paths = []
    for i in range(1, window + 1):
        year = current_year.year + direction * i
        suffix = str(year)
        path = base / filtered / market / asset / level / symbol / suffix / f"{prefix}{suffix}.parquet"
        paths.append(path)
    return paths


def generate_month_paths(base, filtered, market, asset, level, symbol, prefix, current_date, direction, window):
    paths = []
    for i in range(1, window + 1):
        month_date = current_date + relativedelta(months=direction * i)
        suffix = month_date.strftime("%Y-%m")
        path = base / filtered / market / asset / level / symbol / suffix / f"{prefix}{suffix}.parquet"
        paths.append(path)
    return paths


def generate_day_paths(base, filtered, market, asset, level, symbol, prefix, current_date, direction, window):
    paths = []
    for i in range(1, window + 1):
        day_date = current_date + timedelta(days=direction * i)
        suffix = day_date.strftime("%Y-%m-%d")
        path = base / filtered / market / asset / level / symbol / suffix / f"{prefix}{suffix}.parquet"
        paths.append(path)
    return paths
