import sys
from pathlib import Path

import pandas as pd
import yfinance as yf


def fetch_and_save_bitcoin_data():
    symbol_yf = "BTC-USD"
    
    # Fetch daily data (existing functionality)
    print("Fetching daily Bitcoin data...")
    df_daily = yf.download(
        tickers=symbol_yf,
        period="max",
        interval="1d",
        auto_adjust=False,
        threads=True,
        progress=False,
    )

    if df_daily is None or df_daily.empty:
        raise RuntimeError("No daily data returned from yfinance for BTC-USD")

    df_daily = df_daily.reset_index()
    df_daily = df_daily[["Date", "Open", "High", "Low", "Close", "Volume"]].copy()

    # Ensure Date is date-only (no time component)
    if pd.api.types.is_datetime64_any_dtype(df_daily["Date"]):
        df_daily["Date"] = df_daily["Date"].dt.date

    # Add Symbol column
    df_daily["Symbol"] = "BTC"
    df_daily = df_daily[["Date", "Open", "High", "Low", "Close", "Volume", "Symbol"]]

    # Save daily data
    daily_output_path = Path(__file__).resolve().parent / "bitcoin_data.csv"
    df_daily.to_csv(daily_output_path, index=False)
    print(f"Saved daily CSV to: {daily_output_path}")
    print("First 5 rows of daily data:")
    print(df_daily.head().to_string(index=False))
    
    # Fetch hourly data (new functionality)
    print("\nFetching hourly Bitcoin data...")
    df_hourly = yf.download(
        tickers=symbol_yf,
        period="60d",  # Last 60 days for hourly data (yfinance limit for free tier)
        interval="1h",
        auto_adjust=False,
        threads=True,
        progress=False,
    )

    if df_hourly is None or df_hourly.empty:
        raise RuntimeError("No hourly data returned from yfinance for BTC-USD")

    df_hourly = df_hourly.reset_index()
    df_hourly = df_hourly[["Datetime", "Open", "High", "Low", "Close", "Volume"]].copy()
    
    # Rename Datetime to Date for consistency
    df_hourly = df_hourly.rename(columns={"Datetime": "Date"})

    # Add Symbol column
    df_hourly["Symbol"] = "BTC"
    df_hourly = df_hourly[["Date", "Open", "High", "Low", "Close", "Volume", "Symbol"]]

    # Save hourly data
    hourly_output_path = Path(__file__).resolve().parent / "bitcoin_hourly_data.csv"
    df_hourly.to_csv(hourly_output_path, index=False)
    print(f"Saved hourly CSV to: {hourly_output_path}")
    print("First 5 rows of hourly data:")
    print(df_hourly.head().to_string(index=False))

    return daily_output_path, hourly_output_path


if __name__ == "__main__":
    try:
        daily_path, hourly_path = fetch_and_save_bitcoin_data()
        print(f"\nSummary:")
        print(f"Daily data: {daily_path}")
        print(f"Hourly data: {hourly_path}")
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


