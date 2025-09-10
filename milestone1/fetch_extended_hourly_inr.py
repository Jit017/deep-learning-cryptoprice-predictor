import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List

import pandas as pd
import requests

OUTPUT_PATH = Path(__file__).resolve().parent / "crypto_hourly_extended_inr.csv"

# Multiple free APIs to get extended data
APIS = {
    "cryptocompare": {
        "url": "https://min-api.cryptocompare.com/data/v2/histohour",
        "free_limit": 2000,
        "requires_key": False
    },
    "binance": {
        "url": "https://api.binance.com/api/v3/klines",
        "free_limit": 1000,
        "requires_key": False
    },
    "coinbase": {
        "url": "https://api.pro.coinbase.com/products/{symbol}/candles",
        "free_limit": 300,
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

SLEEP_SECONDS = 1.5  # Be gentle with rate limits


def fetch_usd_inr_rate():
    """Fetch current USD-INR rate for conversion"""
    try:
        response = requests.get("https://api.exchangerate-api.com/v4/latest/USD", timeout=30)
        response.raise_for_status()
        data = response.json()
        return data["rates"]["INR"]
    except:
        return 83.0


def fetch_cryptocompare_extended(symbol: str, max_hours: int = 5000) -> pd.DataFrame:
    """Fetch extended data from CryptoCompare using multiple calls"""
    all_data = []
    to_ts = int(datetime.now().timestamp())
    hours_fetched = 0
    
    while hours_fetched < max_hours:
        url = "https://min-api.cryptocompare.com/data/v2/histohour"
        params = {
            "fsym": symbol,
            "tsym": "USD",
            "limit": 2000,  # Max per call
            "toTs": to_ts
        }
        
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if data.get("Response") != "Success" or "Data" not in data or "Data" not in data["Data"]:
                break
                
            rows = data["Data"]["Data"]
            if not rows:
                break
                
            df = pd.DataFrame(rows)
            df["Datetime"] = pd.to_datetime(df["time"], unit="s", utc=True)
            df = df.rename(columns={
                "open": "Open",
                "high": "High", 
                "low": "Low",
                "close": "Close",
                "volumefrom": "Volume"
            })
            
            all_data.append(df)
            hours_fetched += len(rows)
            
            # Update timestamp for next call
            to_ts = rows[0]["time"] - 1
            
            # Stop if we got less than max (reached beginning)
            if len(rows) < 2000:
                break
                
            time.sleep(SLEEP_SECONDS)
            
        except Exception as e:
            print(f"  ⚠ Error in batch for {symbol}: {e}")
            break
    
    if not all_data:
        return pd.DataFrame()
        
    # Combine all batches
    combined_df = pd.concat(all_data, ignore_index=True)
    combined_df = combined_df.sort_values("Datetime").reset_index(drop=True)
    
    # Convert USD to INR
    usd_inr_rate = fetch_usd_inr_rate()
    for col in ["Open", "High", "Low", "Close"]:
        combined_df[col] = combined_df[col] * usd_inr_rate
        
    combined_df["Symbol"] = symbol
    combined_df["Currency"] = "INR"
    
    return combined_df[["Datetime", "Open", "High", "Low", "Close", "Volume", "Symbol", "Currency"]]


def fetch_binance_extended(symbol: str, max_hours: int = 3000) -> pd.DataFrame:
    """Fetch extended data from Binance using multiple calls"""
    symbol_map = {
        "BTC": "BTCUSDT", "ETH": "ETHUSDT", "LTC": "LTCUSDT",
        "XRP": "XRPUSDT", "ADA": "ADAUSDT", "BNB": "BNBUSDT", "SOL": "SOLUSDT"
    }
    
    binance_symbol = symbol_map.get(symbol)
    if not binance_symbol:
        return pd.DataFrame()
    
    all_data = []
    hours_fetched = 0
    
    while hours_fetched < max_hours:
        url = "https://api.binance.com/api/v3/klines"
        params = {
            "symbol": binance_symbol,
            "interval": "1h",
            "limit": 1000  # Max per call
        }
        
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if not data:
                break
                
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
                "open": "Open", "high": "High", "low": "Low", 
                "close": "Close", "volume": "Volume"
            })
            
            all_data.append(df)
            hours_fetched += len(df)
            
            # Add endTime parameter for next call to get older data
            if len(data) > 0:
                oldest_time = int(data[0][0])  # First row's open_time
                params["endTime"] = oldest_time - 1
            
            time.sleep(SLEEP_SECONDS)
            
        except Exception as e:
            print(f"  ⚠ Error in batch for {symbol}: {e}")
            break
    
    if not all_data:
        return pd.DataFrame()
        
    # Combine all batches
    combined_df = pd.concat(all_data, ignore_index=True)
    combined_df = combined_df.sort_values("Datetime").reset_index(drop=True)
    
    # Convert USD to INR
    usd_inr_rate = fetch_usd_inr_rate()
    for col in ["Open", "High", "Low", "Close"]:
        combined_df[col] = combined_df[col] * usd_inr_rate
        
    combined_df["Symbol"] = symbol
    combined_df["Currency"] = "INR"
    
    return combined_df[["Datetime", "Open", "High", "Low", "Close", "Volume", "Symbol", "Currency"]]


def main():
    print("Fetching extended historical hourly INR data...")
    
    # Test USD-INR rate
    usd_inr_rate = fetch_usd_inr_rate()
    print(f"USD-INR rate: {usd_inr_rate}")
    
    all_data = []
    
    for symbol, name in COINS.items():
        print(f"\nFetching {name} ({symbol}) extended hourly data...")
        
        # Try CryptoCompare first (more historical data)
        print(f"  Trying CryptoCompare...")
        df = fetch_cryptocompare_extended(symbol, max_hours=8000)  # ~1 year of hourly data
        
        if df.empty or len(df) < 1000:
            print(f"  ⚠ CryptoCompare limited for {symbol}, trying Binance...")
            df = fetch_binance_extended(symbol, max_hours=5000)
            
        if df.empty:
            print(f"  ✗ No data for {symbol}")
            continue
            
        # Ensure no negative values
        for col in ["Open", "High", "Low", "Close"]:
            df[col] = pd.to_numeric(df[col], errors="coerce").clip(lower=0)
        
        all_data.append(df)
        print(f"  ✓ {symbol}: {len(df)} rows from {df['Datetime'].min()} to {df['Datetime'].max()}")
        print(f"    Duration: {(df['Datetime'].max() - df['Datetime'].min()).days} days")
        
        time.sleep(SLEEP_SECONDS * 2)  # Extra delay between coins
    
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
    print(f"Total duration: {(final_df['Datetime'].max() - final_df['Datetime'].min()).days} days")
    
    # Print summary by symbol
    print("\nSummary by cryptocurrency:")
    for symbol in COINS.keys():
        symbol_data = final_df[final_df['Symbol'] == symbol]
        if not symbol_data.empty:
            duration_days = (symbol_data['Datetime'].max() - symbol_data['Datetime'].min()).days
            print(f"  {symbol}: {len(symbol_data)} rows ({duration_days} days)")
    
    return 0


if __name__ == "__main__":
    try:
        result = main()
        if result == 0:
            print(f"\n✓ Successfully created: {OUTPUT_PATH}")
            print("\nThis dataset contains extended historical data using free APIs only!")
        sys.exit(result)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
