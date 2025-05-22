import argparse
import os
import subprocess

import pandas as pd
from common.logging.logger import setup_logger

logger = setup_logger()


def run_feature_engineering(input_path, output_dir, symbol, start_date, end_date):
    try:
        cmd = [
            "poetry", "run", "feature-engineering",
            "--input-dir", input_path,
            "--output-dir", output_dir,
            "--symbols", symbol,
            "--start-date", start_date,
            "--end-date", end_date
        ]
        logger.info(f"Running Feature Engineering for {symbol} {start_date}")
        subprocess.run(cmd, check=True)
        logger.info(f"Success: {symbol} {start_date}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed Feature Engineering for {symbol} {start_date}: {e}")
        logger.error("Traceback:", exc_info=True)


def main():
    parser = argparse.ArgumentParser(description="Dispatch historical files to Feature Engineering service.")
    parser.add_argument("--manifest", required=True, help="Path to historical_files manifest (CSV or Parquet)")
    parser.add_argument("--feature-engineering-path", required=True, help="Path to filtered input files")
    parser.add_argument("--output-dir", required=True, help="Path to save feature output")
    args = parser.parse_args()

    # Load manifest
    try:
        if args.manifest.endswith(".csv"):
            manifest = pd.read_csv(args.manifest)
        elif args.manifest.endswith(".parquet"):
            manifest = pd.read_parquet(args.manifest)
        else:
            logger.error("Unsupported manifest file type. Use CSV or Parquet.")
            logger.error("Traceback:", exc_info=True)
            return
    except Exception as e:
        logger.error(f"Error loading manifest file: {e}")
        logger.error("Traceback:", exc_info=True)
        return

    # Dispatch each file
    for idx, row in manifest.iterrows():
        try:
            symbol = row['symbol']
            level = row['level']
            market = row['market']
            date = row['date']
            start_date = str(date)
            end_date = str(date)

            input_path = os.path.join(args.feature_engineering_path, level, market, symbol, date.replace('-', '/'))

            # Validate path exists
            if not os.path.exists(input_path):
                logger.warning(f"Input path does not exist: {input_path}, skipping.")
                continue

            # Run feature engineering
            run_feature_engineering(input_path, args.output_dir, symbol, start_date, end_date)

        except Exception as e:
            logger.error(f"Error dispatching file idx {idx}: {e}")
            logger.error("Traceback:", exc_info=True)


if __name__ == "__main__":
    main()
