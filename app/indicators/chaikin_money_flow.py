# Source file: app\indicators\chaikin_money_flow.py


def add_chaikin_money_flow(df, config):
    df = df.copy()
    period = config.get("periods", [20])[0]
    mf_multiplier = ((df["close"] - df["low"]) - (df["high"] - df["close"])) / (df["high"] - df["low"]).replace(0, 1)
    mf_volume = mf_multiplier * df["volume"]
    df["cmf"] = mf_volume.rolling(window=period).sum() / df["volume"].rolling(window=period).sum()
    return df
