import pytest
from unittest.mock import patch, MagicMock
from app.db import dispatcher
from sqlalchemy.exc import SQLAlchemyError

@patch("app.db.dispatcher.get_db_session")
def test_fetch_pending_jobs_success(mock_get_db_session):
    mock_session = MagicMock()
    mock_job = MagicMock()
    mock_session.query().filter_by().limit().all.return_value = [mock_job] * 3
    mock_get_db_session.return_value = mock_session

    jobs = dispatcher.fetch_pending_jobs(limit=3)

    assert isinstance(jobs, list)
    assert len(jobs) == 3
    mock_session.close.assert_called_once()

@patch("app.db.dispatcher.get_db_session")
def test_fetch_pending_jobs_failure(mock_get_db_session):
    mock_session = MagicMock()
    mock_session.query().filter_by().limit().all.side_effect = SQLAlchemyError("Simulated DB failure")
    mock_get_db_session.return_value = mock_session

    jobs = dispatcher.fetch_pending_jobs(limit=3)

    assert jobs == []
    mock_session.close.assert_called_once()
