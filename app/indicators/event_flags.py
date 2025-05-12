# app/indicators/event_flags.py

import pandas as pd

def add_event_flags(df: pd.DataFrame, config: dict) -> pd.DataFrame:
    """
    Adds event flags for corporate actions.
    These are mock/dummy placeholders. In production you would map from real corporate action calendars.
    """
    df = df.copy()
    types = config.get("types", [])

    for event_type in types:
        if event_type == "earnings":
            # Simulate random earnings events for demonstration
            df["event_earnings"] = 0
            df.loc[df.index[::50], "event_earnings"] = 1  # every 50th row
        elif event_type == "dividend":
            df["event_dividend"] = 0
            df.loc[df.index[::75], "event_dividend"] = 1  # every 75th row
        elif event_type == "splits":
            df["event_splits"] = 0
            df.loc[df.index[::100], "event_splits"] = 1  # every 100th row

    return df
