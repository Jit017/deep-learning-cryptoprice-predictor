"""
Configuration management for FutureCoin application.
"""
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR / "crypto-prediction-website-main"
MODELS_DIR = BASE_DIR / "models"
DB_PATH = BASE_DIR / "app.db"

# Load configuration from environment variables
def load_config():
    config = {
        "COINDESK_API_KEY": os.getenv("COINDESK_API_KEY", ""),
        "COINDESK_API_URL": os.getenv("COINDESK_API_URL", "https://api.coindesk.com/v1/bpi/currentprice.json"),
        "YAHOO_FINANCE_DAYS_LIMIT": int(os.getenv("YAHOO_FINANCE_DAYS_LIMIT", "60")),
        "BINANCE_HOURS_LIMIT": int(os.getenv("BINANCE_HOURS_LIMIT", "60")),
        "DAYS_AHEAD_MAX": int(os.getenv("DAYS_AHEAD_MAX", "30")),
        "HOURS_AHEAD_MAX": int(os.getenv("HOURS_AHEAD_MAX", "23")),
        "DAILY_MODEL_CURRENCY": os.getenv("DAILY_MODEL_CURRENCY", "INR"),
        "HOURLY_MODEL_CURRENCY": os.getenv("HOURLY_MODEL_CURRENCY", "USDT"),
        "FLASK_SECRET_KEY": os.getenv("FLASK_SECRET_KEY", "change-this-secret-in-env"),
        "APP_USERNAME": os.getenv("APP_USERNAME", "admin"),
        "APP_PASSWORD": os.getenv("APP_PASSWORD", "admin"),
        "PORT": int(os.getenv("PORT", "5000")),
        "USE_ASYNC_EVAL": os.getenv("USE_ASYNC_EVAL", "0") == "1",
        "REDIS_URL": os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    }
    return config

# Known coin symbols to alias
KNOWN_SYMBOLS = [
    "btc", "eth", "ada", "bnb", "xrp", "sol", "doge", "ltc", "matic"
]

# Coin symbol mappings
COIN_SYMBOLS = {
    "BTC": "BTC-USD",
    "ETH": "ETH-USD", 
    "ADA": "ADA-USD",
    "BNB": "BNB-USD",
    "XRP": "XRP-USD",
    "SOL": "SOL-USD",
    "DOGE": "DOGE-USD",
    "LTC": "LTC-USD",
    "MATIC": "MATIC-USD"
}

BINANCE_SYMBOLS = {
    "BTC": "BTCUSDT",
    "ETH": "ETHUSDT",
    "ADA": "ADAUSDT", 
    "BNB": "BNBUSDT",
    "XRP": "XRPUSDT",
    "SOL": "SOLUSDT",
    "DOGE": "DOGEUSDT",
    "LTC": "LTCUSDT",
    "MATIC": "MATICUSDT"
}

# Load configuration
CONFIG = load_config()
