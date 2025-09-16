import os
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
import json
from datetime import datetime, timedelta
import requests
import pandas as pd
import yfinance as yf

from flask import Flask, jsonify, request, send_from_directory, session
import joblib
import pickle
import numpy as np

# Optional tensorflow/keras import
try:
    import tensorflow as tf  # type: ignore
    _TF_AVAILABLE = True
except Exception:
    _TF_AVAILABLE = False

# Optional standalone Keras 3
try:
    import keras  # type: ignore
    _KERAS_AVAILABLE = True
except Exception:
    _KERAS_AVAILABLE = False

import json
try:
    import h5py  # type: ignore
    _H5_AVAILABLE = True
except Exception:
    _H5_AVAILABLE = False

BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR / "crypto-prediction-website-main"
MODELS_DIR = BASE_DIR / "models"

# Load configuration
def load_config():
    config = {
        "COINDESK_API_KEY": os.getenv("COINDESK_API_KEY", ""),
        "COINDESK_API_URL": os.getenv("COINDESK_API_URL", "https://api.coindesk.com/v1/bpi/currentprice.json"),
        "YAHOO_FINANCE_DAYS_LIMIT": int(os.getenv("YAHOO_FINANCE_DAYS_LIMIT", "60")),
        "BINANCE_HOURS_LIMIT": int(os.getenv("BINANCE_HOURS_LIMIT", "60")),
        "DAYS_AHEAD_MAX": int(os.getenv("DAYS_AHEAD_MAX", "30")),
        "HOURS_AHEAD_MAX": int(os.getenv("HOURS_AHEAD_MAX", "23")),
        "DAILY_MODEL_CURRENCY": os.getenv("DAILY_MODEL_CURRENCY", "INR"),
        "HOURLY_MODEL_CURRENCY": os.getenv("HOURLY_MODEL_CURRENCY", "USDT")
    }
    return config

CONFIG = load_config()

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

app = Flask(
    __name__,
    static_folder=str(FRONTEND_DIR),
    static_url_path="/",
)

# Secret key for session management
app.secret_key = os.getenv("FLASK_SECRET_KEY", "change-this-secret-in-env")

_loaded_models: Dict[str, Any] = {}
_model_meta: Dict[str, Dict[str, Any]] = {}


def fetch_yahoo_finance_data(symbol: str, days: int = 60) -> Optional[pd.DataFrame]:
    """Fetch daily data from Yahoo Finance"""
    try:
        yahoo_symbol = COIN_SYMBOLS.get(symbol.upper())
        if not yahoo_symbol:
            return None
        
        ticker = yf.Ticker(yahoo_symbol)
        data = ticker.history(period=f"{days}d")
        
        if data.empty:
            return None
            
        # Reset index to make Date a column
        data = data.reset_index()
        data['Date'] = pd.to_datetime(data['Date']).dt.date
        
        # Select only OHLCV columns
        columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
        data = data[columns]
        
        return data
    except Exception as e:
        print(f"Error fetching Yahoo Finance data for {symbol}: {e}")
        return None


def fetch_binance_hourly_data(symbol: str, hours: int = 60) -> Optional[pd.DataFrame]:
    """Fetch hourly data from Binance"""
    try:
        binance_symbol = BINANCE_SYMBOLS.get(symbol.upper())
        if not binance_symbol:
            return None
            
        # Binance API endpoint
        url = "https://api.binance.com/api/v3/klines"
        params = {
            'symbol': binance_symbol,
            'interval': '1h',
            'limit': min(hours, 1000)  # Binance limit
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if not data:
            return None
            
        # Convert to DataFrame
        df = pd.DataFrame(data, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_volume', 'trades', 'taker_buy_base',
            'taker_buy_quote', 'ignore'
        ])
        
        # Convert timestamp to datetime
        df['Date'] = pd.to_datetime(df['timestamp'], unit='ms')
        
        # Select and rename columns
        df = df[['Date', 'open', 'high', 'low', 'close', 'volume']]
        df.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
        
        # Convert to numeric
        for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
        return df
    except Exception as e:
        print(f"Error fetching Binance data for {symbol}: {e}")
        return None


def get_coindesk_price() -> Optional[float]:
    """Get current Bitcoin price from CoinDesk"""
    try:
        response = requests.get(CONFIG["COINDESK_API_URL"], timeout=5)
        response.raise_for_status()
        
        data = response.json()
        return float(data['bpi']['USD']['rate_float'])
    except Exception as e:
        print(f"Error fetching CoinDesk price: {e}")
        return None


def prepare_model_input(data: pd.DataFrame, sequence_length: int = 60) -> np.ndarray:
    """Prepare input data for LSTM model"""
    if data is None or len(data) < sequence_length:
        return None
        
    # Use Close prices
    prices = data['Close'].values
    
    # Create sequences
    sequences = []
    for i in range(len(prices) - sequence_length + 1):
        sequences.append(prices[i:i + sequence_length])
    
    if not sequences:
        return None
        
    # Convert to numpy array and reshape for LSTM (samples, timesteps, features)
    X = np.array(sequences)
    X = X.reshape((X.shape[0], X.shape[1], 1))
    
    return X[-1:]  # Return the last sequence


def _add_aliases(stem_lower: str, model: Any, meta: Dict[str, Any]) -> None:
    for sym in KNOWN_SYMBOLS:
        if sym in stem_lower and sym not in _loaded_models:
            _loaded_models[sym] = model
            _model_meta[sym] = {**meta, "alias_of": stem_lower}


def _load_h5_with_patch(path: Path):
    if not (_TF_AVAILABLE and _H5_AVAILABLE):
        raise RuntimeError("TF/H5 not available for fallback loader")
    with h5py.File(str(path), "r") as f:
        if "model_config" not in f.attrs:
            raise ValueError("H5 file missing model_config")
        config_json = f.attrs["model_config"]
        if isinstance(config_json, bytes):
            config_json = config_json.decode("utf-8")
        config = json.loads(config_json)
    # Recursively replace 'batch_shape' with 'batch_input_shape'
    def patch(obj):
        if isinstance(obj, dict):
            new = {}
            for k, v in obj.items():
                key = "batch_input_shape" if k == "batch_shape" else k
                new[key] = patch(v)
            return new
        if isinstance(obj, list):
            return [patch(x) for x in obj]
        return obj
    patched = patch(config)
    model = tf.keras.models.model_from_config(patched)
    # Load weights
    model.load_weights(str(path))
    return model


def _try_load_h5(path: Path):
    # Prefer standalone Keras if available (better for Keras 3 models)
    if _KERAS_AVAILABLE:
        try:
            model = keras.models.load_model(str(path))
            return model, {"type": "keras3", "path": str(path)}
        except Exception:
            pass
    # Try tf.keras
    if _TF_AVAILABLE:
        try:
            model = tf.keras.models.load_model(str(path))
            return model, {"type": "keras", "path": str(path)}
        except Exception:
            # Patch fallback
            try:
                model = _load_h5_with_patch(path)
                return model, {"type": "keras_patched", "path": str(path), "note": "batch_shape patched"}
            except Exception as e:
                raise e
    raise RuntimeError("No Keras loader available")


def load_models() -> None:
    _loaded_models.clear()
    _model_meta.clear()
    if not MODELS_DIR.exists():
        return
    for file in MODELS_DIR.iterdir():
        if not file.is_file():
            continue
        stem_lower = file.stem.lower()
        try:
            if file.suffix in [".joblib", ".jl"]:
                model = joblib.load(file)
                _loaded_models[stem_lower] = model
                meta = {"type": "sklearn", "path": str(file)}
                _model_meta[stem_lower] = meta
                _add_aliases(stem_lower, model, meta)
            elif file.suffix in [".pkl", ".pickle"]:
                with open(file, "rb") as f:
                    model = pickle.load(f)
                _loaded_models[stem_lower] = model
                meta = {"type": "pickle", "path": str(file)}
                _model_meta[stem_lower] = meta
                _add_aliases(stem_lower, model, meta)
            elif file.suffix == ".h5":
                try:
                    model, meta = _try_load_h5(file)
                    # Determine input shape for info
                    ishape = None
                    try:
                        shape = getattr(model, "input_shape", None)
                        if shape is not None:
                            if isinstance(shape, list):
                                shape = shape[0]
                            ishape = tuple(int(x) if x else 1 for x in shape[1:])
                    except Exception:
                        ishape = None
                    if ishape is not None:
                        meta["input_shape"] = ishape
                    _loaded_models[stem_lower] = model
                    _model_meta[stem_lower] = meta
                    _add_aliases(stem_lower, model, meta)
                except Exception as e:
                    _model_meta[stem_lower] = {"error": str(e), "path": str(file)}
                    continue
            else:
                continue
        except Exception as e:
            _model_meta[stem_lower] = {"error": str(e), "path": str(file)}
            continue


@app.route("/api/health")
def health():
    if not _loaded_models:
        load_models()
    return jsonify({"status": "ok", "models": list(_loaded_models.keys()), "tf": _TF_AVAILABLE, "keras": _KERAS_AVAILABLE})


@app.route("/api/models")
def list_models():
    return jsonify(sorted(list(_loaded_models.keys())))


@app.route("/api/models/details")
def model_details():
    return jsonify(_model_meta)


@app.route("/api/session", methods=["GET"])
def session_status():
    user = session.get("user")
    return jsonify({"authenticated": bool(user), "user": user})


@app.route("/api/login", methods=["POST"])
def login():
    payload = request.get_json(silent=True) or {}
    username = (payload.get("username") or "").strip()
    password = (payload.get("password") or "").strip()

    env_user = os.getenv("APP_USERNAME", "admin")
    env_pass = os.getenv("APP_PASSWORD", "admin")

    if username == env_user and password == env_pass:
        session["user"] = username
        return jsonify({"ok": True, "user": username})
    return jsonify({"ok": False, "error": "Invalid credentials"}), 401


@app.route("/api/logout", methods=["POST"])
def logout():
    session.pop("user", None)
    return jsonify({"ok": True})


@app.route("/api/predict/<model_name>", methods=["POST"])
def predict(model_name: str):
    # Optional guard: require authenticated session
    if not session.get("user"):
        return jsonify({"error": "Unauthorized"}), 401
    payload = request.get_json(silent=True) or {}
    
    # Extract parameters
    symbol = payload.get("symbol", model_name.upper())
    days_ahead = int(payload.get("days_ahead", 0))
    hours_ahead = int(payload.get("hours_ahead", 0))
    current_price = payload.get("current_price")
    
    # Validate inputs
    if days_ahead < 0 or days_ahead > CONFIG["DAYS_AHEAD_MAX"]:
        return jsonify({"error": f"days_ahead must be between 0 and {CONFIG['DAYS_AHEAD_MAX']}"}), 400
    if hours_ahead < 0 or hours_ahead > CONFIG["HOURS_AHEAD_MAX"]:
        return jsonify({"error": f"hours_ahead must be between 0 and {CONFIG['HOURS_AHEAD_MAX']}"}), 400
    
    results = {}
    
    # Daily predictions (INR)
    if days_ahead > 0:
        daily_model_key = f"lstm_{symbol.lower()}_daily"
        daily_model = _loaded_models.get(daily_model_key)
        
        if daily_model:
            try:
                # Fetch daily data
                daily_data = fetch_yahoo_finance_data(symbol, CONFIG["YAHOO_FINANCE_DAYS_LIMIT"])
                if daily_data is not None:
                    # Prepare input for daily model
                    X_daily = prepare_model_input(daily_data, 60)
                    if X_daily is not None:
                        # Make prediction
                        y_pred_daily = daily_model.predict(X_daily)
                        daily_prediction = float(y_pred_daily[0][0])
                        
                        results["daily_prediction"] = {
                            "predicted_price": daily_prediction,
                            "currency": CONFIG["DAILY_MODEL_CURRENCY"],
                            "days_ahead": days_ahead,
                            "model_type": "daily_lstm"
                        }
            except Exception as e:
                results["daily_error"] = str(e)
    
    # Hourly predictions (USDT)
    if hours_ahead > 0:
        hourly_model_key = f"lstm_{symbol.lower()}_hourly"
        hourly_model = _loaded_models.get(hourly_model_key)
        
        if hourly_model:
            try:
                # Fetch hourly data
                hourly_data = fetch_binance_hourly_data(symbol, CONFIG["BINANCE_HOURS_LIMIT"])
                if hourly_data is not None:
                    # Prepare input for hourly model
                    X_hourly = prepare_model_input(hourly_data, 60)
                    if X_hourly is not None:
                        # Make prediction
                        y_pred_hourly = hourly_model.predict(X_hourly)
                        hourly_prediction = float(y_pred_hourly[0][0])
                        
                        results["hourly_prediction"] = {
                            "predicted_price": hourly_prediction,
                            "currency": CONFIG["HOURLY_MODEL_CURRENCY"],
                            "hours_ahead": hours_ahead,
                            "model_type": "hourly_lstm"
                        }
            except Exception as e:
                results["hourly_error"] = str(e)
    
    # Get current price if not provided
    if current_price is None:
        if symbol.upper() == "BTC":
            current_price = get_coindesk_price()
        else:
            # Try to get from latest data
            daily_data = fetch_yahoo_finance_data(symbol, 1)
            if daily_data is not None and not daily_data.empty:
                current_price = float(daily_data['Close'].iloc[-1])
    
    if current_price:
        results["current_price"] = current_price
    
    # Fallback predictions if models not available
    if not results.get("daily_prediction") and days_ahead > 0:
        if current_price:
            vol = 0.05  # Daily volatility
            seed = abs(hash(f"{symbol}_daily")) % 1000
            rng = np.random.default_rng(seed)
            trend = float(rng.uniform(-vol/2, vol/2))
            pred = current_price * (1.0 + trend)
            results["daily_prediction"] = {
                "predicted_price": pred,
                "currency": CONFIG["DAILY_MODEL_CURRENCY"],
                "days_ahead": days_ahead,
                "model_type": "fallback"
            }
    
    if not results.get("hourly_prediction") and hours_ahead > 0:
        if current_price:
            vol = 0.02  # Hourly volatility
            seed = abs(hash(f"{symbol}_hourly")) % 1000
            rng = np.random.default_rng(seed)
            trend = float(rng.uniform(-vol/2, vol/2))
            pred = current_price * (1.0 + trend)
            results["hourly_prediction"] = {
                "predicted_price": pred,
                "currency": CONFIG["HOURLY_MODEL_CURRENCY"],
                "hours_ahead": hours_ahead,
                "model_type": "fallback"
            }
    
    return jsonify({
        "symbol": symbol.upper(),
        "timestamp": datetime.now().isoformat(),
        **results
    })


# Frontend
@app.route("/")
def index():
    index_path = FRONTEND_DIR / "index.html"
    if index_path.exists():
        return send_from_directory(str(FRONTEND_DIR), "index.html")
    return jsonify({"message": "Frontend not found"})


@app.route("/<path:path>")
def serve_static(path: str):
    file_path = FRONTEND_DIR / path
    if file_path.exists():
        return send_from_directory(str(FRONTEND_DIR), path)
    return send_from_directory(str(FRONTEND_DIR), "index.html")


if __name__ == "__main__":
    load_models()
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)
