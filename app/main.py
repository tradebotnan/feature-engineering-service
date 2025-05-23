# Source file: app/main.py

from concurrent.futures import ThreadPoolExecutor, as_completed
from sqlalchemy import and_, or_

from common.db.db_writer import fetch_records
from common.db.session_manager import init_db_session
from common.env.env_loader import get_env_variable, load_env_list
from common.io.path_resolver import get_path_from_file_name
from common.logging.logger import setup_logger
from common.schema.models import FeatureDispatchLog
from common.time.date_time import parse_date
from common.utils.retry_utils import retry

from app.feature.loader import load_and_process

logger = setup_logger()

SLEEP_INTERVAL = int(get_env_variable("WORKER_SLEEP_INTERVAL", False, "5"))
MAX_WORKERS = int(get_env_variable("MAX_WORKERS", False, "4"))
BATCH_SIZE = 100

@retry(Exception, tries=3, delay=2, backoff=2)
def process_job(job):
    try:
        symbol = job.symbol
        date = job.date
        level = job.level
        row_id = job.id
        file_path = get_path_from_file_name(job.filtered_file).with_suffix(".parquet")
        logger.info(f"🛠️ Processing feature generation for {symbol} ({level})")
        load_and_process(job.market, job.asset, level, symbol, str(date), file_path, row_id)
    except Exception as e:
        logger.error(f"❌ Error processing job {job}: {e}", exc_info=True)


def build_query_filter(start_date, end_date, levels, symbols, markets, assets):
    base_filter = and_(
        FeatureDispatchLog.status == "pending",
        FeatureDispatchLog.filtered_file.isnot(None),
        FeatureDispatchLog.symbol.in_(symbols),
        FeatureDispatchLog.market.in_(markets),
        FeatureDispatchLog.asset.in_(assets),
        FeatureDispatchLog.level.in_(levels)
    )

    date_filters = []
    for level in levels:
        if level == "trades":
            date_filters.append(and_(
                FeatureDispatchLog.level == "trades",
                FeatureDispatchLog.date >= start_date,
                FeatureDispatchLog.date <= end_date
            ))
        elif level == "minute":
            date_filters.append(and_(
                FeatureDispatchLog.level == "minute",
                or_(
                    and_(
                        FeatureDispatchLog.year == start_date.year,
                        FeatureDispatchLog.month >= start_date.month
                    ),
                    and_(
                        FeatureDispatchLog.year == end_date.year,
                        FeatureDispatchLog.month <= end_date.month
                    ),
                    and_(
                        FeatureDispatchLog.year > start_date.year,
                        FeatureDispatchLog.year < end_date.year
                    )
                )
            ))
        elif level == "day":
            date_filters.append(and_(
                FeatureDispatchLog.level == "day",
                FeatureDispatchLog.year >= start_date.year,
                FeatureDispatchLog.year <= end_date.year
            ))

    if date_filters:
        full_filter = and_(base_filter, or_(*date_filters))
    else:
        full_filter = base_filter

    return full_filter


def main():
    try:
        init_db_session()

        markets = load_env_list("MARKETS")
        assets = load_env_list("ASSETS")
        levels = load_env_list("LEVELS")
        symbols = load_env_list("SYMBOLS")
        start_date = parse_date(get_env_variable("START_DATE"))
        end_date = parse_date(get_env_variable("END_DATE"))

        query_filter = build_query_filter(start_date, end_date, levels, symbols, markets, assets)

        jobs = fetch_records(FeatureDispatchLog, query_filter, limit=BATCH_SIZE)

        if not jobs:
            logger.info("🟡 No matching jobs found.")
            return

        logger.info(f"🚀 Processing {len(jobs)} jobs...")

        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = {
                executor.submit(process_job, job): job
                for job in jobs if hasattr(job, "symbol") and hasattr(job, "filtered_file")
            }

            for future in as_completed(futures):
                job = futures[future]
                try:
                    future.result()
                except Exception as e:
                    logger.error(f"❌ Failed in thread for job {job}: {e}", exc_info=True)

    except Exception as e:
        logger.critical(f"❌ Fatal error during job processing: {e}", exc_info=True)


if __name__ == "__main__":
    main()
