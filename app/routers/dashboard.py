from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models.user import User
from app.services import metrics as metrics_service
from app.services.history import history_entries, latest_entry, previous_entry
from app.templating import templates

router = APIRouter()

SPARKLINE_DAYS = 30


def _trend(current: float | None, previous: float | None) -> str | None:
    if current is None or previous is None:
        return None
    if current > previous:
        return "up"
    if current < previous:
        return "down"
    return "flat"


@router.get("/")
def dashboard(request: Request, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    since = datetime.now(timezone.utc) - timedelta(days=SPARKLINE_DAYS)
    cards = []

    for slug, config in metrics_service.METRICS.items():
        # BMI jest liczone z wpisów wagi, więc korzysta z tego samego modelu co "waga"
        source_model = config.model or metrics_service.METRICS["waga"].model
        latest = latest_entry(db, source_model, user.id)
        previous = None
        sparkline_entries = []

        if latest:
            previous = previous_entry(db, source_model, user.id, latest.measured_at)
            sparkline_entries = history_entries(db, source_model, user.id, since=since)

        card = {
            "slug": slug,
            "label": config.label,
            "unit": config.unit,
            "has_data": latest is not None,
            "needs_height": slug == "bmi" and user.height_cm is None,
        }

        if latest:
            card["display_value"] = metrics_service.display_value(slug, latest, user.height_cm)
            card["measured_at"] = latest.measured_at
            card["classification"] = metrics_service.classify(slug, latest, user.height_cm)
            card["trend"] = _trend(
                metrics_service.value_of(slug, latest, user.height_cm),
                metrics_service.value_of(slug, previous, user.height_cm) if previous else None,
            )
            card["sparkline"] = metrics_service.chart_series(slug, sparkline_entries, user.height_cm)

        cards.append(card)

    return templates.TemplateResponse(
        "dashboard.html", {"request": request, "user": user, "cards": cards}
    )
