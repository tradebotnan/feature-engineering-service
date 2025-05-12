# app/indicators/sentiment.py

import pandas as pd
import numpy as np

def add_sentiment_features(df: pd.DataFrame, config: dict) -> pd.DataFrame:
    """
    Adds mock sentiment signals. In production, replace with NLP + news/sentiment pipelines.
    """
    df = df.copy()

    if config.get("include_mock_sentiment", False):
        np.random.seed(42)
        df["sentiment_score"] = np.random.uniform(-1, 1, len(df))
        df["sentiment_positive"] = (df["sentiment_score"] > 0).astype(int)
        df["sentiment_negative"] = (df["sentiment_score"] < 0).astype(int)

    if "sentiment_trend" in config:
        periods = config["sentiment_trend"].get("periods", [])
        for period in periods:
            col_name = f"sentiment_trend_{period}"
            df[col_name] = df["sentiment_score"].rolling(window=period).mean()

    return df
