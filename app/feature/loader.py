from pathlib import Path

import pandas as pd
from common.config.yaml_loader import load_market_config
from common.io.path_resolver import resolve_feature_output_path, get_group_key_from_filename
from common.logging.logger import setup_logger
from common.schema.enums import MarketType, AssetType, DataType
from common.utils.retry_utils import retry

from app.feature.generator import generate_features
from app.feature.labeler import apply_labeling_strategy
from app.feature.writer import write_features, update_feature_status
from app.preprocessing.data_preprocessor import preprocess_dataframe

logger = setup_logger()


@retry(Exception, tries=3, delay=2, backoff=2)
def load_and_process(market, asset, data, symbol, date, file_path, row_id) -> pd.DataFrame:
    """
    Full pipeline for feature engineering:
    """
    try:
        logger.info(f"🛠️ Starting feature generation for {file_path}")

        df = pd.read_parquet(file_path)
        df = preprocess_dataframe(df)
        df = generate_features(df, load_market_config(market, asset), data)
        df = apply_labeling_strategy(df, load_market_config(market, asset))

        if df.empty:
            raise ValueError("Generated feature DataFrame is empty.")

        input_base = file_path

        output_path = resolve_feature_output_path(MarketType(market), AssetType(asset), DataType(data), symbol,
                                                  get_group_key_from_filename(Path(file_path).stem))

        parquet_path = Path(str(output_path) + ".parquet")

        parquet_path.parent.mkdir(parents=True, exist_ok=True)
        parquet_path = Path(str(output_path) + ".parquet")

        write_features(df, str(parquet_path))
        update_feature_status(row_id=row_id, status="completed", path=str(parquet_path))

        logger.info(f"✅ Completed: {symbol} {date} saved to {parquet_path}")
        return df

    except Exception as e:
        logger.error(f"❌ Feature generation failed for {symbol} {date}: {e}")
        update_feature_status(symbol=symbol, date=date, data=data,
                              status="error", error_message=str(e))
        return df
