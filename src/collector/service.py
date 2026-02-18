import logging
from datetime import date
from time import sleep
from typing import Any

import requests
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from src.db.models import DailyPrice

logger = logging.getLogger(__name__)


def _to_float(value: Any) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    cleaned = str(value).replace(",", "").strip()
    return float(cleaned) if cleaned else 0.0


def _to_int(value: Any) -> int:
    if isinstance(value, int):
        return value
    cleaned = str(value).replace(",", "").strip()
    return int(float(cleaned)) if cleaned else 0


def fetch_ngx_prices(source_url: str, retries: int = 3, backoff_seconds: int = 2) -> list[dict]:
    for attempt in range(1, retries + 1):
        try:
            response = requests.get(source_url, timeout=15)
            response.raise_for_status()
            payload = response.json()
            return payload.get("data", [])
        except Exception as exc:
            logger.warning("collector failed attempt %s/%s: %s", attempt, retries, exc)
            if attempt < retries:
                sleep(backoff_seconds * attempt)
    logger.error("collector exhausted retries")
    return []


def ingest_prices(db: Session, rows: list[dict], trade_date: date) -> int:
    total = 0
    for row in rows:
        ticker = str(row.get("ticker", "")).strip().upper()
        if not ticker:
            continue
        open_price = _to_float(row.get("open"))
        close_price = _to_float(row.get("close"))
        high_price = _to_float(row.get("high"))
        low_price = _to_float(row.get("low"))
        volume = _to_int(row.get("volume"))
        pct_change = 0.0 if open_price == 0 else ((close_price - open_price) / open_price) * 100

        stmt = insert(DailyPrice).values(
            ticker=ticker,
            trade_date=trade_date,
            open_price=open_price,
            close_price=close_price,
            high_price=high_price,
            low_price=low_price,
            volume=volume,
            percent_change=pct_change,
        )
        stmt = stmt.on_conflict_do_update(
            constraint="uq_daily_ticker_date",
            set_={
                "open_price": open_price,
                "close_price": close_price,
                "high_price": high_price,
                "low_price": low_price,
                "volume": volume,
                "percent_change": pct_change,
            },
        )
        db.execute(stmt)
        total += 1
    db.commit()
    return total
