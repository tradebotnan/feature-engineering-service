import pandas as pd

def add_cross_features(df, config):
    df = df.copy()
    for pair in config.get("include", []):
        fast, slow = pair.split("_vs_")
        if fast in df.columns and slow in df.columns:
            col_name = f"cross_{fast}_{slow}"
            df[col_name] = (df[fast] > df[slow]).astype(int)
    return df