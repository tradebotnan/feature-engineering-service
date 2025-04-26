import pandas as pd
from app.labeler import label_trend


def test_label_trend():
    data = {
        'close': [100, 102, 101, 103, 105]
    }
    df = pd.DataFrame(data)
    labeled_df = label_trend(df)

    # Check that the trend_label column exists
    assert 'trend_label' in labeled_df.columns

    # Check that there are no missing labels
    assert labeled_df['trend_label'].isnull().sum() == 0

    # Optional: Check basic trend logic
    assert labeled_df.iloc[0]['trend_label'] == 1  # 102 > 100, should be uptrend
    assert labeled_df.iloc[2]['trend_label'] == 1  # 103 > 101, should be uptrend
