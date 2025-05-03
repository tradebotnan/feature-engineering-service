import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from app.utils.logger import get_logger
from app.utils.env_loader import get_env_variable
from app.db.dispatcher import get_pending_jobs
from app.loader import load_filtered_file
from app.preprocessor import preprocess_dataframe
from app.generator import generate_features
from app.labeler import label_features
from app.writer import write_features, update_feature_status

logger = get_logger("feature_worker")
NUM_THREADS = int(get_env_variable("NUM_THREADS", "4"))
SLEEP_INTERVAL = int(get_env_variable("WORKER_SLEEP_INTERVAL", "5"))


def process_job(job):
    symbol = job.symbol
    date = job.date
    data_type = job.data_type
    file_path = job.filtered_path

    try:
        logger.info(f"🛠️ Processing feature generation for {symbol} {date} ({data_type})")
        df = load_filtered_file(file_path)
        df = preprocess_dataframe(df)
        df = generate_features(df, {"data_type": data_type})
        df = label_features(df)

        feature_path = file_path.replace("filtered", "features")
        success = write_features(df, feature_path)

        if success:
            update_feature_status(symbol, date, data_type, "completed", path=feature_path)
        else:
            update_feature_status(symbol, date, data_type, "error", path=feature_path, error_message="Failed to write file")

    except Exception as e:
        logger.error(f"❌ Error processing {symbol} {date} ({data_type}): {e}")
        update_feature_status(symbol, date, data_type, "error", error_message=str(e))


def run_worker_loop():
    while True:
        jobs = get_pending_jobs()
        if not jobs:
            logger.info("🟡 No pending features found. Waiting...")
            time.sleep(SLEEP_INTERVAL)
            continue

        with ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
            futures = [executor.submit(process_job, job) for job in jobs]
            for future in as_completed(futures):
                future.result()


if __name__ == "__main__":
    logger.info("🚀 Feature Engineering Worker started.")
    run_worker_loop()
