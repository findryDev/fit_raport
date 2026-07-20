from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_api_user
from app.models.measurements import BloodPressureEntry, GlucoseEntry, HeartRateEntry, WeightEntry
from app.models.user import User
from app.schemas.measurements import (
    BloodPressureIn,
    BloodPressureOut,
    GlucoseIn,
    GlucoseOut,
    HeartRateIn,
    HeartRateOut,
    WeightIn,
    WeightOut,
)
from app.services.history import history_entries

router = APIRouter(prefix="/api/v1", tags=["measurements"])


def _measured_at(value: datetime | None) -> datetime:
    when = value or datetime.now(timezone.utc)
    if when.tzinfo is None:
        when = when.replace(tzinfo=timezone.utc)
    return when


@router.post("/weight", response_model=WeightOut, status_code=201)
def add_weight(payload: WeightIn, user: User = Depends(get_api_user), db: Session = Depends(get_db)):
    entry = WeightEntry(
        user_id=user.id,
        value_kg=payload.value_kg,
        measured_at=_measured_at(payload.measured_at),
        note=payload.note,
        source="api",
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


@router.get("/weight", response_model=list[WeightOut])
def list_weight(user: User = Depends(get_api_user), db: Session = Depends(get_db)):
    return history_entries(db, WeightEntry, user.id)


@router.post("/blood-pressure", response_model=BloodPressureOut, status_code=201)
def add_blood_pressure(
    payload: BloodPressureIn, user: User = Depends(get_api_user), db: Session = Depends(get_db)
):
    entry = BloodPressureEntry(
        user_id=user.id,
        systolic=payload.systolic,
        diastolic=payload.diastolic,
        pulse=payload.pulse,
        measured_at=_measured_at(payload.measured_at),
        note=payload.note,
        source="api",
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


@router.get("/blood-pressure", response_model=list[BloodPressureOut])
def list_blood_pressure(user: User = Depends(get_api_user), db: Session = Depends(get_db)):
    return history_entries(db, BloodPressureEntry, user.id)


@router.post("/heart-rate", response_model=HeartRateOut, status_code=201)
def add_heart_rate(payload: HeartRateIn, user: User = Depends(get_api_user), db: Session = Depends(get_db)):
    entry = HeartRateEntry(
        user_id=user.id,
        bpm=payload.bpm,
        context=payload.context,
        measured_at=_measured_at(payload.measured_at),
        note=payload.note,
        source="api",
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


@router.get("/heart-rate", response_model=list[HeartRateOut])
def list_heart_rate(user: User = Depends(get_api_user), db: Session = Depends(get_db)):
    return history_entries(db, HeartRateEntry, user.id)


@router.post("/glucose", response_model=GlucoseOut, status_code=201)
def add_glucose(payload: GlucoseIn, user: User = Depends(get_api_user), db: Session = Depends(get_db)):
    entry = GlucoseEntry(
        user_id=user.id,
        value_mg_dl=payload.value_mg_dl,
        context=payload.context,
        measured_at=_measured_at(payload.measured_at),
        note=payload.note,
        source="api",
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


@router.get("/glucose", response_model=list[GlucoseOut])
def list_glucose(user: User = Depends(get_api_user), db: Session = Depends(get_db)):
    return history_entries(db, GlucoseEntry, user.id)
