# app/indicators/chaikin_money_flow.py

import pandas as pd
import numpy as np

def add_chaikin_money_flow(df: pd.DataFrame, config: dict) -> pd.DataFrame:
    """
    Adds Chaikin Money Flow (CMF) indicator to the dataframe.
    """
    df = df.copy()
    periods = config.get("periods", [])

    for period in periods:
        mfv = ((df["close"] - df["low"]) - (df["high"] - df["close"])) / (df["high"] - df["low"])
        mfv = mfv.replace([np.inf, -np.inf], 0).fillna(0)
        mfv *= df["volume"]
        cmf = mfv.rolling(window=period).sum() / df["volume"].rolling(window=period).sum()
        df[f"cmf_{period}"] = cmf

    return df
