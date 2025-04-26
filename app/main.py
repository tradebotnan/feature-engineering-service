import argparse
from app.utils.env_loader import load_env
from app.utils.logger import get_logger

logger = get_logger(__name__)

def main():
    config = load_env()

    parser = argparse.ArgumentParser(description="Feature Engineering CLI")
    parser.add_argument("--input-dir", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--symbols", required=True)
    parser.add_argument("--start-date", required=True)
    parser.add_argument("--end-date", required=True)
    args = parser.parse_args()

    logger.info(f"Starting Feature Engineering for symbols: {args.symbols} from {args.start_date} to {args.end_date}")

    # Placeholder - actual processing will happen here later
    logger.info("Feature Engineering CLI run completed successfully.")

if __name__ == "__main__":
    main()
