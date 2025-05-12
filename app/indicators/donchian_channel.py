import pandas as pd

def add_donchian_channel(df, config):
    df = df.copy()
    period = config.get("periods", [20])[0]
    df["donchian_high"] = df["high"].rolling(window=period).max()
    df["donchian_low"] = df["low"].rolling(window=period).min()
    return df