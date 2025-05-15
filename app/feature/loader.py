# Source file: app/feature/loader.py

from pathlib import Path
import pandas as pd

from common.config.yaml_loader import load_market_config
from common.env.env_loader import get_env_variable
from common.io.path_resolver import resolve_feature_output_path, get_group_key_from_filename
from common.logging.logger import setup_logger
from common.schema.enums import MarketType, AssetType, DataType
from common.utils.retry_utils import retry

from app.feature.generator import generate_features
from app.feature.labeler import apply_labeling_strategy
from app.feature.writer import write_features, update_feature_status
from app.preprocessing.data_preprocessor import preprocess_dataframe

# ✅ NEW: import stitcher
from app.utils.file_stitcher import stitch_with_previous

logger = setup_logger()

@retry(Exception, tries=3, delay=2, backoff=2)
def load_and_process(market, asset, data, symbol, date, file_path, row_id, all_files=None) -> pd.DataFrame:
    """
    Full pipeline for feature engineering.
    If all_files is provided, stitch previous file rows for continuity.
    """
    try:
        logger.info(f"🛠️ Starting feature generation for {file_path}")

        df = pd.read_parquet(file_path)
        df = df.sort_values("timestamp").reset_index(drop=True)

        # ✅ Optional: Stitch previous file (only if all_files provided)
        if all_files:
            df = stitch_with_previous(df, Path(file_path), all_files, data_type=data)

        df = preprocess_dataframe(df)
        df = generate_features(df, load_market_config(market, asset), data)
        df = apply_labeling_strategy(df, load_market_config(market, asset))

        if df.empty:
            raise ValueError("Generated feature DataFrame is empty.")

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

        update_feature_status(row_id=row_id, status="completed", path=relative_output_path)

        logger.info(f"✅ Completed: {symbol} {date} saved to {parquet_path}")
        return df

    except Exception as e:
        logger.error(f"❌ Feature generation failed for {symbol} {date}: {e}")
        update_feature_status(symbol=symbol, date=date, data=data,
                              status="error", error_message=str(e))
        return df
