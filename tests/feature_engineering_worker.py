import pytest
from unittest.mock import patch, MagicMock
from app.worker.feature_engineering_worker import process_job

@patch("app.worker.feature_engineering_worker.load_filtered_file")
@patch("app.worker.feature_engineering_worker.preprocess_dataframe")
@patch("app.worker.feature_engineering_worker.generate_features")
@patch("app.worker.feature_engineering_worker.label_features")
@patch("app.worker.feature_engineering_worker.write_features")
@patch("app.worker.feature_engineering_worker.update_feature_status")
def test_process_job_success(mock_update, mock_write, mock_label, mock_generate, mock_preprocess, mock_load):
    mock_job = MagicMock()
    mock_job.symbol = "AAPL"
    mock_job.date = "2024-01-01"
    mock_job.data_type = "day"
    mock_job.filtered_path = "tests/data/filtered/AAPL_day_2024-01-01.parquet"

    mock_load.return_value = "df"
    mock_preprocess.return_value = "df"
    mock_generate.return_value = "df"
    mock_label.return_value = "df"
    mock_write.return_value = True

    process_job(mock_job)
    mock_update.assert_called_with("AAPL", "2024-01-01", "day", "completed", path="tests/data/features/AAPL_day_2024-01-01.parquet")
