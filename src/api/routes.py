from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from src.ai_engine.insight_service import generate_daily_insight
from src.analytics.engine import sector_momentum
from src.db.models import AIInsight, DailyPrice
from src.db.session import get_db
from src.ussd.formatter import optimize_ussd_text

router = APIRouter()


@router.get("/insight/today")
def insight_today(db: Session = Depends(get_db)):
    insight = db.scalar(select(AIInsight).where(AIInsight.insight_date == date.today()))
    if not insight:
        insight = generate_daily_insight(db)
    return {
        "date": str(insight.insight_date),
        "market_sentiment": insight.market_sentiment,
        "risk_level": insight.risk_level,
        "sector_leader": insight.sector_leader,
        "insight_text": insight.insight_text,
    }


@router.get("/insight/ussd")
def insight_ussd(db: Session = Depends(get_db)):
    insight = db.scalar(select(AIInsight).where(AIInsight.insight_date == date.today()))
    if not insight:
        insight = generate_daily_insight(db)
    return {"message": optimize_ussd_text(insight.ussd_text)}


@router.get("/stocks/top-gainers")
def top_gainers(db: Session = Depends(get_db), limit: int = 5):
    rows = db.scalars(select(DailyPrice).order_by(desc(DailyPrice.percent_change)).limit(limit)).all()
    return [
        {
            "ticker": r.ticker,
            "trade_date": str(r.trade_date),
            "percent_change": r.percent_change,
            "close_price": r.close_price,
        }
        for r in rows
    ]


@router.get("/risk-level")
def risk_level(db: Session = Depends(get_db)):
    insight = db.scalar(select(AIInsight).where(AIInsight.insight_date == date.today()))
    if not insight:
        raise HTTPException(status_code=404, detail="No insight generated")
    return {"risk_level": insight.risk_level}


@router.get("/sector/momentum")
def sector_momentum_view(db: Session = Depends(get_db)):
    return {"leaders": sector_momentum(db)}
