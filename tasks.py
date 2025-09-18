import os
import sqlite3
from datetime import datetime
import json
import requests

from celery import Celery

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "app.db")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery = Celery(__name__, broker=REDIS_URL, backend=REDIS_URL)


def _fetch_actual_price(symbol: str) -> float | None:
    try:
        if symbol.upper() == "BTC":
            resp = requests.get("https://api.coindesk.com/v1/bpi/currentprice.json", timeout=5)
            resp.raise_for_status()
            data = resp.json()
            return float(data["bpi"]["USD"]["rate_float"])  # type: ignore
        # Fallback using Yahoo via yfinance API is in app; here keep it light
        return None
    except Exception:
        return None


@celery.task(name="tasks.evaluate_prediction")
def evaluate_prediction(
    prediction_id: int,
    username: str,
    symbol: str,
    daily_prediction: float | None,
    hourly_prediction: float | None,
):
    actual = _fetch_actual_price(symbol)
    if actual is None:
        return {"ok": False, "error": "actual price fetch failed"}

    # Compute basic errors against whichever prediction exists (prefer daily)
    pred = daily_prediction if daily_prediction is not None else hourly_prediction
    mae = abs(actual - pred) if pred is not None else None
    ape = (abs(actual - pred) / actual * 100.0) if (pred is not None and actual) else None

    try:
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO prediction_evaluations (
                    prediction_id, username, symbol, target_time,
                    actual_price, daily_prediction, hourly_prediction,
                    mae, ape, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    int(prediction_id),
                    username,
                    symbol.upper(),
                    datetime.utcnow().isoformat(),
                    float(actual),
                    float(daily_prediction) if daily_prediction is not None else None,
                    float(hourly_prediction) if hourly_prediction is not None else None,
                    float(mae) if mae is not None else None,
                    float(ape) if ape is not None else None,
                    datetime.utcnow().isoformat(),
                ),
            )
            conn.commit()
    except Exception as e:
        return {"ok": False, "error": str(e)}

    return {
        "ok": True,
        "prediction_id": prediction_id,
        "actual_price": actual,
        "mae": mae,
        "ape": ape,
    }


