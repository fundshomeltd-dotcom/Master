from datetime import date

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from src.analytics.engine import sector_momentum
from src.config.settings import settings
from src.db.models import AIInsight, TechnicalIndicator

BANNED_WORDS = {"buy", "sell", "target", "guarantee", "guaranteed"}


def _sanitize(text: str) -> str:
    out = text
    for word in BANNED_WORDS:
        out = out.replace(word, "")
        out = out.replace(word.capitalize(), "")
    return " ".join(out.split())


def build_insight_text(mood: str, risk: str, sector: str, signal: str) -> tuple[str, str]:
    long_txt = (
        f"Market Mood: {mood}. Risk Level: {risk}. Top Momentum Sector: {sector}. "
        f"AI Signal Summary: {signal}. {settings.disclaimer}"
    )
    long_txt = _sanitize(long_txt)
    ussd = f"Mood:{mood} Risk:{risk} Sector:{sector} Signal:{signal}. {settings.disclaimer}"
    ussd = _sanitize(ussd)[:160]
    return long_txt, ussd


def generate_daily_insight(db: Session) -> AIInsight:
    latest = db.scalars(
        select(TechnicalIndicator).order_by(desc(TechnicalIndicator.trade_date)).limit(100)
    ).all()

    avg_mom = sum(item.momentum_score for item in latest) / len(latest) if latest else 0
    avg_spike = sum(item.volume_spike_score for item in latest) / len(latest) if latest else 0

    mood = "Positive" if avg_mom > 0 else "Mixed"
    risk = "Elevated" if avg_spike > 0.35 else "Moderate"

    leaders = sector_momentum(db)
    sector = leaders[0]["ticker"] if leaders else "Broad Market"
    signal = "Momentum is active with selective participation" if avg_mom > 0 else "Range-bound action with cautious activity"

    long_txt, ussd = build_insight_text(mood, risk, sector, signal)

    insight = db.scalar(select(AIInsight).where(AIInsight.insight_date == date.today()))
    if not insight:
        insight = AIInsight(insight_date=date.today(), market_sentiment=mood, risk_level=risk, sector_leader=sector, insight_text=long_txt, ussd_text=ussd)
        db.add(insight)
    else:
        insight.market_sentiment = mood
        insight.risk_level = risk
        insight.sector_leader = sector
        insight.insight_text = long_txt
        insight.ussd_text = ussd
    db.commit()
    db.refresh(insight)
    return insight
