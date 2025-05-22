# Source file: app/main.py

import time
from pathlib import Path

from common.db.db_writer import fetch_records
from common.db.session_manager import init_db_session
from common.env.env_loader import get_env_variable, load_env_list
from common.logging.logger import setup_logger
from common.schema.models import FeatureDispatchLog
from common.time.date_time import parse_date
from common.utils.retry_utils import retry
from sqlalchemy import and_

from app.feature.loader import load_and_process

logger = setup_logger()
SLEEP_INTERVAL = int(get_env_variable("WORKER_SLEEP_INTERVAL", False, "5"))


@retry(Exception, tries=3, delay=2, backoff=2)
def process_job(job):
    try:
        symbol = job.symbol
        date = job.date
        level = job.level
        row_id = job.id
        file_path = Path(f"D:\\{str(job.output_path)}")

        logger.info(f"🛠️ Processing feature generation for {symbol} ({level})")
        load_and_process(
            job.market, job.asset, level,
            symbol, str(date), file_path,
            row_id
        )

    except Exception as e:
        logger.error(f"❌ Error processing job {job}: {e}", exc_info=True)
        logger.error("Traceback:", exc_info=True)


def main():
    try:
        init_db_session()
        markets = load_env_list("MARKETS")
        assets = load_env_list("ASSETS")
        levels = load_env_list("LEVELS")
        symbols = load_env_list("SYMBOLS")
        start_date = parse_date(get_env_variable("START_DATE"))
        end_date = parse_date(get_env_variable("END_DATE"))

        date_filter = None

        if start_date and end_date:
            if FeatureDispatchLog.level == "trades":
                date_filter = and_(
                    FeatureDispatchLog.date >= start_date,
                    FeatureDispatchLog.date <= end_date
                )
            elif FeatureDispatchLog.level == "minute":
                date_filter = and_(
                    FeatureDispatchLog.year >= start_date.year,
                    FeatureDispatchLog.year <= end_date.year,
                    FeatureDispatchLog.month >= start_date.month,
                    FeatureDispatchLog.month <= end_date.month,
                )
            elif FeatureDispatchLog.level == "day":
                date_filter = and_(
                    FeatureDispatchLog.year >= start_date.year,
                    FeatureDispatchLog.year <= end_date.year
                )

        query_filter = and_(
            FeatureDispatchLog.status == "pending",
            FeatureDispatchLog.symbol.in_(symbols),
            FeatureDispatchLog.market.in_(markets),
            FeatureDispatchLog.asset.in_(assets),
            FeatureDispatchLog.level.in_(levels),
        )

        if date_filter:
            query_filter = and_(query_filter, date_filter)

        while True:
            try:
                jobs = fetch_records(FeatureDispatchLog, query_filter, limit=100)

                if not jobs:
                    logger.info("🟡 No pending features found. Waiting...")
                    time.sleep(SLEEP_INTERVAL)
                    continue

                for job in jobs:
                    try:
                        if not hasattr(job, "symbol") or not hasattr(job, "output_path"):
                            logger.warning(f"⚠️ Malformed job skipped: {job}")
                            continue

                        process_job(job)

                    except Exception as job_err:
                        logger.error(f"❌ Unhandled error while processing job: {job_err}", exc_info=True)
                        logger.error("Traceback:", exc_info=True)

            except Exception as fetch_err:
                logger.error(f"❌ Failed to fetch or process jobs: {fetch_err}", exc_info=True)
                logger.error("Traceback:", exc_info=True)
                time.sleep(SLEEP_INTERVAL)

    except Exception as e:
        logger.critical(f"❌ Fatal error during feature worker init: {e}", exc_info=True)
        logger.error("Traceback:", exc_info=True)


if __name__ == "__main__":
    main()
