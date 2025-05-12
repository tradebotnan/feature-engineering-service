import pandas as pd

def add_fundamental_features(df, config):
    df = df.copy()
    for feature in config.get("include", []):
        df[feature] = 0.0
    return df