# Source file: app\indicators\accumulation_distribution.py


def add_accumulation_distribution(df, config):
    df = df.copy()
    clv = ((df["close"] - df["low"]) - (df["high"] - df["close"])) / (df["high"] - df["low"]).replace(0, 1)
    df["ad"] = clv * df["volume"]
    df["accum_dist"] = df["ad"].cumsum()
    return df
