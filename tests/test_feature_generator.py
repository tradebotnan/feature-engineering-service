import pandas as pd
from app.feature_generator import generate_features

def test_generate_features():
    data = {
        'close': [100 + i for i in range(20)]  # Generate 20 increasing prices
    }
    df = pd.DataFrame(data)
    df = generate_features(df)

    assert 'rsi_14' in df.columns
    assert 'ema_10' in df.columns
    assert 'macd' in df.columns

    # There will be NaN values at the beginning, but after 14 rows, RSI should be valid
    valid_rsi = df['rsi_14'].dropna()
    assert not valid_rsi.empty
    assert valid_rsi.iloc[0] >= 0  # RSI is between 0-100
