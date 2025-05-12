# Source file: app\indicators\fundamentals.py


def add_fundamental_features(df, config):
    df = df.copy()
    for feature in config.get("include", []):
        df[feature] = 0.0
    return df
