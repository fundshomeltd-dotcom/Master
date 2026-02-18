from datetime import date

from apscheduler.schedulers.background import BackgroundScheduler

from src.ai_engine.insight_service import generate_daily_insight
from src.analytics.engine import calculate_and_store_indicators
from src.collector.service import fetch_ngx_prices, ingest_prices
from src.config.settings import settings
from src.db.session import SessionLocal

scheduler = BackgroundScheduler()


def daily_pipeline():
    db = SessionLocal()
    try:
        rows = fetch_ngx_prices(settings.collector_source_url)
        ingest_prices(db, rows, date.today())
        calculate_and_store_indicators(db)
        generate_daily_insight(db)
    finally:
        db.close()


def start_scheduler() -> None:
    scheduler.add_job(daily_pipeline, "interval", minutes=settings.scheduler_interval_minutes, id="daily_pipeline", replace_existing=True)
    scheduler.start()
