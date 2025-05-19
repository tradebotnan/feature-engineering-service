# Source file: app/enrichment/generate_enrichment_overlay.py

from pathlib import Path
import pandas as pd
import numpy as np
from common.env.env_loader import get_env_variable
from common.io.parquet_utils import read_parquet_to_df


def generate_enrichment_overlay(df: pd.DataFrame, market, asset, symbol: str) -> pd.DataFrame:
    reference_dir = Path(get_env_variable("BASE_DIR")).joinpath(get_env_variable("ENRICHMENT_DIR"))

    # df = enrich_with_dividends(df, reference_dir / "dividends" / market / asset / symbol / f"{symbol}_dividends.parquet")
    df = enrich_with_splits(df, reference_dir / "splits" / market / asset / symbol / f"{symbol}_splits.parquet")
    # df = enrich_with_events(df, reference_dir / "events" / market / asset / symbol / f"{symbol}_events.parquet")
    # df = enrich_with_fundamentals(df, reference_dir / "financials" / market / asset / symbol / f"{symbol}_financials.parquet")

    return df

from common.logging.logger import setup_logger

logger = setup_logger()

import os

def enrich_with_dividends(df, path):
    try:
        if not path.exists():
            logger.warning(f"⚠️ Dividend file not found at {path}. Skipping enrichment.")
            return df

        if path.suffix == ".parquet":
            dividends = read_parquet_to_df(path)
        else:
            dividends = pd.read_csv(path, parse_dates=["ex_dividend_date"])

        dividends = dividends.dropna(subset=["ex_dividend_date"])
        dividends["ex_date"] = pd.to_datetime(dividends["ex_dividend_date"]).dt.tz_localize("UTC").dt.date

        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")
        df["date"] = df["timestamp"].dt.tz_convert("America/New_York").dt.tz_localize(None).dt.date

        df["is_dividend_day"] = df["date"].isin(dividends["ex_date"]).astype(int)
        df = df.merge(dividends[["ex_date", "cash_amount"]], how="left", left_on="date", right_on="ex_date")
        df.rename(columns={"cash_amount": "dividend_amount"}, inplace=True)

        # Days since last dividend
        last_div = pd.Series(index=df.index, dtype=float)
        last_date = None
        for i, d in enumerate(df["date"]):
            if d in dividends["ex_date"].values:
                last_date = d
            last_div.iloc[i] = (d - last_date).days if last_date else float("nan")
        df["days_since_last_dividend"] = last_div

        # Days until next dividend
        next_div = pd.Series(index=df.index, dtype=float)
        next_dates = sorted(dividends["ex_date"].unique())
        j = 0
        for i, d in enumerate(df["date"]):
            while j < len(next_dates) and next_dates[j] < d:
                j += 1
            next_div.iloc[i] = (next_dates[j] - d).days if j < len(next_dates) else float("nan")
        df["next_dividend_in_X_days"] = next_div

        logger.info("✅ Dividend enrichment complete.")
        df = df.drop(columns=["date", "ex_date"])
        return df

    except Exception as e:
        logger.exception(f"❌ Failed to enrich with dividends from {path}: {e}")
        return df


def enrich_with_splits(df, path):
    if not path.exists():
        return df

    splits = pd.read_csv(path, parse_dates=["execution_date"])
    splits["split_date"] = splits["execution_date"].dt.date
    splits["split_ratio"] = splits["split_from"] / splits["split_to"]

    df["is_split_day"] = df["date"].isin(splits["split_date"]).astype(int)
    df = df.merge(splits[["split_date", "split_ratio"]], how="left", left_on="date", right_on="split_date")

    return df

def enrich_with_events(df, path):
    if not path.exists():
        return df

    events = pd.read_csv(path, parse_dates=["date"])
    events["event_date"] = events["date"].dt.date

    df["has_event"] = df["date"].isin(events["event_date"]).astype(int)
    df["has_ticker_change"] = df["date"].isin(events.loc[events["type"] == "ticker_change", "event_date"]).astype(int)
    df["has_merger_or_acquisition"] = df["date"].isin(events.loc[events["type"].isin(["merger", "acquisition"]), "event_date"]).astype(int)
    df["has_name_change"] = df["date"].isin(events.loc[events["type"] == "name_change", "event_date"]).astype(int)

    # Days since last event
    event_dates = sorted(events["event_date"].unique())
    last_event = pd.Series(index=df.index, dtype=float)
    last_date = None
    for i, d in enumerate(df["date"]):
        if d in event_dates:
            last_date = d
        last_event.iloc[i] = (d - last_date).days if last_date else np.nan
        df["days_since_last_event"] = last_event

    return df

def enrich_with_fundamentals(df, path):
    if not path.exists():
        return df

    fin = pd.read_csv(path, parse_dates=["end_date"])
    fin = fin.sort_values("end_date")
    fin["report_date"] = fin["end_date"].dt.date

    # Forward fill from last known fundamental
    df["pe_ratio"] = np.nan
    df["eps"] = np.nan
    df["dividend_yield"] = np.nan
    df["revenue_growth"] = np.nan
    df["has_fundamentals"] = 0
    df["fundamental_gap_days"] = np.nan
    df["has_reporting_lag"] = 0
    df["financials_stale_flag"] = 0

    last_row = None
    last_date = None
    for i, d in enumerate(df["date"]):
        valid_rows = fin[fin["report_date"] <= d]
        if not valid_rows.empty:
            latest = valid_rows.iloc[-1]
            df.at[i, "pe_ratio"] = latest.get("pe_ratio")
            df.at[i, "eps"] = latest.get("diluted_earnings_per_share", latest.get("basic_earnings_per_share"))
            df.at[i, "dividend_yield"] = latest.get("dividend_yield")
            df.at[i, "has_fundamentals"] = 1

            if last_row is not None:
                growth = (latest.get("revenues", 0) - last_row.get("revenues", 0)) / last_row.get("revenues", 1)
                df.at[i, "revenue_growth"] = growth
                df.at[i, "fundamental_gap_days"] = (latest["report_date"] - last_date).days
            last_row = latest
            last_date = latest["report_date"]

            # Reporting lag
            filed = latest.get("filed_date") or latest.get("filing_date")
            if filed:
                lag = (pd.to_datetime(filed).date() - latest["report_date"]).days
                df.at[i, "has_reporting_lag"] = 1 if lag > 30 else 0

            # Stale check
            stale_days = (d - latest["report_date"]).days
            df.at[i, "financials_stale_flag"] = 1 if stale_days > 90 else 0

    return df