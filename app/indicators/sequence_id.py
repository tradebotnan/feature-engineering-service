# Source file: app\indicators\sequence_id.py
import pandas as pd


def add_sequence_id(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add sequential ID column for RL training.
    """
    df = df.copy()
    df["sequence_id"] = range(len(df))
    return df
