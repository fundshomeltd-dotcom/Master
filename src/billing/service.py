from sqlalchemy.orm import Session

from src.db.models import Subscriber


def verify_active_subscription(db: Session, msisdn: str) -> bool:
    s = db.get(Subscriber, msisdn)
    return bool(s and s.subscription_status == "active")


def create_subscription(db: Session, msisdn: str, plan_type: str = "daily") -> Subscriber:
    s = db.get(Subscriber, msisdn)
    if s:
        s.subscription_status = "active"
        s.plan_type = plan_type
    else:
        s = Subscriber(msisdn=msisdn, subscription_status="active", plan_type=plan_type)
        db.add(s)
    db.commit()
    db.refresh(s)
    return s


def deactivate_subscription(db: Session, msisdn: str) -> Subscriber | None:
    s = db.get(Subscriber, msisdn)
    if not s:
        return None
    s.subscription_status = "inactive"
    db.commit()
    db.refresh(s)
    return s


def process_billing_webhook(db: Session, payload: dict) -> dict:
    msisdn = payload.get("msisdn", "")
    event = payload.get("event", "")
    if event == "charged":
        sub = create_subscription(db, msisdn)
        return {"status": "ok", "subscription": sub.subscription_status}
    if event == "failed":
        sub = deactivate_subscription(db, msisdn)
        return {"status": "ok", "subscription": sub.subscription_status if sub else "inactive"}
    return {"status": "ignored"}
