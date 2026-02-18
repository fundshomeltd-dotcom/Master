from datetime import date, datetime

from sqlalchemy import Date, DateTime, Float, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.db.base import Base


class StockMaster(Base):
    __tablename__ = "stocks_master"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    ticker: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    company_name: Mapped[str] = mapped_column(String(120))
    sector: Mapped[str] = mapped_column(String(80))


class DailyPrice(Base):
    __tablename__ = "daily_prices"
    __table_args__ = (UniqueConstraint("ticker", "trade_date", name="uq_daily_ticker_date"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    ticker: Mapped[str] = mapped_column(String(20), index=True)
    trade_date: Mapped[date] = mapped_column(Date, index=True)
    open_price: Mapped[float] = mapped_column(Float)
    close_price: Mapped[float] = mapped_column(Float)
    high_price: Mapped[float] = mapped_column(Float)
    low_price: Mapped[float] = mapped_column(Float)
    volume: Mapped[int] = mapped_column(Integer)
    percent_change: Mapped[float] = mapped_column(Float)


class TechnicalIndicator(Base):
    __tablename__ = "technical_indicators"
    __table_args__ = (UniqueConstraint("ticker", "trade_date", name="uq_ti_ticker_date"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    ticker: Mapped[str] = mapped_column(String(20), index=True)
    trade_date: Mapped[date] = mapped_column(Date, index=True)
    ma20: Mapped[float] = mapped_column(Float)
    ma50: Mapped[float] = mapped_column(Float)
    volume_spike_score: Mapped[float] = mapped_column(Float)
    momentum_score: Mapped[float] = mapped_column(Float)


class AIInsight(Base):
    __tablename__ = "ai_insights"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    insight_date: Mapped[date] = mapped_column(Date, unique=True, index=True)
    market_sentiment: Mapped[str] = mapped_column(String(20))
    risk_level: Mapped[str] = mapped_column(String(20))
    sector_leader: Mapped[str] = mapped_column(String(80))
    insight_text: Mapped[str] = mapped_column(String(500))
    ussd_text: Mapped[str] = mapped_column(String(160))


class Subscriber(Base):
    __tablename__ = "subscribers"

    msisdn: Mapped[str] = mapped_column(String(20), primary_key=True)
    subscription_status: Mapped[str] = mapped_column(String(20), default="inactive")
    plan_type: Mapped[str] = mapped_column(String(20), default="daily")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
