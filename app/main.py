import argparse
from datetime import date

from app.utils.env_loader import get_env_variable
from app.utils.logger import get_logger
from app.feature.loader import load_and_process
from app.preprocessing.data_preprocessor import preprocess_dataframe
from app.feature.generator import generate_features
from app.feature.labeler import apply_labeling_strategy
from app.feature.writer import write_features

logger = get_logger("feature_engineering_main")


def main():
    parser = argparse.ArgumentParser(description="Feature Engineering CLI")
    parser.add_argument("--input-dir", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--symbols", required=True)
    parser.add_argument("--start-date", required=True)
    parser.add_argument("--end-date", required=True)
    parser.add_argument("--data-type", required=True, choices=["day", "minute", "trades"])
    args = parser.parse_args()

    logger.info(f"🔍 Starting Feature Engineering for {args.symbols} from {args.start_date} to {args.end_date} ({args.data_type})")

    symbols = args.symbols.split(",")
    for symbol in symbols:
        file_path = f"{args.input_dir}/{args.data_type}_{symbol}_{args.start-date}.parquet"
        logger.info(f"📂 Loading file: {file_path}")
        df = load_and_process(file_path)
        df = preprocess_dataframe(df)
        df = generate_features(df, {"data_type": args.data_type})
        df = apply_labeling_strategy(df)

        output_path = f"{args.output_dir}/{args.data_type}_{symbol}_{args.start-date}.parquet"
        write_features(df, output_path)

    logger.info("✅ Feature Engineering CLI run completed successfully.")


if __name__ == "__main__":
    main()
