from dataclasses import dataclass

from app.models.measurements import BloodPressureEntry, GlucoseEntry, HeartRateEntry, WeightEntry
from app.services import ranges
from app.services.bmi import calculate_bmi
from app.services.ranges import Classification

CONTEXT_LABELS = {
    "resting": "spoczynkowe",
    "active": "po wysiłku",
    "fasting": "na czczo",
    "after_meal": "po posiłku",
    "random": "losowy pomiar",
}


@dataclass(frozen=True)
class MetricConfig:
    slug: str
    label: str
    unit: str
    model: type | None  # None dla BMI (parametr wyliczany, nie ma własnej tabeli)


METRICS: dict[str, MetricConfig] = {
    "waga": MetricConfig("waga", "Masa ciała", "kg", WeightEntry),
    "bmi": MetricConfig("bmi", "BMI", "", None),
    "cisnienie": MetricConfig("cisnienie", "Ciśnienie krwi", "mmHg", BloodPressureEntry),
    "tetno": MetricConfig("tetno", "Tętno", "bpm", HeartRateEntry),
    "cukier": MetricConfig("cukier", "Poziom cukru", "mg/dL", GlucoseEntry),
}


def value_of(slug: str, entry, height_cm: float | None = None) -> float | None:
    """Główna wartość liczbowa wpisu, używana do wykresów i statystyk."""
    if slug == "waga":
        return entry.value_kg
    if slug == "bmi":
        if height_cm is None:
            return None
        return calculate_bmi(entry.value_kg, height_cm)
    if slug == "cisnienie":
        return entry.systolic
    if slug == "tetno":
        return entry.bpm
    if slug == "cukier":
        return entry.value_mg_dl
    raise ValueError(f"Nieznany parametr: {slug}")


def display_value(slug: str, entry, height_cm: float | None = None) -> str:
    if slug == "waga":
        return f"{entry.value_kg:g} kg"
    if slug == "bmi":
        if height_cm is None:
            return "brak danych o wzroście"
        return f"{calculate_bmi(entry.value_kg, height_cm):.1f}"
    if slug == "cisnienie":
        pulse = f", tętno {entry.pulse} bpm" if entry.pulse else ""
        return f"{entry.systolic}/{entry.diastolic} mmHg{pulse}"
    if slug == "tetno":
        return f"{entry.bpm} bpm ({CONTEXT_LABELS.get(entry.context, entry.context)})"
    if slug == "cukier":
        return f"{entry.value_mg_dl:g} mg/dL ({CONTEXT_LABELS.get(entry.context, entry.context)})"
    raise ValueError(f"Nieznany parametr: {slug}")


def classify(slug: str, entry, height_cm: float | None = None) -> Classification | None:
    if slug == "waga":
        return None
    if slug == "bmi":
        if height_cm is None:
            return None
        return ranges.classify_bmi(calculate_bmi(entry.value_kg, height_cm))
    if slug == "cisnienie":
        return ranges.classify_blood_pressure(entry.systolic, entry.diastolic)
    if slug == "tetno":
        return ranges.classify_heart_rate(entry.bpm)
    if slug == "cukier":
        return ranges.classify_glucose(entry.value_mg_dl, entry.context)
    raise ValueError(f"Nieznany parametr: {slug}")


def chart_series(slug: str, entries: list, height_cm: float | None = None) -> dict:
    """Dane pod Chart.js: {labels: [...], datasets: [{label, data}, ...]}."""
    labels = [e.measured_at.isoformat() for e in entries]
    if slug == "cisnienie":
        return {
            "labels": labels,
            "datasets": [
                {"label": "Skurczowe", "data": [e.systolic for e in entries]},
                {"label": "Rozkurczowe", "data": [e.diastolic for e in entries]},
            ],
        }
    values = [value_of(slug, e, height_cm) for e in entries]
    return {"labels": labels, "datasets": [{"label": METRICS[slug].label, "data": values}]}
