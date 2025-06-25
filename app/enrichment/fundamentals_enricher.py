# Source file: app/enrichment/fundamentals_enricher.py

from pathlib import Path

import numpy as np
import pandas as pd
from common.io.parquet_utils import read_parquet_to_df
from common.logging.logger import setup_logger

logger = setup_logger()


def enrich_with_fundamentals(df: pd.DataFrame, path: Path) -> pd.DataFrame:
    if not path.exists():
        logger.warning(f"⚠️ Fundamentals file missing: {path}")
        initialize_fundamental_columns(df)
        return df

    try:
        fin = read_parquet_to_df(path).sort_values("end_date")
        fin["report_date"] = pd.to_datetime(fin["end_date"], errors="coerce").dt.date
        initialize_fundamental_columns(df)

        last_row = None
        last_report_date = None

        for i, d in enumerate(df["date"]):
            snapshot = fin[fin["report_date"] <= d]
            if snapshot.empty:
                continue

            latest = snapshot.iloc[-1]
            enrich_row(df, i, d, latest, last_row, last_report_date)
            last_row = latest
            last_report_date = latest["report_date"]

        logger.info("✅ Fundamentals enrichment applied.")
        return df

    except Exception as e:
        logger.exception(f"❌ Failed to enrich fundamentals from {path}: {e}")
        return df


def initialize_fundamental_columns(df: pd.DataFrame):
    df["pe_ratio"] = np.nan
    df["eps"] = np.nan
    df["dividend_yield"] = np.nan
    df["revenue_growth"] = np.nan
    df["has_fundamentals"] = 0
    df["fundamental_gap_days"] = np.nan
    df["has_reporting_lag"] = 0
    df["financials_stale_flag"] = 0
    df["event_earnings"] = 0
    df["days_since_earnings"] = np.nan
    df["earnings_surprise"] = np.nan


def enrich_row(df, i, d, latest, last_row, last_report_date):
    eps = latest.get("diluted_earnings_per_share") or latest.get("basic_earnings_per_share")
    price = df.at[i, "close"]
    df.at[i, "eps"] = eps
    if pd.notnull(price) and pd.notnull(eps) and eps != 0:
        df.at[i, "pe_ratio"] = price / eps

    if last_row is not None and last_report_date:
        try:
            prev_revenue = last_row.get("revenues", 1)
            growth = (latest.get("revenues", 0) - prev_revenue) / prev_revenue
            df.at[i, "revenue_growth"] = growth
            df.at[i, "fundamental_gap_days"] = (latest["report_date"] - last_report_date).days
        except Exception as e:
            logger.warning(f"⚠️ Revenue growth calc failed at {d}: {e}")

    enrich_dividend_yield(df, i, latest, price)
    enrich_reporting_flags(df, i, d, latest)
    enrich_earnings_flags(df, i, d, latest, last_row, eps)


def enrich_dividend_yield(df, i, latest, price):
    div_per_share = latest.get("common_stock_dividends", np.nan)
    if pd.notnull(div_per_share) and price:
        annualized_div = div_per_share * 4
        df.at[i, "dividend_yield"] = annualized_div / price


def enrich_reporting_flags(df, i, d, latest):
    filed_date = pd.to_datetime(latest.get("filed_date") or latest.get("filing_date"), errors="coerce")
    if pd.notnull(filed_date):
        lag_days = (filed_date.date() - latest["report_date"]).days
        df.at[i, "has_reporting_lag"] = int(lag_days > 30)

    stale_days = (d - latest["report_date"]).days
    df.at[i, "financials_stale_flag"] = int(stale_days > 90)
    df.at[i, "has_fundamentals"] = 1


def enrich_earnings_flags(df, i, d, latest, last_row, eps):
    if latest["report_date"] == d:
        df.at[i, "event_earnings"] = 1
        logger.debug(f"📅 Earnings event on {d} for symbol: {df.at[i, 'symbol']}")

    df.at[i, "days_since_earnings"] = (d - latest["report_date"]).days

    if last_row is not None:
        last_eps_val = last_row.get("diluted_earnings_per_share") or last_row.get("basic_earnings_per_share")
        if last_eps_val and last_eps_val != 0 and eps is not None:
            surprise = (eps - last_eps_val) / abs(last_eps_val)
            df.at[i, "earnings_surprise"] = surprise
