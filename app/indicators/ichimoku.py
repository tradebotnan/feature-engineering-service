# Source file: app\indicators\ichimoku.py


def add_ichimoku_features(df, config):
    df = df.copy()
    high_9 = df["high"].rolling(window=9).max()
    low_9 = df["low"].rolling(window=9).min()
    high_26 = df["high"].rolling(window=26).max()
    low_26 = df["low"].rolling(window=26).min()
    high_52 = df["high"].rolling(window=52).max()
    low_52 = df["low"].rolling(window=52).min()

    df["tenkan_sen"] = (high_9 + low_9) / 2
    df["kijun_sen"] = (high_26 + low_26) / 2
    df["senkou_span_a"] = ((df["tenkan_sen"] + df["kijun_sen"]) / 2).shift(26)
    df["senkou_span_b"] = ((high_52 + low_52) / 2).shift(26)
    df["chikou_span"] = df["close"].shift(-26)
    return df
