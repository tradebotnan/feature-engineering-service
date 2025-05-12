# Source file: app\indicators\event_flags.py


def add_event_flags(df, config):
    df = df.copy()
    for event_type in config.get("types", []):
        df[f"event_{event_type}"] = 0
    return df
