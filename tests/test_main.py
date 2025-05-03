import pytest
import argparse
from unittest.mock import patch
from app import main

@patch("builtins.print")
@patch("argparse.ArgumentParser.parse_args")
@patch("app.main.load_filtered_file")
@patch("app.main.preprocess_dataframe")
@patch("app.main.generate_features")
@patch("app.main.label_features")
@patch("app.main.write_features")
def test_main_cli_flow(mock_write, mock_label, mock_generate, mock_preprocess, mock_load, mock_parse_args, mock_print):
    mock_parse_args.return_value = argparse.Namespace(
        input_dir="tests/data/filtered",
        output_dir="tests/data/features",
        symbols="AAPL",
        start_date="2024-01-01",
        end_date="2024-01-01",
        data_type="day"
    )

    mock_load.return_value = "raw_df"
    mock_preprocess.return_value = "pre_df"
    mock_generate.return_value = "feat_df"
    mock_label.return_value = "labeled_df"
    mock_write.return_value = True

    main.main()
    mock_write.assert_called_once()