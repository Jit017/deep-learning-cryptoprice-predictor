import sys
from pathlib import Path
from typing import Tuple

import pandas as pd
import yfinance as yf


DATA_DIR = Path(__file__).resolve().parent


def fetch_usd_inr_daily() -> pd.DataFrame:
    fx = yf.download(
        tickers="USDINR=X",
        period="max",
        interval="1d",
        auto_adjust=False,
        threads=True,
        progress=False,
    )
    if fx is None or fx.empty:
        raise RuntimeError("No USD/INR daily data returned from yfinance")
    fx = fx.reset_index()
    # Normalize columns
    if isinstance(fx.columns, pd.MultiIndex):
        fx.columns = fx.columns.get_level_values(0)
    fx = fx[["Date", "Close"]].rename(columns={"Close": "USDINR"})
    fx["Date"] = pd.to_datetime(fx["Date"]).dt.date
    return fx


def fetch_usd_inr_hourly() -> pd.DataFrame:
    fx = yf.download(
        tickers="USDINR=X",
        period="2y",
        interval="1h",
        auto_adjust=False,
        threads=True,
        progress=False,
    )
    if fx is None or fx.empty:
        raise RuntimeError("No USD/INR hourly data returned from yfinance")
    fx = fx.reset_index()
    if isinstance(fx.columns, pd.MultiIndex):
        fx.columns = fx.columns.get_level_values(0)
    fx = fx[["Datetime", "Close"]].rename(columns={"Close": "USDINR"})
    # Ensure timezone-aware
    fx["Datetime"] = pd.to_datetime(fx["Datetime"], utc=True)
    return fx


essential_cols = ["Open", "High", "Low", "Close"]


def convert_daily_usd_to_inr(input_csv: Path, output_csv: Path) -> Tuple[int, int]:
    df = pd.read_csv(input_csv)
    # Coerce numeric
    for c in essential_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    # Prepare Date
    if "Date" not in df.columns:
        raise ValueError(f"Expected 'Date' column in {input_csv}")
    df["Date"] = pd.to_datetime(df["Date"]).dt.date

    fx = fetch_usd_inr_daily()
    merged = df.merge(fx, on="Date", how="left")
    # Forward-fill FX if missing on holidays/weekends
    merged["USDINR"] = merged["USDINR"].ffill()

    for c in essential_cols:
        if c in merged.columns:
            merged[c] = merged[c] * merged["USDINR"]

    merged["Currency"] = "INR"

    # Drop helper
    merged = merged.drop(columns=["USDINR"])  

    merged.to_csv(output_csv, index=False)
    return len(df), len(merged)


def convert_hourly_usd_to_inr(input_csv: Path, output_csv: Path) -> Tuple[int, int]:
    df = pd.read_csv(input_csv)
    for c in essential_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    # Accept either 'Datetime' or 'Date'; prefer 'Datetime'
    if "Datetime" in df.columns:
        ts = pd.to_datetime(df["Datetime"], utc=True, errors="coerce")
        df["Datetime"] = ts
    elif "Date" in df.columns:
        ts = pd.to_datetime(df["Date"], utc=True, errors="coerce")
        df["Datetime"] = ts
    else:
        raise ValueError(f"Expected 'Datetime' or 'Date' column in {input_csv}")

    # Floor to hour key
    df["_key_hour"] = df["Datetime"].dt.floor("h")

    fx = fetch_usd_inr_hourly()
    fx["_key_hour"] = fx["Datetime"].dt.floor("h")

    merged = df.merge(fx[["_key_hour", "USDINR"]].drop_duplicates("_key_hour"), on="_key_hour", how="left")

    merged["USDINR"] = merged["USDINR"].ffill()

    for c in essential_cols:
        if c in merged.columns:
            merged[c] = merged[c] * merged["USDINR"]

    merged["Currency"] = "INR"
    merged = merged.drop(columns=["USDINR", "_key_hour"])  

    merged.to_csv(output_csv, index=False)
    return len(df), len(merged)


def main() -> int:
    daily_files = [
        (DATA_DIR / "crypto_daily_data.csv", DATA_DIR / "crypto_daily_data_inr.csv"),
        (DATA_DIR / "bitcoin_data.csv", DATA_DIR / "bitcoin_data_inr.csv"),
    ]
    hourly_files = [
        (DATA_DIR / "crypto_hourly_data.csv", DATA_DIR / "crypto_hourly_data_inr.csv"),
        (DATA_DIR / "bitcoin_hourly_data.csv", DATA_DIR / "bitcoin_hourly_data_inr.csv"),
    ]

    try:
        for src, dst in daily_files:
            if src.exists():
                before, after = convert_daily_usd_to_inr(src, dst)
                print(f"Converted DAILY: {src.name} -> {dst.name} ({before} rows)")
            else:
                print(f"Skipped missing DAILY source: {src}")

        for src, dst in hourly_files:
            if src.exists():
                before, after = convert_hourly_usd_to_inr(src, dst)
                print(f"Converted HOURLY: {src.name} -> {dst.name} ({before} rows)")
            else:
                print(f"Skipped missing HOURLY source: {src}")
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
