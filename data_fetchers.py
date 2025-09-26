"""
Data fetching utilities for external APIs (CoinDesk, Yahoo Finance, Binance).
"""
import requests
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import time
from config import CONFIG, COIN_SYMBOLS, BINANCE_SYMBOLS


def fetch_coindesk_price(symbol: str = "BTC") -> Optional[Dict[str, Any]]:
    """Fetch current price from CoinDesk API."""
    try:
        url = CONFIG["COINDESK_API_URL"]
        headers = {}
        if CONFIG["COINDESK_API_KEY"]:
            headers["X-API-Key"] = CONFIG["COINDESK_API_KEY"]
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if "bpi" in data and "USD" in data["bpi"]:
            return {
                "price": float(data["bpi"]["USD"]["rate_float"]),
                "currency": "USD",
                "source": "coindesk",
                "timestamp": data.get("time", {}).get("updatedISO", datetime.utcnow().isoformat())
            }
    except Exception as e:
        print(f"CoinDesk fetch error for {symbol}: {e}")
    return None


def fetch_yahoo_finance_data(symbol: str, days: int = 60) -> Optional[pd.DataFrame]:
    """Fetch historical data from Yahoo Finance."""
    try:
        yahoo_symbol = COIN_SYMBOLS.get(symbol.upper(), f"{symbol.upper()}-USD")
        ticker = yf.Ticker(yahoo_symbol)
        
        # Get historical data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        hist = ticker.history(start=start_date, end=end_date, interval="1d")
        
        if hist.empty:
            print(f"No Yahoo Finance data for {symbol}")
            return None
            
        # Select relevant columns and rename
        df = hist[["Open", "High", "Low", "Close", "Volume"]].copy()
        df.columns = ["open", "high", "low", "close", "volume"]
        df = df.reset_index()
        
        return df
        
    except Exception as e:
        print(f"Yahoo Finance fetch error for {symbol}: {e}")
    return None


def fetch_binance_data(symbol: str, hours: int = 60) -> Optional[pd.DataFrame]:
    """Fetch historical data from Binance API."""
    try:
        binance_symbol = BINANCE_SYMBOLS.get(symbol.upper())
        if not binance_symbol:
            print(f"Binance symbol not found for {symbol}")
            return None
            
        # Binance API endpoint for klines (candlestick data)
        url = "https://api.binance.com/api/v3/klines"
        
        # Calculate timestamps
        end_time = int(time.time() * 1000)
        start_time = end_time - (hours * 60 * 60 * 1000)
        
        params = {
            "symbol": binance_symbol,
            "interval": "1h",
            "startTime": start_time,
            "endTime": end_time,
            "limit": 1000
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if not data:
            print(f"No Binance data for {symbol}")
            return None
            
        # Convert to DataFrame
        df = pd.DataFrame(data, columns=[
            "timestamp", "open", "high", "low", "close", "volume",
            "close_time", "quote_asset_volume", "number_of_trades",
            "taker_buy_base_asset_volume", "taker_buy_quote_asset_volume", "ignore"
        ])
        
        # Convert timestamp to datetime
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        df = df.set_index("timestamp")
        
        # Select relevant columns and convert to float
        df = df[["open", "high", "low", "close", "volume"]].astype(float)
        df = df.reset_index()
        
        return df
        
    except Exception as e:
        print(f"Binance fetch error for {symbol}: {e}")
    return None


def fetch_current_price(symbol: str, currency: str = "USD") -> Optional[float]:
    """Fetch current price for a symbol from available sources."""
    try:
        # Try Yahoo Finance first
        yahoo_symbol = COIN_SYMBOLS.get(symbol.upper(), f"{symbol.upper()}-USD")
        ticker = yf.Ticker(yahoo_symbol)
        info = ticker.info
        
        if "currentPrice" in info:
            return float(info["currentPrice"])
        elif "regularMarketPrice" in info:
            return float(info["regularMarketPrice"])
            
        # Fallback to CoinDesk for BTC
        if symbol.upper() == "BTC":
            coindesk_data = fetch_coindesk_price(symbol)
            if coindesk_data:
                return coindesk_data["price"]
                
    except Exception as e:
        print(f"Current price fetch error for {symbol}: {e}")
    
    return None


def get_historical_data(symbol: str, timeframe: str = "daily", limit: int = 60) -> Optional[pd.DataFrame]:
    """Get historical data for a symbol based on timeframe."""
    try:
        if timeframe.lower() == "hourly":
            return fetch_binance_data(symbol, limit)
        else:
            return fetch_yahoo_finance_data(symbol, limit)
    except Exception as e:
        print(f"Historical data fetch error for {symbol} ({timeframe}): {e}")
    return None


def prepare_model_data(df: pd.DataFrame, sequence_length: int = 60) -> Optional[np.ndarray]:
    """Prepare data for model prediction."""
    try:
        if df is None or df.empty:
            return None
            
        # Select features (open, high, low, close, volume)
        features = ["open", "high", "low", "close", "volume"]
        if not all(col in df.columns for col in features):
            print(f"Missing required columns: {features}")
            return None
            
        # Get the last sequence_length rows
        data = df[features].tail(sequence_length).values
        
        # Normalize the data (simple min-max scaling)
        data_normalized = (data - data.min(axis=0)) / (data.max(axis=0) - data.min(axis=0) + 1e-8)
        
        return data_normalized
        
    except Exception as e:
        print(f"Data preparation error: {e}")
    return None


def evaluate_prediction_accuracy(
    prediction: float, 
    actual: float
) -> Dict[str, float]:
    """Calculate accuracy metrics for a prediction."""
    try:
        if actual == 0:
            return {"mae": abs(prediction), "ape": 100.0}
            
        mae = abs(prediction - actual)
        ape = (mae / actual) * 100
        
        return {"mae": mae, "ape": ape}
        
    except Exception as e:
        print(f"Accuracy calculation error: {e}")
        return {"mae": 0.0, "ape": 100.0}
