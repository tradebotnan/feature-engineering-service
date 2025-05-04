import os
from pathlib import Path
from datetime import datetime, timedelta

from app.feature.loader import load_and_process
from app.utils.env_loader import get_env_variable, load_env_list, resolve_env_path
from app.utils.logger import get_logger

logger = get_logger(get_env_variable("MAIN_LOGGER"))

def date_range(start: str, end: str):
    start_dt = datetime.strptime(start, "%Y-%m-%d")
    end_dt = datetime.strptime(end, "%Y-%m-%d")
    while start_dt <= end_dt:
        yield start_dt.strftime("%Y-%m-%d")
        start_dt += timedelta(days=1)

def main():
    input_dir = resolve_env_path("FEATURE_INPUT_PATH", True, "D:/tradebotnan/data/filtered")
    output_dir = resolve_env_path("FEATURE_OUTPUT_PATH", True, "D:/tradebotnan/data/features")

    symbols = load_env_list("SYMBOLS")
    data_types = load_env_list("DATA_TYPES")
    start_date = get_env_variable("START_DATE")
    end_date = get_env_variable("END_DATE")

    for data_type in data_types:
        for symbol in symbols:
            for date_str in date_range(start_date, end_date):
                file_path = Path(f"{input_dir}/{data_type}_{symbol}_{date_str}.parquet")
                if not file_path.exists():
                    logger.warning(f"⛔ File not found: {file_path}")
                    continue

                logger.info(f"📂 Processing {symbol} - {date_str} ({data_type})")
                try:
                    df = load_and_process(
                        file_path=file_path,
                        symbol=symbol,
                        date=date_str,
                        data_type=data_type,
                        config=None  # Optionally load with `load_yaml_config()`
                    )
                    logger.info(f"✅ Done: {symbol} - {date_str} ({data_type})")

                except Exception as e:
                    logger.error(f"❌ Failed processing {file_path}: {e}")

if __name__ == "__main__":
    main()
