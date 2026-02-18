from statistics import mean

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from src.db.models import DailyPrice, TechnicalIndicator


def moving_average(values: list[float], period: int) -> float:
    if not values:
        return 0.0
    window = values[-period:]
    return round(mean(window), 4)


def is_volume_spike(volume_today: int, avg_volume_20d: float) -> float:
    if avg_volume_20d <= 0:
        return 0.0
    return 1.0 if volume_today > 1.5 * avg_volume_20d else 0.0


def momentum_score(percent_change: float, volume_today: int, avg_volume_20d: float) -> float:
    volume_factor = 1.0 if avg_volume_20d == 0 else min(volume_today / avg_volume_20d, 3)
    return round(percent_change * volume_factor, 4)


def calculate_and_store_indicators(db: Session) -> int:
    tickers = db.scalars(select(DailyPrice.ticker).distinct()).all()
    count = 0

    for ticker in tickers:
        prices = db.scalars(
            select(DailyPrice)
            .where(DailyPrice.ticker == ticker)
            .order_by(DailyPrice.trade_date.asc())
        ).all()
        closes = [p.close_price for p in prices]
        volumes = [p.volume for p in prices]
        for idx, price in enumerate(prices):
            close_slice = closes[: idx + 1]
            vol_slice = volumes[: idx + 1]
            ma20 = moving_average(close_slice, 20)
            ma50 = moving_average(close_slice, 50)
            avg20v = mean(vol_slice[-20:]) if vol_slice else 0
            v_spike = is_volume_spike(price.volume, avg20v)
            mom = momentum_score(price.percent_change, price.volume, avg20v)

            stmt = insert(TechnicalIndicator).values(
                ticker=ticker,
                trade_date=price.trade_date,
                ma20=ma20,
                ma50=ma50,
                volume_spike_score=v_spike,
                momentum_score=mom,
            )
            stmt = stmt.on_conflict_do_update(
                constraint="uq_ti_ticker_date",
                set_={
                    "ma20": ma20,
                    "ma50": ma50,
                    "volume_spike_score": v_spike,
                    "momentum_score": mom,
                },
            )
            db.execute(stmt)
            count += 1
    db.commit()
    return count


def sector_momentum(db: Session):
    q = (
        select(func.coalesce(func.avg(TechnicalIndicator.momentum_score), 0), DailyPrice.ticker)
        .join(
            DailyPrice,
            (TechnicalIndicator.ticker == DailyPrice.ticker)
            & (TechnicalIndicator.trade_date == DailyPrice.trade_date),
        )
        .group_by(DailyPrice.ticker)
        .order_by(func.avg(TechnicalIndicator.momentum_score).desc())
        .limit(5)
    )
    rows = db.execute(q).all()
    return [{"ticker": r[1], "momentum": round(r[0], 4)} for r in rows]
