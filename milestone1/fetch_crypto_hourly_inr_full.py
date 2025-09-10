import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

import pandas as pd
import requests

OUTPUT_PATH = Path(__file__).resolve().parent / "crypto_hourly_data_inr_full.csv"

# Map short symbols to CryptoCompare fsym and label
COINS: Dict[str, str] = {
    "BTC": "BTC",
    "ETH": "ETH", 
    "LTC": "LTC",
    "XRP": "XRP",
    "ADA": "ADA",
    "BNB": "BNB",
    "SOL": "SOL",
}

API_URL = "https://min-api.cryptocompare.com/data/v2/histohour"
TSYM = "INR"
LIMIT_PER_CALL = 2000  # CryptoCompare max per call
SLEEP_SECONDS = 1.2    # be gentle to avoid rate limits
MAX_RETRIES = 3


def fetch_hist_hour_inr(fsym: str) -> pd.DataFrame:
    all_rows: List[dict] = []
    to_ts = int(datetime.now(tz=timezone.utc).timestamp())
    last_batch_size = LIMIT_PER_CALL
    retry_count = 0

    while retry_count < MAX_RETRIES:
        try:
            params = {
                "fsym": fsym,
                "tsym": TSYM,
                "limit": LIMIT_PER_CALL,
                "toTs": to_ts,
            }
            resp = requests.get(API_URL, params=params, timeout=60)
            resp.raise_for_status()
            payload = resp.json()
            
            if payload.get("Response") != "Success" or "Data" not in payload or "Data" not in payload["Data"]:
                print(f"  ⚠ API response issue for {fsym}: {payload.get('Message', 'Unknown error')}")
                break
                
            data = payload["Data"]["Data"]
            if not data:
                break

            # Append and step back
            all_rows.extend(data)
            last_time = data[0]["time"]  # earliest in this batch
            # Next window ends before earliest time we just received
            to_ts = last_time - 1
            last_batch_size = len(data)

            # Stop if batch smaller than limit → reached the beginning
            if last_batch_size < LIMIT_PER_CALL:
                break

            time.sleep(SLEEP_SECONDS)
            retry_count = 0  # Reset retry count on success
            
        except requests.exceptions.RequestException as e:
            retry_count += 1
            print(f"  ⚠ Retry {retry_count}/{MAX_RETRIES} for {fsym}: {e}")
            if retry_count >= MAX_RETRIES:
                print(f"  ✗ Failed {fsym} after {MAX_RETRIES} retries")
                break
            time.sleep(SLEEP_SECONDS * 2)  # Longer sleep on retry

    if not all_rows:
        return pd.DataFrame()

    df = pd.DataFrame(all_rows)
    # Normalize
    df["Datetime"] = pd.to_datetime(df["time"], unit="s", utc=True)
    df = df.rename(columns={
        "open": "Open",
        "high": "High", 
        "low": "Low",
        "close": "Close",
        "volumefrom": "VolumeFrom",
        "volumeto": "VolumeTo",
    })
    keep = ["Datetime", "Open", "High", "Low", "Close", "VolumeFrom", "VolumeTo"]
    df = df[keep]

    # Add Symbol and Currency columns
    df["Symbol"] = fsym
    df["Currency"] = TSYM

    # Ensure no negative OHLC values
    for c in ["Open", "High", "Low", "Close"]:
        df[c] = pd.to_numeric(df[c], errors="coerce").clip(lower=0)

    # Use traded volume in base coin; also keep INR volume
    df = df.rename(columns={"VolumeFrom": "VolumeBase", "VolumeTo": "VolumeINR"})

    return df.sort_values("Datetime").reset_index(drop=True)


def main() -> int:
    frames: List[pd.DataFrame] = []
    for sym, fsym in COINS.items():
        print(f"Fetching hourly INR for {sym}...")
        try:
            df = fetch_hist_hour_inr(fsym)
        except Exception as e:
            print(f"  ✗ Failed {sym}: {e}", file=sys.stderr)
            continue
        if df.empty:
            print(f"  ⚠ No data for {sym}")
            continue
        # Standardize Symbol to short code (same as fsym here)
        df["Symbol"] = sym
        # Keep common output columns
        df = df[["Datetime", "Open", "High", "Low", "Close", "VolumeBase", "VolumeINR", "Symbol", "Currency"]]
        print(f"  ✓ {sym}: {len(df)} rows from {df['Datetime'].min()} to {df['Datetime'].max()}")
        frames.append(df)

    if not frames:
        print("No data fetched.", file=sys.stderr)
        return 1

    merged = pd.concat(frames, ignore_index=True)
    merged = merged.sort_values(["Datetime", "Symbol"]).reset_index(drop=True)

    # Write output
    merged.to_csv(OUTPUT_PATH, index=False)
    print(f"\nSaved: {OUTPUT_PATH}  rows={len(merged)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
