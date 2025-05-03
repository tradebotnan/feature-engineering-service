import pytest
from sqlalchemy.exc import OperationalError
from app.db.connector import get_db_session

def test_get_db_session_success():
    session = get_db_session()
    assert session is not None
    assert hasattr(session, "execute")

def test_get_db_session_failure(monkeypatch):
    from app.db import connector

    def fail_settings():
        raise Exception("forced error")

    monkeypatch.setattr(connector, "get_db_settings", fail_settings)
    connector.engine = None
    connector.Session = None

    with pytest.raises(Exception, match="forced error"):
        connector.get_db_session()
