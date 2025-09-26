"""
API routes for FutureCoin application.
"""
import os
import json
import numpy as np
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, session, render_template_string
from werkzeug.security import check_password_hash, generate_password_hash
from typing import Dict, Any, Optional

from config import CONFIG, FRONTEND_DIR
from database import (
    init_db, insert_login_event, insert_prediction_event, 
    get_user_predictions, get_user_by_username, create_user
)
from model_loader import load_models, get_model, get_model_info, get_available_models, predict_with_model, get_model_status
from data_fetchers import (
    get_historical_data, prepare_model_data, fetch_current_price,
    evaluate_prediction_accuracy
)

# Create blueprint
api = Blueprint('api', __name__)


@api.route("/api/health", methods=["GET"])
def health():
    """Health check endpoint."""
    try:
        # Load models if not already loaded
        from model_loader import models
        if not models:
            load_models()
        
        model_status = get_model_status()
        
        return jsonify({
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "models": {
                "total": model_status["total_models"],
                "loaded": model_status["loaded_models"],
                "status": model_status["status"]
            },
            "config": {
                "use_async_eval": CONFIG["USE_ASYNC_EVAL"],
                "daily_currency": CONFIG["DAILY_MODEL_CURRENCY"],
                "hourly_currency": CONFIG["HOURLY_MODEL_CURRENCY"]
            }
        })
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500


@api.route("/api/models", methods=["GET"])
def get_models():
    """Get available models."""
    try:
        # Load models if not already loaded
        from model_loader import models
        if not models:
            load_models()
        
        model_list = get_available_models()
        return jsonify({"models": model_list})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api.route("/api/models/details", methods=["GET"])
def get_model_details():
    """Get detailed model information."""
    try:
        # Load models if not already loaded
        from model_loader import models
        if not models:
            load_models()
        
        model_list = get_available_models()
        return jsonify({"models": model_list})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api.route("/api/login", methods=["POST"])
def login():
    """User login endpoint."""
    try:
        data = request.get_json()
        username = data.get("username", "").strip()
        password = data.get("password", "").strip()
        
        if not username or not password:
            return jsonify({"error": "Username and password required"}), 400
        
        # Check admin credentials
        if username == CONFIG["APP_USERNAME"] and password == CONFIG["APP_PASSWORD"]:
            session["user"] = username
            session["is_admin"] = True
            
            # Log login event
            insert_login_event(
                username, 
                request.remote_addr, 
                request.headers.get("User-Agent", "")
            )
            
            return jsonify({"message": "Login successful", "is_admin": True})
        
        # Check registered user credentials
        user = get_user_by_username(username)
        if user and check_password_hash(user["password_hash"], password):
            session["user"] = username
            session["is_admin"] = False
            
            # Log login event
            insert_login_event(
                username, 
                request.remote_addr, 
                request.headers.get("User-Agent", "")
            )
            
            return jsonify({"message": "Login successful", "is_admin": False})
        
        return jsonify({"error": "Invalid credentials"}), 401
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api.route("/api/register", methods=["POST"])
def register():
    """User registration endpoint."""
    try:
        data = request.get_json()
        username = data.get("username", "").strip()
        password = data.get("password", "").strip()
        
        if not username or not password:
            return jsonify({"error": "Username and password required"}), 400
        
        if len(username) < 3:
            return jsonify({"error": "Username must be at least 3 characters"}), 400
        
        if len(password) < 6:
            return jsonify({"error": "Password must be at least 6 characters"}), 400
        
        # Check if user already exists
        if get_user_by_username(username):
            return jsonify({"error": "Username already exists"}), 400
        
        # Create user
        password_hash = generate_password_hash(password)
        if create_user(username, password_hash):
            return jsonify({"message": "Registration successful"})
        else:
            return jsonify({"error": "Failed to create user"}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api.route("/api/logout", methods=["POST"])
def logout():
    """User logout endpoint."""
    session.clear()
    return jsonify({"message": "Logged out successfully"})


@api.route("/api/predict", methods=["POST"])
def predict():
    """Make cryptocurrency price predictions."""
    try:
        if not session.get("user"):
            return jsonify({"error": "Unauthorized"}), 401
        
        data = request.get_json()
        symbol = data.get("symbol", "").strip().upper()
        days_ahead = int(data.get("days_ahead", 0))
        hours_ahead = int(data.get("hours_ahead", 0))
        
        if not symbol:
            return jsonify({"error": "Symbol required"}), 400
        
        if days_ahead < 0 or days_ahead > CONFIG["DAYS_AHEAD_MAX"]:
            return jsonify({"error": f"Days ahead must be 0-{CONFIG['DAYS_AHEAD_MAX']}"}), 400
        
        if hours_ahead < 0 or hours_ahead > CONFIG["HOURS_AHEAD_MAX"]:
            return jsonify({"error": f"Hours ahead must be 0-{CONFIG['HOURS_AHEAD_MAX']}"}), 400
        
        if days_ahead == 0 and hours_ahead == 0:
            return jsonify({"error": "Either days_ahead or hours_ahead must be > 0"}), 400
        
        # Load models if not already loaded
        from model_loader import models
        if not models:
            load_models()
        
        predictions = {}
        
        # Daily prediction
        if days_ahead > 0:
            daily_model_info = get_model_info(symbol, "daily")
            if daily_model_info and daily_model_info.get("loaded"):
                daily_data = get_historical_data(symbol, "daily", CONFIG["YAHOO_FINANCE_DAYS_LIMIT"])
                if daily_data is not None:
                    model_data = prepare_model_data(daily_data, 30)  # Daily models use 30-day sequences
                    if model_data is not None:
                        daily_pred = predict_with_model(
                            daily_model_info["model"], 
                            model_data, 
                            30,
                            daily_model_info.get("is_dummy", False)
                        )
                        if daily_pred is not None:
                            predictions["daily_prediction"] = daily_pred
        
        # Hourly prediction
        if hours_ahead > 0:
            hourly_model_info = get_model_info(symbol, "hourly")
            if hourly_model_info and hourly_model_info.get("loaded"):
                hourly_data = get_historical_data(symbol, "hourly", CONFIG["BINANCE_HOURS_LIMIT"])
                if hourly_data is not None:
                    model_data = prepare_model_data(hourly_data, 60)  # Hourly models use 60-hour sequences
                    if model_data is not None:
                        hourly_pred = predict_with_model(
                            hourly_model_info["model"], 
                            model_data, 
                            60,
                            hourly_model_info.get("is_dummy", False)
                        )
                        if hourly_pred is not None:
                            predictions["hourly_prediction"] = hourly_pred
        
        if not predictions:
            return jsonify({"error": "No predictions available for this symbol"}), 400
        
        # Add metadata
        predictions.update({
            "symbol": symbol,
            "days_ahead": days_ahead,
            "hours_ahead": hours_ahead,
            "daily_currency": CONFIG["DAILY_MODEL_CURRENCY"],
            "hourly_currency": CONFIG["HOURLY_MODEL_CURRENCY"],
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Log prediction
        prediction_id = insert_prediction_event(
            session["user"],
            symbol,
            days_ahead,
            hours_ahead,
            predictions.get("daily_prediction"),
            predictions.get("hourly_prediction"),
            data,
            predictions
        )
        
        predictions["prediction_id"] = prediction_id
        
        # Schedule async evaluation if enabled
        if CONFIG["USE_ASYNC_EVAL"]:
            try:
                from tasks import evaluate_prediction
                target_time = datetime.utcnow() + timedelta(days=days_ahead, hours=hours_ahead)
                evaluate_prediction.apply_async(
                    args=[prediction_id, session["user"], symbol, target_time.isoformat()],
                    eta=target_time
                )
            except Exception as e:
                print(f"Failed to schedule async evaluation: {e}")
        
        return jsonify(predictions)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api.route("/api/predictions/history", methods=["GET"])
def get_prediction_history():
    """Get prediction history for the logged-in user."""
    try:
        if not session.get("user"):
            return jsonify({"error": "Unauthorized"}), 401
        
        username = session["user"]
        limit = request.args.get("limit", type=int, default=20)
        symbol_filter = request.args.get("symbol", type=str, default="").upper()
        
        predictions = get_user_predictions(username, limit)
        
        # Filter by symbol if provided
        if symbol_filter:
            predictions = [p for p in predictions if symbol_filter in p["symbol"]]
        
        return jsonify({"items": predictions})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api.route("/api/current-price/<symbol>", methods=["GET"])
def get_current_price(symbol):
    """Get current price for a symbol."""
    try:
        price = fetch_current_price(symbol.upper())
        if price is not None:
            return jsonify({"symbol": symbol.upper(), "price": price})
        else:
            return jsonify({"error": "Price not available"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Static file serving
@api.route("/")
def index():
    """Serve the main index page."""
    try:
        index_path = FRONTEND_DIR / "index.html"
        if index_path.exists():
            return index_path.read_text(encoding="utf-8")
        else:
            return "Frontend files not found", 404
    except Exception as e:
        return f"Error serving index: {e}", 500


@api.route("/<path:filename>")
def serve_static(filename):
    """Serve static files from the frontend directory."""
    try:
        file_path = FRONTEND_DIR / filename
        if file_path.exists() and file_path.is_file():
            return file_path.read_text(encoding="utf-8")
        else:
            return "File not found", 404
    except Exception as e:
        return f"Error serving file: {e}", 500
