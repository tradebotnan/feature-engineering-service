from pathlib import Path
import pandas as pd

from app.utils.logger import get_logger
from app.preprocessing.data_preprocessor import preprocess_dataframe
from app.feature.generator import generate_features
from app.feature.labeler import apply_labeling_strategy
from app.feature.writer import write_features, update_feature_status
from app.utils.env_loader import get_env_variable, resolve_env_path

logger = get_logger("loader")


def load_and_process(file_path: Path, symbol: str, date: str, data_type: str, config: dict) -> bool:
    """
    Full pipeline for feature engineering:
    1. Load filtered Parquet
    2. Preprocess
    3. Generate features
    4. Apply labeling
    5. Save output
    6. Log success or failure in feature dispatch table
    """
    try:
        logger.info(f"🛠️ Starting feature generation for {file_path}")

        df = pd.read_parquet(file_path)
        df = preprocess_dataframe(df)
        df = generate_features(df, config)
        df = apply_labeling_strategy(df)

        if df.empty:
            raise ValueError("Generated feature DataFrame is empty.")

        input_base = Path(resolve_env_path("FEATURE_INPUT_PATH", "data/filtered"))
        output_base = Path(resolve_env_path("FEATURE_OUTPUT_PATH", "data/features"))

        relative_path = file_path.relative_to(input_base)
        output_path = output_base / relative_path
        output_path.parent.mkdir(parents=True, exist_ok=True)

        write_features(df, str(output_path))
        update_feature_status(symbol, date, data_type, "completed", output_path)
        logger.info(f"✅ Completed: {symbol} {date} saved to {output_path}")
        return True

    except Exception as e:
        logger.error(f"❌ Feature generation failed for {symbol} {date}: {e}")
        update_feature_status(symbol, date, data_type, "error", "", str(e))
        return False
