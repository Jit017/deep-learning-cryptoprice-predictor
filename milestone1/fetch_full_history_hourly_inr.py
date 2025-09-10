import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd
import requests

OUTPUT_PATH = Path(__file__).resolve().parent / "crypto_hourly_full_inr.csv"
CHECKPOINT_DIR = Path(__file__).resolve().parent / "checkpoints"
CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)

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
LIMIT_PER_CALL = 2000
SLEEP_SECONDS = 1.25
MAX_RETRIES = 4


def load_checkpoint(symbol: str) -> Optional[pd.DataFrame]:
    path = CHECKPOINT_DIR / f"hourly_inr_{symbol}.csv"
    if path.exists():
        try:
            df = pd.read_csv(path)
            df["Datetime"] = pd.to_datetime(df["Datetime"], utc=True, errors="coerce")
            return df
        except Exception:
            return None
    return None


def save_checkpoint(symbol: str, df: pd.DataFrame) -> None:
    path = CHECKPOINT_DIR / f"hourly_inr_{symbol}.csv"
    # Sort and drop duplicates before save
    out = df.sort_values("Datetime").drop_duplicates(subset=["Datetime"]).reset_index(drop=True)
    out.to_csv(path, index=False)


def fetch_full_hist_hour_inr(symbol: str) -> pd.DataFrame:
    # Resume from checkpoint if present
    existing = load_checkpoint(symbol)
    all_rows: List[pd.DataFrame] = []
    if existing is not None and not existing.empty:
        all_rows.append(existing)
        # Continue from the earliest timestamp already fetched
        earliest_existing = int(existing["Datetime"].min().timestamp())
        to_ts = earliest_existing - 1
        print(f"  ↻ Resuming {symbol} from {pd.to_datetime(to_ts, unit='s', utc=True)}")
    else:
        to_ts = int(datetime.now(tz=timezone.utc).timestamp())

    no_progress_batches = 0

    while True:
        params = {
            "fsym": symbol,
            "tsym": TSYM,
            "limit": LIMIT_PER_CALL,
            "toTs": to_ts,
        }
        retries = 0
        while True:
            try:
                resp = requests.get(API_URL, params=params, timeout=45)
                resp.raise_for_status()
                payload = resp.json()
                break
            except requests.exceptions.RequestException as e:
                retries += 1
                if retries > MAX_RETRIES:
                    print(f"  ✗ {symbol}: network error after retries: {e}")
                    # Flush what we have and return
                    if all_rows:
                        combined = pd.concat(all_rows, ignore_index=True)
                        save_checkpoint(symbol, combined)
                        return combined
                    return pd.DataFrame()
                sleep_for = SLEEP_SECONDS * (1.5 ** (retries - 1))
                print(f"  ⚠ {symbol}: retry {retries}/{MAX_RETRIES} after {sleep_for:.1f}s due to {e}")
                time.sleep(sleep_for)

        if payload.get("Response") != "Success" or "Data" not in payload or "Data" not in payload["Data"]:
            break
        data = payload["Data"]["Data"]
        if not data:
            break

        batch = pd.DataFrame(data)
        prev_to_ts = to_ts
        # Move window back
        earliest_time = data[0]["time"]
        to_ts = earliest_time - 1

        if len(batch) == 0 or to_ts >= prev_to_ts:
            no_progress_batches += 1
            if no_progress_batches >= 3:
                print(f"  ⚠ {symbol}: no progress for 3 batches, stopping.")
                break
        else:
            no_progress_batches = 0

        batch["Datetime"] = pd.to_datetime(batch["time"], unit="s", utc=True)
        batch = batch.rename(columns={
            "open": "Open",
            "high": "High",
            "low": "Low",
            "close": "Close",
            "volumefrom": "VolumeBase",
            "volumeto": "VolumeINR",
        })
        keep = ["Datetime", "Open", "High", "Low", "Close", "VolumeBase", "VolumeINR"]
        batch = batch[keep]

        # Clean
        for c in ["Open", "High", "Low", "Close"]:
            batch[c] = pd.to_numeric(batch[c], errors="coerce").clip(lower=0)
        batch["Symbol"] = symbol
        batch["Currency"] = TSYM

        all_rows.append(batch)

        # Periodic flush to checkpoint every ~5 batches
        if len(all_rows) % 5 == 0:
            combined = pd.concat(all_rows, ignore_index=True)
            save_checkpoint(symbol, combined)
            print(f"  💾 {symbol}: checkpoint saved ({len(combined)} rows) up to {combined['Datetime'].min()} .. {combined['Datetime'].max()}")

        # Be gentle
        time.sleep(SLEEP_SECONDS)

    if not all_rows:
        return pd.DataFrame()

    combined = pd.concat(all_rows, ignore_index=True)
    save_checkpoint(symbol, combined)
    # Final tidy
    combined = combined.sort_values("Datetime").drop_duplicates(subset=["Datetime"]).reset_index(drop=True)
    return combined


def main() -> int:
    frames: List[pd.DataFrame] = []
    for sym in COINS.keys():
        print(f"Fetching FULL hourly INR history for {sym}...")
        df = fetch_full_hist_hour_inr(sym)
        if df.empty:
            print(f"  ⚠ No data for {sym}")
            continue
        print(f"  ✓ {sym}: {len(df)} rows from {df['Datetime'].min()} to {df['Datetime'].max()}")
        frames.append(df)

    if not frames:
        print("No data fetched.", file=sys.stderr)
        return 1

    merged = pd.concat(frames, ignore_index=True)
    merged = merged.sort_values(["Datetime", "Symbol"]).reset_index(drop=True)
    merged.to_csv(OUTPUT_PATH, index=False)

    print(f"\nSaved: {OUTPUT_PATH} rows={len(merged)}")
    for sym in COINS.keys():
        sub = merged[merged["Symbol"] == sym]
        if not sub.empty:
            print(f"  {sym}: {sub['Datetime'].min()} -> {sub['Datetime'].max()}  ({len(sub)} rows)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
