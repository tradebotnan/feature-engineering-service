# Source file: app/feature/loader.py

from pathlib import Path

import pandas as pd
from common.config.yaml_loader import load_market_config
from common.env.env_loader import get_env_variable
from common.io.parquet_utils import read_parquet_to_df
from common.io.path_resolver import resolve_feature_output_path, get_group_key_from_filename
from common.logging.logger import setup_logger
from common.schema.enums import MarketType, AssetType, DataType
from common.utils.retry_utils import retry

from app.enrichment.generate_enrichment_overlay import generate_enrichment_overlay
from app.feature.writer import write_features, update_feature_status
from app.utils.file_stitcher import stitch_with_previous_and_next
from feature.generator import generate_features
from feature.labeler import apply_labeling_strategy
from preprocessing.data_preprocessor import preprocess_dataframe

logger = setup_logger()


@retry(Exception, tries=3, delay=2, backoff=2)
def load_and_process(market, asset, data, symbol, date, file_path, row_id, all_files=None) -> pd.DataFrame:
    """
    Full pipeline for feature engineering.
    If all_files is provided, stitch previous file rows for continuity.
    """
    try:
        logger.info(f"🛠️ Starting feature generation for {file_path}")

        df = read_parquet_to_df(file_path)
        # Ensure the 'timestamp' column is in datetime format
        # logger.info(
        #     f"Before conversion, 'timestamp' column format: {df['timestamp'].head()}, dtype: {df['timestamp'].dtype}")
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ns", utc=True, errors="coerce")

        df = df.sort_values("timestamp").reset_index(drop=True)

        # ✅ Optional: Stitch previous file (only if all_files provided)
        if all_files:
            df = stitch_with_previous_and_next(df, Path(file_path), all_files, data_type=data)

        # ✅ Clean + technical preparation
        df = generate_enrichment_overlay(df, market, asset, symbol)
        df = preprocess_dataframe(df)
        df = generate_features(df, load_market_config(market, asset), data)
        df = apply_labeling_strategy(df, load_market_config(market, asset))

        # ✅ NEW BLOCK
        if hasattr(df, "attrs") and "current_file_min_ts" in df.attrs:
            min_ts = pd.to_datetime(df.attrs["current_file_min_ts"], utc=True)
            max_ts = pd.to_datetime(df.attrs["current_file_max_ts"], utc=True)

            original_count = len(df)

            # Ensure the 'timestamp' column is in datetime format
            df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")

            # Drop rows with invalid timestamps
            df = df.dropna(subset=["timestamp"]).reset_index(drop=True)

            # Validate min_ts and max_ts
            if min_ts > max_ts:
                raise ValueError(f"Invalid range: min_ts ({min_ts}) is greater than max_ts ({max_ts})")

            # Filter rows within the range
            df = df[(df["timestamp"] >= min_ts) & (df["timestamp"] <= max_ts)].reset_index(drop=True)
            trimmed_count = original_count - len(df)

            logger.info(
                f"✅ Trimmed stitched file to original time range ({min_ts} → {max_ts}), removed {trimmed_count} buffer rows.")

        if df.empty:
            raise ValueError("Generated feature DataFrame is empty.")

        # ✅ Output path resolution
        output_path = resolve_feature_output_path(
            MarketType(market), AssetType(asset), DataType(data),
            symbol, get_group_key_from_filename(Path(file_path).stem)
        )

        parquet_path = Path(str(output_path) + ".parquet")
        parquet_path.parent.mkdir(parents=True, exist_ok=True)

        write_features(df, str(parquet_path))

        relative_output_path = str(parquet_path).replace(
            str(Path(get_env_variable("BASE_DIR")).resolve()), ""
        )
        if date in [None, "None", ""]:
            date = None
        elif isinstance(date, str):
            date = pd.to_datetime(date).date()

        update_feature_status(row_id=row_id, status="completed", path=relative_output_path)

        logger.info(f"✅ Completed: {symbol} {date} saved to {parquet_path}")
        return df

    except Exception as e:
        logger.error(f"❌ Feature generation failed for {symbol} {date}: {e}")
        logger.error("Traceback:", exc_info=True)
        update_feature_status(symbol=symbol, date=date, data=data,
                              status="error", error_message=str(e))
        return df
