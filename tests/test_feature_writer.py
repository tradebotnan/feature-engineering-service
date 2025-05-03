import pandas as pd
from unittest.mock import patch, MagicMock
from app.feature import writer

def test_write_features_success(tmp_path):
    df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
    output_path = tmp_path / "features.parquet"

    result = writer.write_features(df, str(output_path))
    assert result is True
    assert output_path.exists()

def test_write_features_failure(monkeypatch):
    def fail_to_parquet(*args, **kwargs):
        raise Exception("write failed")

    monkeypatch.setattr(pd.DataFrame, "to_parquet", fail_to_parquet)
    result = writer.write_features(pd.DataFrame(), "dummy/path/output.parquet")
    assert result is False

@patch("app.feature.writer.get_db_session")
@patch("app.feature.writer.FeatureDispatchLog")
def test_update_feature_status_by_id(mock_model, mock_get_db_session):
    mock_session = MagicMock()
    mock_obj = MagicMock()
    mock_get_db_session.return_value = mock_session
    mock_session.query().filter_by().first.return_value = mock_obj

    writer.update_feature_status(row_id=1, status="completed", path="/new/path", error_message=None)
    assert mock_obj.error_message is None

    assert mock_obj.status == "completed"
    assert mock_obj.feature_path == "/new/path"
    assert mock_obj.error_message is None
    assert mock_session.commit.called

@patch("app.feature.writer.get_db_session")
def test_update_feature_status_not_found(mock_get_db_session):
    mock_session = MagicMock()
    mock_session.query().filter_by().first.return_value = None
    mock_get_db_session.return_value = mock_session

    writer.update_feature_status(symbol="AAPL", date="2024-03-01", data_type="minute")
    assert mock_session.commit.called is False  # should never reach commit
