import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List

import pandas as pd
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

OUTPUT_PATH = Path(__file__).resolve().parent / "crypto_hourly_coindesk_inr.csv"

# CoinDesk API configuration
API_KEY = os.getenv('COINDESK_API_KEY')
if not API_KEY:
    raise ValueError("COINDESK_API_KEY not found in .env file")

# Updated CoinDesk API endpoints
BASE_URL = "https://api.coindesk.com"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Define cryptocurrencies supported by CoinDesk
COINS = {
    "BTC": "Bitcoin",
    "ETH": "Ethereum", 
    "LTC": "Litecoin",
    "XRP": "Ripple",
    "ADA": "Cardano",
    "BNB": "Binance Coin",
    "SOL": "Solana"
}

SLEEP_SECONDS = 1  # Rate limiting


def fetch_current_price_coindesk(symbol: str) -> float:
    """Fetch current price for a symbol"""
    # Try different endpoint formats
    endpoints = [
        f"{BASE_URL}/v1/bpi/currentprice/{symbol}.json",
        f"{BASE_URL}/v1/bpi/currentprice.json?index={symbol}",
        f"{BASE_URL}/bpi/currentprice/{symbol}.json"
    ]
    
    for url in endpoints:
        try:
            print(f"  Trying endpoint: {url}")
            response = requests.get(url, headers=HEADERS, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            print(f"  Response: {data}")
            
            if "bpi" in data and "INR" in data["bpi"]:
                return float(data["bpi"]["INR"]["rate_float"])
            elif "bpi" in data and "USD" in data["bpi"]:
                # Convert USD to INR if needed
                usd_price = float(data["bpi"]["USD"]["rate_float"])
                # You might need to fetch USD-INR rate separately
                return usd_price * 83  # Approximate conversion
                
        except Exception as e:
            print(f"  ✗ Error with {url}: {e}")
            continue
    
    return None


def fetch_historical_data_coindesk(symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
    """Fetch historical data from CoinDesk"""
    # Try different endpoint formats
    endpoints = [
        f"{BASE_URL}/v1/bpi/historical/close.json?currency=INR&start={start_date}&end={end_date}&index={symbol}",
        f"{BASE_URL}/bpi/historical/close.json?currency=INR&start={start_date}&end={end_date}&index={symbol}",
        f"{BASE_URL}/v1/bpi/historical/close.json?start={start_date}&end={end_date}&index={symbol}"
    ]
    
    for url in endpoints:
        try:
            print(f"  Trying endpoint: {url}")
            response = requests.get(url, headers=HEADERS, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            print(f"  Response keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
            
            if "bpi" in data:
                # Convert to DataFrame
                df = pd.DataFrame(list(data["bpi"].items()), columns=["Date", "Close"])
                df["Date"] = pd.to_datetime(df["Date"])
                df["Symbol"] = symbol
                df["Currency"] = "INR"
                
                # Add OHLC columns (using Close as approximation)
                df["Open"] = df["Close"]
                df["High"] = df["Close"]
                df["Low"] = df["Close"]
                df["Volume"] = 0
                
                return df[["Date", "Open", "High", "Low", "Close", "Volume", "Symbol", "Currency"]]
                
        except Exception as e:
            print(f"  ✗ Error with {url}: {e}")
            continue
    
    return pd.DataFrame()


def main():
    print("Fetching CoinDesk API data...")
    print(f"API Key: {API_KEY[:10]}..." if API_KEY else "No API key found")
    
    # Test API connection
    print("\nTesting API connection...")
    test_price = fetch_current_price_coindesk("BTC")
    if test_price:
        print(f"✓ API working - BTC current price: ₹{test_price:,.2f}")
    else:
        print("✗ API connection failed - trying without auth...")
        # Try without authentication
        try:
            response = requests.get(f"{BASE_URL}/v1/bpi/currentprice.json", timeout=30)
            if response.status_code == 200:
                print("✓ API accessible without authentication")
                # Update headers to not use auth
                global HEADERS
                HEADERS = {"Content-Type": "application/json"}
            else:
                print(f"✗ API not accessible: {response.status_code}")
                return 1
        except Exception as e:
            print(f"✗ API not accessible: {e}")
            return 1
    
    # Set date range (last 2 years for testing)
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=2*365)).strftime("%Y-%m-%d")
    
    print(f"\nFetching data from {start_date} to {end_date}")
    
    all_data = []
    
    for symbol, name in COINS.items():
        print(f"\nFetching {name} ({symbol}) historical data...")
        
        df = fetch_historical_data_coindesk(symbol, start_date, end_date)
        
        if df.empty:
            print(f"  ⚠ No data for {symbol}")
            continue
            
        # Ensure no negative values
        for col in ["Open", "High", "Low", "Close"]:
            df[col] = pd.to_numeric(df[col], errors="coerce").clip(lower=0)
        
        all_data.append(df)
        print(f"  ✓ {symbol}: {len(df)} rows from {df['Date'].min()} to {df['Date'].max()}")
        
        time.sleep(SLEEP_SECONDS)
    
    if not all_data:
        print("No data fetched from any cryptocurrency")
        return 1
    
    # Merge all datasets
    print("\nMerging all datasets...")
    final_df = pd.concat(all_data, ignore_index=True)
    final_df = final_df.sort_values(["Date", "Symbol"]).reset_index(drop=True)
    
    # Save to file
    final_df.to_csv(OUTPUT_PATH, index=False)
    
    print(f"\nSaved: {OUTPUT_PATH}")
    print(f"Total rows: {len(final_df)}")
    print(f"Date range: {final_df['Date'].min()} to {final_df['Date'].max()}")
    
    # Print summary by symbol
    print("\nSummary by cryptocurrency:")
    for symbol in COINS.keys():
        symbol_data = final_df[final_df['Symbol'] == symbol]
        if not symbol_data.empty:
            print(f"  {symbol}: {len(symbol_data)} rows ({symbol_data['Date'].min()} to {symbol_data['Date'].max()})")
    
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
