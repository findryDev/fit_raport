from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models.user import User
from app.services import metrics as metrics_service
from app.services.history import RANGE_DAYS, entry_by_id, history_entries
from app.templating import templates

router = APIRouter(prefix="/reports")


def _get_metric_or_404(slug: str) -> metrics_service.MetricConfig:
    config = metrics_service.METRICS.get(slug)
    if not config or config.model is None:
        raise HTTPException(status_code=404, detail="Nieznany parametr")
    return config


def _entry_kwargs(slug: str, value, systolic, diastolic, pulse, context, note) -> dict:
    if slug == "waga":
        return {"value_kg": value, "note": note}
    if slug == "cisnienie":
        return {"systolic": systolic, "diastolic": diastolic, "pulse": pulse, "note": note}
    if slug == "tetno":
        return {"bpm": value, "context": context or "resting", "note": note}
    if slug == "cukier":
        return {"value_mg_dl": value, "context": context or "random", "note": note}
    raise HTTPException(status_code=404, detail="Nieznany parametr")


@router.get("/{slug}")
def report_detail(
    slug: str,
    request: Request,
    range: str = "90d",
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if slug not in metrics_service.METRICS:
        raise HTTPException(status_code=404, detail="Nieznany parametr")
    config = metrics_service.METRICS[slug]
    source_model = config.model or metrics_service.METRICS["waga"].model

    if range not in RANGE_DAYS:
        range = "90d"
    days = RANGE_DAYS[range]
    since = datetime.now(timezone.utc) - timedelta(days=days) if days else None

    entries = history_entries(db, source_model, user.id, since=since)
    values = [v for v in (metrics_service.value_of(slug, e, user.height_cm) for e in entries) if v is not None]

    stats = None
    if values:
        stats = {"min": min(values), "max": max(values), "avg": round(sum(values) / len(values), 1)}

    rows = [
        {
            "id": e.id,
            "measured_at": e.measured_at,
            "display_value": metrics_service.display_value(slug, e, user.height_cm),
            "classification": metrics_service.classify(slug, e, user.height_cm),
            "note": e.note,
            "editable": config.model is not None,
        }
        for e in reversed(entries)
    ]

    return templates.TemplateResponse(
        "report_detail.html",
        {
            "request": request,
            "user": user,
            "slug": slug,
            "config": config,
            "range": range,
            "range_options": list(RANGE_DAYS.keys()),
            "chart_data": metrics_service.chart_series(slug, entries, user.height_cm),
            "stats": stats,
            "rows": rows,
            "is_virtual": config.model is None,
        },
    )


@router.post("/{slug}/add")
def add_entry(
    slug: str,
    request: Request,
    value: float | None = Form(default=None),
    systolic: int | None = Form(default=None),
    diastolic: int | None = Form(default=None),
    pulse: int | None = Form(default=None),
    context: str | None = Form(default=None),
    measured_at: str | None = Form(default=None),
    note: str | None = Form(default=None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    config = _get_metric_or_404(slug)
    when = datetime.fromisoformat(measured_at) if measured_at else datetime.now(timezone.utc)
    if when.tzinfo is None:
        when = when.replace(tzinfo=timezone.utc)

    kwargs = _entry_kwargs(slug, value, systolic, diastolic, pulse, context, note or None)
    entry = config.model(user_id=user.id, measured_at=when, source="manual", **kwargs)
    db.add(entry)
    db.commit()
    return RedirectResponse(f"/reports/{slug}", status_code=303)


@router.get("/{slug}/{entry_id}/edit")
def edit_entry_form(
    slug: str,
    entry_id: int,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    config = _get_metric_or_404(slug)
    entry = entry_by_id(db, config.model, user.id, entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Wpis nie znaleziony")
    return templates.TemplateResponse(
        "edit_entry.html", {"request": request, "user": user, "slug": slug, "config": config, "entry": entry}
    )


@router.post("/{slug}/{entry_id}/edit")
def edit_entry_submit(
    slug: str,
    entry_id: int,
    request: Request,
    value: float | None = Form(default=None),
    systolic: int | None = Form(default=None),
    diastolic: int | None = Form(default=None),
    pulse: int | None = Form(default=None),
    context: str | None = Form(default=None),
    measured_at: str | None = Form(default=None),
    note: str | None = Form(default=None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    config = _get_metric_or_404(slug)
    entry = entry_by_id(db, config.model, user.id, entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Wpis nie znaleziony")

    when = datetime.fromisoformat(measured_at) if measured_at else entry.measured_at
    if when.tzinfo is None:
        when = when.replace(tzinfo=timezone.utc)

    for key, val in _entry_kwargs(slug, value, systolic, diastolic, pulse, context, note or None).items():
        setattr(entry, key, val)
    entry.measured_at = when
    db.commit()
    return RedirectResponse(f"/reports/{slug}", status_code=303)


@router.post("/{slug}/{entry_id}/delete")
def delete_entry(
    slug: str,
    entry_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    config = _get_metric_or_404(slug)
    entry = entry_by_id(db, config.model, user.id, entry_id)
    if entry:
        db.delete(entry)
        db.commit()
    return RedirectResponse(f"/reports/{slug}", status_code=303)
