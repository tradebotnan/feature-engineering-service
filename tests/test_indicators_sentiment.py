import pandas as pd
from app.indicators import options, sentiment


def test_add_options_features():
    df = pd.DataFrame({
        "timestamp": pd.date_range(start="2024-01-01", periods=10, freq="D"),
        "open_interest": [100, 120, 130, 150, 140, 135, 125, 110, 115, 120],
        "put_call_ratio": [1.0, 0.9, 0.95, 1.1, 1.2, 1.05, 0.98, 0.96, 1.0, 1.1]
    })

    config = {
        "put_call_ratio": {"enabled": True},
        "open_interest_trend": {"periods": [3]}
    }

    result = options.add_options_features(df.copy(), config)

    assert "put_call_ratio" in result.columns
    assert "open_interest_trend_3" in result.columns
    assert result["open_interest_trend_3"].isnull().sum() < len(result)


def test_add_sentiment_features():
    df = pd.DataFrame({
        "timestamp": pd.date_range(start="2024-01-01", periods=10, freq="D"),
        "news_sentiment": [0.1, -0.2, 0.3, 0.0, 0.5, -0.1, 0.2, 0.4, 0.3, 0.0],
        "social_sentiment": [0.05, 0.1, -0.05, 0.0, 0.2, -0.1, 0.15, 0.1, 0.05, 0.0]
    })

    config = {
        "news_sentiment": {"enabled": True},
        "social_sentiment": {"enabled": True},
        "sentiment_trend": {"periods": [3]}
    }

    result = sentiment.add_sentiment_features(df.copy(), config)

    assert "news_sentiment" in result.columns
    assert "social_sentiment" in result.columns
    assert "sentiment_trend_3" in result.columns
    assert result["sentiment_trend_3"].isnull().sum() < len(result)
