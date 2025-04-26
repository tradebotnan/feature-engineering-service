import pandas as pd
from app.preprocessor import clean_data

def test_clean_data():
    data = {
        'timestamp': [3, 1, 2],
        'close': [100, None, 102]
    }
    df = pd.DataFrame(data)
    cleaned_df = clean_data(df)
    assert cleaned_df.isnull().sum().sum() == 0
    assert cleaned_df.iloc[0]['timestamp'] == 2
