import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List

import pandas as pd
import requests

OUTPUT_PATH = Path(__file__).resolve().parent / "crypto_hourly_alternative_inr.csv"

# Alternative API endpoints that are more reliable
APIS = {
    "cryptocompare": {
        "base_url": "https://min-api.cryptocompare.com/data/v2/histohour",
        "requires_key": False
    },
    "binance": {
        "base_url": "https://api.binance.com/api/v3/klines",
        "requires_key": False
    }
}

# Define cryptocurrencies
COINS = {
    "BTC": "Bitcoin",
    "ETH": "Ethereum", 
    "LTC": "Litecoin",
    "XRP": "Ripple",
    "ADA": "Cardano",
    "BNB": "Binance Coin",
    "SOL": "Solana"
}

SLEEP_SECONDS = 1


def fetch_usd_inr_rate():
    """Fetch current USD-INR rate for conversion"""
    try:
        # Use a reliable forex API
        response = requests.get("https://api.exchangerate-api.com/v4/latest/USD", timeout=30)
        response.raise_for_status()
        data = response.json()
        return data["rates"]["INR"]
    except:
        # Fallback to approximate rate
        return 83.0


def fetch_cryptocompare_hourly(symbol: str, limit: int = 2000) -> pd.DataFrame:
    """Fetch hourly data from CryptoCompare"""
    url = "https://min-api.cryptocompare.com/data/v2/histohour"
    
    params = {
        "fsym": symbol,
        "tsym": "USD",
        "limit": limit
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        if data.get("Response") != "Success" or "Data" not in data or "Data" not in data["Data"]:
            return pd.DataFrame()
            
        rows = data["Data"]["Data"]
        if not rows:
            return pd.DataFrame()
            
        df = pd.DataFrame(rows)
        df["Datetime"] = pd.to_datetime(df["time"], unit="s", utc=True)
        df = df.rename(columns={
            "open": "Open",
            "high": "High", 
            "low": "Low",
            "close": "Close",
            "volumefrom": "Volume"
        })
        
        # Convert USD to INR
        usd_inr_rate = fetch_usd_inr_rate()
        for col in ["Open", "High", "Low", "Close"]:
            df[col] = df[col] * usd_inr_rate
            
        df["Symbol"] = symbol
        df["Currency"] = "INR"
        
        return df[["Datetime", "Open", "High", "Low", "Close", "Volume", "Symbol", "Currency"]]
        
    except Exception as e:
        print(f"  ✗ Error fetching {symbol}: {e}")
        return pd.DataFrame()


def fetch_binance_hourly(symbol: str, limit: int = 1000) -> pd.DataFrame:
    """Fetch hourly data from Binance"""
    # Convert symbol to Binance format
    symbol_map = {
        "BTC": "BTCUSDT",
        "ETH": "ETHUSDT", 
        "LTC": "LTCUSDT",
        "XRP": "XRPUSDT",
        "ADA": "ADAUSDT",
        "BNB": "BNBUSDT",
        "SOL": "SOLUSDT"
    }
    
    binance_symbol = symbol_map.get(symbol)
    if not binance_symbol:
        return pd.DataFrame()
        
    url = "https://api.binance.com/api/v3/klines"
    
    params = {
        "symbol": binance_symbol,
        "interval": "1h",
        "limit": limit
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        if not data:
            return pd.DataFrame()
            
        # Binance returns array of arrays
        df = pd.DataFrame(data, columns=[
            "open_time", "open", "high", "low", "close", "volume",
            "close_time", "quote_volume", "trades", "taker_buy_base",
            "taker_buy_quote", "ignore"
        ])
        
        df["Datetime"] = pd.to_datetime(df["open_time"], unit="ms", utc=True)
        
        # Convert string values to float
        for col in ["open", "high", "low", "close", "volume"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")
            
        df = df.rename(columns={
            "open": "Open",
            "high": "High",
            "low": "Low", 
            "close": "Close",
            "volume": "Volume"
        })
        
        # Convert USD to INR
        usd_inr_rate = fetch_usd_inr_rate()
        for col in ["Open", "High", "Low", "Close"]:
            df[col] = df[col] * usd_inr_rate
            
        df["Symbol"] = symbol
        df["Currency"] = "INR"
        
        return df[["Datetime", "Open", "High", "Low", "Close", "Volume", "Symbol", "Currency"]]
        
    except Exception as e:
        print(f"  ✗ Error fetching {symbol}: {e}")
        return pd.DataFrame()


def main():
    print("Fetching alternative API data...")
    
    # Test USD-INR rate
    usd_inr_rate = fetch_usd_inr_rate()
    print(f"USD-INR rate: {usd_inr_rate}")
    
    all_data = []
    
    for symbol, name in COINS.items():
        print(f"\nFetching {name} ({symbol}) hourly data...")
        
        # Try CryptoCompare first
        df = fetch_cryptocompare_hourly(symbol, limit=2000)
        
        if df.empty:
            print(f"  ⚠ CryptoCompare failed for {symbol}, trying Binance...")
            df = fetch_binance_hourly(symbol, limit=1000)
            
        if df.empty:
            print(f"  ✗ No data for {symbol}")
            continue
            
        # Ensure no negative values
        for col in ["Open", "High", "Low", "Close"]:
            df[col] = pd.to_numeric(df[col], errors="coerce").clip(lower=0)
        
        all_data.append(df)
        print(f"  ✓ {symbol}: {len(df)} rows from {df['Datetime'].min()} to {df['Datetime'].max()}")
        
        time.sleep(SLEEP_SECONDS)
    
    if not all_data:
        print("No data fetched from any cryptocurrency")
        return 1
    
    # Merge all datasets
    print("\nMerging all datasets...")
    final_df = pd.concat(all_data, ignore_index=True)
    final_df = final_df.sort_values(["Datetime", "Symbol"]).reset_index(drop=True)
    
    # Save to file
    final_df.to_csv(OUTPUT_PATH, index=False)
    
    print(f"\nSaved: {OUTPUT_PATH}")
    print(f"Total rows: {len(final_df)}")
    print(f"Date range: {final_df['Datetime'].min()} to {final_df['Datetime'].max()}")
    
    # Print summary by symbol
    print("\nSummary by cryptocurrency:")
    for symbol in COINS.keys():
        symbol_data = final_df[final_df['Symbol'] == symbol]
        if not symbol_data.empty:
            print(f"  {symbol}: {len(symbol_data)} rows ({symbol_data['Datetime'].min()} to {symbol_data['Datetime'].max()})")
    
    return 0


if __name__ == "__main__":
    try:
        result = main()
        if result == 0:
            print(f"\n✓ Successfully created: {OUTPUT_PATH}")
        sys.exit(result)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
