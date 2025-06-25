# Source file: app\indicators\sequence_id.py

import pytest

pd = pytest.importorskip("pandas")

from app.indicators.sequence_id import add_sequence_id


def test_add_sequence_id():
    df = pd.DataFrame({"value": [10, 20, 30]})
    result = add_sequence_id(df)
    assert "sequence_id" in result.columns

