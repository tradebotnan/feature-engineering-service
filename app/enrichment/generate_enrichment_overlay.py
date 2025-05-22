# Source file: app/enrichment/generate_enrichment_overlay.py

from pathlib import Path

import numpy as np
import pandas as pd
from common.env.env_loader import get_env_variable
from common.io.parquet_utils import read_parquet_to_df
from common.logging.logger import setup_logger

logger = setup_logger()


def generate_enrichment_overlay(df: pd.DataFrame, market, asset, symbol: str) -> pd.DataFrame:
    try:
        preserved_attrs = df.attrs.copy()
        base_dir = Path(get_env_variable("BASE_DIR")) / get_env_variable("ENRICHMENT_DIR")
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")
        df["date"] = df["timestamp"].dt.date

        df = enrich_with_dividends(df, base_dir / "dividends" / market / asset / symbol / f"{symbol}_dividends.parquet")
        df = enrich_with_splits(df, base_dir / "splits" / market / asset / symbol / f"{symbol}_splits.parquet")
        df = enrich_with_events(df, base_dir / "events" / market / asset / symbol / f"{symbol}_events.parquet")
        df = enrich_with_fundamentals(df,
                                      base_dir / "financials" / market / asset / symbol / f"{symbol}_financials.parquet")

        df.attrs.update(preserved_attrs)
        return df

    except Exception as e:
        logger.error(f"❌ Enrichment failed for {symbol}: {e}", exc_info=True)
        logger.error("Traceback:", exc_info=True)
        raise


def enrich_with_dividends(df: pd.DataFrame, path: Path) -> pd.DataFrame:
    if not path.exists():
        logger.warning(f"⚠️ Dividend file missing: {path}")
        return df

    try:
        dividends = read_parquet_to_df(path)
        dividends["ex_date"] = pd.to_datetime(dividends["ex_dividend_date"]).dt.date
        df["is_dividend_day"] = df["date"].isin(dividends["ex_date"]).astype(int)

        df = df.merge(dividends[["ex_date", "cash_amount"]], how="left", left_on="date", right_on="ex_date")
        df.rename(columns={"cash_amount": "dividend_amount"}, inplace=True)
        df.drop(columns=["ex_date"], inplace=True)

        df["days_since_last_dividend"] = calculate_days_since(df["date"], df["is_dividend_day"])
        df["next_dividend_in_X_days"] = calculate_days_until(df["date"], dividends["ex_date"].unique())

        logger.info("✅ Dividend enrichment applied.")
        return df
    except Exception as e:
        logger.exception(f"❌ Failed to enrich dividends from {path}: {e}")
        return df


def enrich_with_splits(df: pd.DataFrame, path: Path) -> pd.DataFrame:
    if not path.exists():
        logger.warning(f"⚠️ Splits file missing: {path}")
        return df

    try:
        splits = read_parquet_to_df(path)
        splits["execution_date"] = pd.to_datetime(splits["execution_date"]).dt.date
        df["is_split_day"] = df["date"].isin(splits["execution_date"]).astype(int)

        df = df.merge(splits[["execution_date", "split_ratio"]],
                      how="left", left_on="date", right_on="execution_date")
        df.drop(columns=["execution_date"], inplace=True)
        return df
    except Exception as e:
        logger.exception(f"❌ Failed to enrich splits from {path}: {e}")
        return df


def enrich_with_events(df: pd.DataFrame, path: Path) -> pd.DataFrame:
    if not path.exists():
        logger.warning(f"⚠️ Events file missing: {path}")
        return df

    try:
        events = read_parquet_to_df(path)
        events["event_date"] = pd.to_datetime(events["date"]).dt.date

        df["has_event"] = df["date"].isin(events["event_date"]).astype(int)
        df["has_ticker_change"] = df["date"].isin(events.query("type == 'ticker_change'")["event_date"]).astype(int)
        df["has_merger_or_acquisition"] = df["date"].isin(
            events.query("type in ['merger', 'acquisition']")["event_date"]).astype(int)
        df["has_name_change"] = df["date"].isin(events.query("type == 'name_change'")["event_date"]).astype(int)

        df["days_since_last_event"] = calculate_days_since(df["date"], df["has_event"])
        return df
    except Exception as e:
        logger.exception(f"❌ Failed to enrich events from {path}: {e}")
        return df


def enrich_with_fundamentals(df: pd.DataFrame, path: Path) -> pd.DataFrame:
    if not path.exists():
        logger.warning(f"⚠️ Fundamentals file missing: {path}")
        return df

    try:
        fin = read_parquet_to_df(path).sort_values("end_date")
        fin["report_date"] = pd.to_datetime(fin["end_date"], errors="coerce").dt.date

        df["pe_ratio"] = np.nan
        df["eps"] = np.nan
        df["dividend_yield"] = np.nan
        df["revenue_growth"] = np.nan
        df["has_fundamentals"] = 0
        df["fundamental_gap_days"] = np.nan
        df["has_reporting_lag"] = 0
        df["financials_stale_flag"] = 0

        last_row = None
        last_report_date = None

        for i, d in enumerate(df["date"]):
            snapshot = fin[fin["report_date"] <= d]
            if snapshot.empty:
                continue

            latest = snapshot.iloc[-1]
            eps = latest.get("diluted_earnings_per_share") or latest.get("basic_earnings_per_share")
            price = df.at[i, "close"]

            df.at[i, "eps"] = eps
            # Ensure price and eps are numeric before division
            if (pd.notnull(price)
                    and pd.notnull(eps)
                    and isinstance(price, (int, float, np.number))
                    and isinstance(eps,(int,float,np.number)) and eps != 0):
                df.at[i, "pe_ratio"] = price / eps
            else:
                df.at[i, "pe_ratio"] = np.nan

            if last_row is not None and last_report_date:
                try:
                    prev_revenue = last_row.get("revenues", 1)
                    growth = (latest.get("revenues", 0) - prev_revenue) / prev_revenue
                    df.at[i, "revenue_growth"] = growth
                    df.at[i, "fundamental_gap_days"] = (latest["report_date"] - last_report_date).days
                except Exception as e:
                    logger.warning(f"⚠️ Revenue growth calc failed at {d}: {e}")

            last_row = latest
            last_report_date = latest["report_date"]

            filed_date = pd.to_datetime(latest.get("filed_date") or latest.get("filing_date"), errors="coerce")
            if pd.notnull(filed_date):
                lag_days = (filed_date.date() - latest["report_date"]).days
                df.at[i, "has_reporting_lag"] = int(lag_days > 30)

            stale_days = (d - latest["report_date"]).days
            df.at[i, "financials_stale_flag"] = int(stale_days > 90)
            df.at[i, "has_fundamentals"] = 1

        logger.info("✅ Fundamentals enrichment applied.")
        return df

    except Exception as e:
        logger.exception(f"❌ Failed to enrich fundamentals from {path}: {e}")
        return df


def calculate_days_since(dates, indicator_series):
    last_date = None
    days_since = []
    for flag, current in zip(indicator_series, dates):
        if flag:
            last_date = current
        days_since.append((current - last_date).days if last_date else np.nan)
    return days_since


def calculate_days_until(dates, future_dates):
    future_dates = sorted(set(future_dates))
    j = 0
    days_until = []
    for d in dates:
        while j < len(future_dates) and future_dates[j] < d:
            j += 1
        days_until.append((future_dates[j] - d).days if j < len(future_dates) else np.nan)
    return days_until
