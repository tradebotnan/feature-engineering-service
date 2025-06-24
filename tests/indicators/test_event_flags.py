# Source file: app\indicators\event_flags.py

import pytest

pd = pytest.importorskip("pandas")

from app.indicators.event_flags import add_event_flags


def test_add_event_flags():
    df = pd.DataFrame({"open": [1, 2, 3]})
    cfg = {"types": ["earnings"]}
    result = add_event_flags(df, cfg)
    assert "event_earnings" in result.columns

