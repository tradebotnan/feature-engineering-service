import pandas as pd
from ta.momentum import RSIIndicator, ROCIndicator, StochasticOscillator

def add_momentum_features(df: pd.DataFrame, config: dict) -> pd.DataFrame:
    """
    Adds momentum indicators like RSI, ROC, Stochastic Oscillator, etc.
    Expected config format:
    {
        "rsi": {"periods": [5, 14]},
        "roc": {"periods": [5]},
        "stochastic": {"periods": [5]}
    }
    """
    if "rsi" in config:
        for period in config["rsi"].get("periods", []):
            df[f"rsi_{period}"] = RSIIndicator(df["close"], window=period).rsi()

    if "roc" in config:
        for period in config["roc"].get("periods", []):
            df[f"roc_{period}"] = ROCIndicator(df["close"], window=period).roc()

    if "stochastic" in config:
        for period in config["stochastic"].get("periods", []):
            so = StochasticOscillator(
                high=df["high"], low=df["low"], close=df["close"], window=period
            )
            df[f"stoch_k_{period}"] = so.stoch()
            df[f"stoch_d_{period}"] = so.stoch_signal()

    return df
