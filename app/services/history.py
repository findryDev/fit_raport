from datetime import datetime

from sqlalchemy.orm import Session

RANGE_DAYS = {"7d": 7, "30d": 30, "90d": 90, "1y": 365, "all": None}


def latest_entry(db: Session, model, user_id: int):
    return (
        db.query(model)
        .filter(model.user_id == user_id)
        .order_by(model.measured_at.desc())
        .first()
    )


def previous_entry(db: Session, model, user_id: int, before: datetime):
    return (
        db.query(model)
        .filter(model.user_id == user_id, model.measured_at < before)
        .order_by(model.measured_at.desc())
        .first()
    )


def history_entries(db: Session, model, user_id: int, since: datetime | None = None):
    query = db.query(model).filter(model.user_id == user_id)
    if since is not None:
        query = query.filter(model.measured_at >= since)
    return query.order_by(model.measured_at.asc()).all()


def entry_by_id(db: Session, model, user_id: int, entry_id: int):
    return (
        db.query(model)
        .filter(model.id == entry_id, model.user_id == user_id)
        .first()
    )
