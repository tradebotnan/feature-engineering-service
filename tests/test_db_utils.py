import pytest
from app.db.utils import retry_on_failure
from sqlalchemy.exc import OperationalError

def test_retry_on_failure_success():
    call_count = {"count": 0}

    @retry_on_failure(retries=3)
    def sample():
        call_count["count"] += 1
        return "ok"

    assert sample() == "ok"
    assert call_count["count"] == 1

def test_retry_on_failure_fails():
    @retry_on_failure(retries=2, delay=0.1)
    def always_fail():
        raise OperationalError("SELECT 1", {}, None)

    with pytest.raises(OperationalError):
        always_fail()
