import pandas as pd
from app.utils.logger import get_logger

logger = get_logger("indicators_candles")


def add_body_size(df: pd.DataFrame) -> pd.DataFrame:
    df["body_size"] = (df["close"] - df["open"]).abs()
    return df


def add_wick_size(df: pd.DataFrame) -> pd.DataFrame:
    df["upper_wick"] = df["high"] - df[["close", "open"]].max(axis=1)
    df["lower_wick"] = df[["close", "open"]].min(axis=1) - df["low"]
    df["wick_size"] = df["upper_wick"] + df["lower_wick"]
    return df


def add_gap_up_down(df: pd.DataFrame) -> pd.DataFrame:
    df["gap_up"] = df["open"] > df["close"].shift(1)
    df["gap_down"] = df["open"] < df["close"].shift(1)
    return df


def add_doji(df: pd.DataFrame, threshold: float = 0.1) -> pd.DataFrame:
    body = (df["close"] - df["open"]).abs()
    range_ = df["high"] - df["low"]
    df["pattern_doji"] = (body / range_ < threshold).astype(int)
    return df


def add_engulfing(df: pd.DataFrame) -> pd.DataFrame:
    prev_open = df["open"].shift(1)
    prev_close = df["close"].shift(1)
    curr_open = df["open"]
    curr_close = df["close"]

    cond_bull = (prev_close < prev_open) & (curr_close > curr_open) & (curr_close > prev_open) & (curr_open < prev_close)
    cond_bear = (prev_close > prev_open) & (curr_close < curr_open) & (curr_close < prev_open) & (curr_open > prev_close)

    df["pattern_engulfing"] = (cond_bull | cond_bear).astype(int)
    return df


def add_candlestick_features(df: pd.DataFrame, config: dict) -> pd.DataFrame:
    if "engineered" in config:
        feats = config["engineered"].get("include", [])
        if "body_size" in feats:
            df = add_body_size(df)
        if "wick_size" in feats:
            df = add_wick_size(df)
        if "gap_up" in feats or "gap_down" in feats:
            df = add_gap_up_down(df)

    if config.get("patterns", {}).get("enabled", False):
        df = add_doji(df)
        df = add_engulfing(df)

    return df


def add_gap_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["gap_up"] = (df["open"] > df["high"].shift(1)).astype(int)
    df["gap_down"] = (df["open"] < df["low"].shift(1)).astype(int)
    return df


def detect_candlestick_patterns(df: pd.DataFrame, patterns: list[str]) -> pd.DataFrame:
    df = df.copy()

    for pattern in patterns:
        if pattern.lower() == "doji":
            body = (df["close"] - df["open"]).abs()
            range_ = df["high"] - df["low"]
            df["pattern_doji"] = (body / range_ < 0.1).astype(int)

        elif pattern.lower() == "engulfing":
            prev = df.shift(1)
            cond_bull = (prev["close"] < prev["open"]) & (df["close"] > df["open"]) & (df["open"] < prev["close"]) & (
                        df["close"] > prev["open"])
            cond_bear = (prev["close"] > prev["open"]) & (df["close"] < df["open"]) & (df["open"] > prev["close"]) & (
                        df["close"] < prev["open"])
            df["pattern_engulfing"] = (cond_bull | cond_bear).astype(int)

        else:
            logger.warning(f"Pattern '{pattern}' not supported.")

    return df
