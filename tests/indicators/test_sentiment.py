# Source file: app\indicators\sentiment.py

import pytest

pd = pytest.importorskip("pandas")

from app.indicators.sentiment import add_sentiment_features


def test_add_sentiment_features():
    df = pd.DataFrame({"close": [1, 2, 3]})
    cfg = {"include_mock_sentiment": True}
    result = add_sentiment_features(df, cfg)
    assert "sentiment_score" in result.columns

