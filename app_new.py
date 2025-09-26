"""
FutureCoin - AI-powered cryptocurrency price prediction application.
Refactored into modular structure for better maintainability.
"""
import os
from flask import Flask
from config import CONFIG
from database import init_db
from model_loader import load_models
from routes import api

# Flask app configuration
app = Flask(__name__)
app.secret_key = CONFIG["FLASK_SECRET_KEY"]

# Register API blueprint
app.register_blueprint(api)


def main():
    """Main application entry point."""
    # Initialize database
    init_db()
    
    # Load models
    load_models()
    
    # Start Flask app
    port = CONFIG["PORT"]
    debug = os.getenv("FLASK_DEBUG", "True") == "True"
    
    print(f"Starting FutureCoin server on port {port}")
    print(f"Debug mode: {debug}")
    print(f"Async evaluation: {CONFIG['USE_ASYNC_EVAL']}")
    
    app.run(host="0.0.0.0", port=port, debug=debug)


if __name__ == "__main__":
    main()
