"""
Database operations for FutureCoin application.
"""
import sqlite3
from datetime import datetime
from typing import Dict, Any, Optional, List
import json
from config import DB_PATH


def init_db() -> None:
    """Initialize the SQLite database with required tables."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.cursor()
            
            # Login audit table
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS logins (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    ip TEXT,
                    user_agent TEXT,
                    created_at TEXT NOT NULL
                )
                """
            )
            
            # Users table for registered users
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            
            # Predictions table
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS predictions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    days_ahead INTEGER NOT NULL,
                    hours_ahead INTEGER NOT NULL,
                    daily_prediction REAL,
                    hourly_prediction REAL,
                    request_payload TEXT,
                    response_payload TEXT,
                    created_at TEXT NOT NULL
                )
                """
            )
            
            # Prediction evaluations table
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS prediction_evaluations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    prediction_id INTEGER NOT NULL,
                    username TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    target_time TEXT NOT NULL,
                    actual_price REAL NOT NULL,
                    daily_prediction REAL,
                    hourly_prediction REAL,
                    mae REAL,
                    ape REAL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (prediction_id) REFERENCES predictions(id)
                )
                """
            )
            
            conn.commit()
    except Exception as e:
        print(f"DB init error: {e}")


def insert_login_event(username: str, ip: str, user_agent: str) -> None:
    """Insert a login event into the database."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO logins (username, ip, user_agent, created_at) VALUES (?, ?, ?, ?)",
                (username, ip, user_agent, datetime.utcnow().isoformat()),
            )
            conn.commit()
    except Exception as e:
        print(f"DB insert error: {e}")


def insert_prediction_event(
    username: str,
    symbol: str,
    days_ahead: int,
    hours_ahead: int,
    daily_prediction: Optional[float],
    hourly_prediction: Optional[float],
    request_payload: Dict[str, Any],
    response_payload: Dict[str, Any],
) -> int:
    """Insert a prediction event into the database."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO predictions (
                    username, symbol, days_ahead, hours_ahead,
                    daily_prediction, hourly_prediction,
                    request_payload, response_payload, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    username,
                    symbol.upper(),
                    int(days_ahead),
                    int(hours_ahead),
                    float(daily_prediction) if daily_prediction is not None else None,
                    float(hourly_prediction) if hourly_prediction is not None else None,
                    json.dumps(request_payload, ensure_ascii=False),
                    json.dumps(response_payload, ensure_ascii=False),
                    datetime.utcnow().isoformat(),
                ),
            )
            conn.commit()
            return cur.lastrowid
    except Exception as e:
        print(f"DB prediction insert error: {e}")
    return 0


def get_user_predictions(username: str, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
    """Get prediction history for a user."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute(
                """
                SELECT id, username, symbol, days_ahead, hours_ahead,
                       daily_prediction, hourly_prediction,
                       request_payload, response_payload, created_at
                FROM predictions
                WHERE username = ?
                ORDER BY datetime(created_at) DESC
                LIMIT ? OFFSET ?
                """,
                (username, limit, offset),
            )
            rows = cur.fetchall()
            results = []
            for r in rows:
                results.append({
                    "id": r["id"],
                    "username": r["username"],
                    "symbol": r["symbol"],
                    "days_ahead": r["days_ahead"],
                    "hours_ahead": r["hours_ahead"],
                    "daily_prediction": r["daily_prediction"],
                    "hourly_prediction": r["hourly_prediction"],
                    "created_at": r["created_at"],
                })
            return results
    except Exception as e:
        print(f"DB get predictions error: {e}")
        return []


def get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
    """Get user by username."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute("SELECT * FROM users WHERE username = ?", (username,))
            row = cur.fetchone()
            if row:
                return dict(row)
    except Exception as e:
        print(f"DB get user error: {e}")
    return None


def create_user(username: str, password_hash: str) -> bool:
    """Create a new user."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO users (username, password_hash, created_at) VALUES (?, ?, ?)",
                (username, password_hash, datetime.utcnow().isoformat()),
            )
            conn.commit()
            return True
    except sqlite3.IntegrityError:
        return False
    except Exception as e:
        print(f"DB create user error: {e}")
        return False
