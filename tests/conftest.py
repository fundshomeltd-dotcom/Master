from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.db.base import Base
from src.db.models import AIInsight, DailyPrice
from src.db.session import get_db
from src.main import app


@pytest.fixture
def client():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    db = TestingSessionLocal()
    db.add(AIInsight(insight_date=date.today(), market_sentiment="Mixed", risk_level="Moderate", sector_leader="BANKING", insight_text="Market information only. Not financial advice.", ussd_text="Mood:Mixed Risk:Moderate. Market information only. Not financial advice."))
    db.add(DailyPrice(ticker="AAA", trade_date=date.today(), open_price=10, close_price=11, high_price=12, low_price=9, volume=2000, percent_change=10))
    db.add(DailyPrice(ticker="BBB", trade_date=date.today(), open_price=10, close_price=10.2, high_price=10.4, low_price=9.8, volume=1000, percent_change=2))
    db.commit()
    db.close()

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
