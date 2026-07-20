"""Orientacyjna klasyfikacja parametrów zdrowotnych wg standardowych progów referencyjnych
(WHO dla BMI, ESC/ESH dla ciśnienia, typowe zakresy kliniczne dla tętna i glukozy).

Wynik nie jest poradą medyczną i nie zastępuje konsultacji lekarskiej.
"""

from dataclasses import dataclass

# poziomy używane do kolorowania w UI (patrz app/static/css/style.css)
LEVEL_LOW = "low"
LEVEL_NORMAL = "normal"
LEVEL_WARNING = "warning"
LEVEL_HIGH = "high"
LEVEL_DANGER = "danger"


@dataclass(frozen=True)
class Classification:
    label: str
    level: str


def classify_bmi(bmi: float) -> Classification:
    if bmi < 18.5:
        return Classification("Niedowaga", LEVEL_WARNING)
    if bmi < 25:
        return Classification("Waga prawidłowa", LEVEL_NORMAL)
    if bmi < 30:
        return Classification("Nadwaga", LEVEL_WARNING)
    return Classification("Otyłość", LEVEL_DANGER)


def classify_blood_pressure(systolic: int, diastolic: int) -> Classification:
    if systolic < 90 or diastolic < 60:
        return Classification("Hipotonia", LEVEL_LOW)
    if systolic < 120 and diastolic < 80:
        return Classification("Optymalne", LEVEL_NORMAL)
    if systolic < 130 and diastolic < 85:
        return Classification("Prawidłowe", LEVEL_NORMAL)
    if systolic < 140 and diastolic < 90:
        return Classification("Wysokie prawidłowe", LEVEL_WARNING)
    if systolic < 160 and diastolic < 100:
        return Classification("Nadciśnienie I stopnia", LEVEL_HIGH)
    if systolic < 180 and diastolic < 110:
        return Classification("Nadciśnienie II stopnia", LEVEL_DANGER)
    return Classification("Nadciśnienie III stopnia", LEVEL_DANGER)


def classify_heart_rate(bpm: int) -> Classification:
    if bpm < 60:
        return Classification("Bradykardia", LEVEL_WARNING)
    if bpm <= 100:
        return Classification("W normie", LEVEL_NORMAL)
    return Classification("Tachykardia", LEVEL_HIGH)


def classify_glucose(value_mg_dl: float, context: str) -> Classification:
    if context == "fasting":
        if value_mg_dl < 70:
            return Classification("Hipoglikemia", LEVEL_LOW)
        if value_mg_dl < 100:
            return Classification("Prawidłowa (na czczo)", LEVEL_NORMAL)
        if value_mg_dl < 126:
            return Classification("Stan przedcukrzycowy", LEVEL_WARNING)
        return Classification("Zakres cukrzycowy", LEVEL_DANGER)

    # po posiłku / losowo
    if value_mg_dl < 70:
        return Classification("Hipoglikemia", LEVEL_LOW)
    if value_mg_dl < 140:
        return Classification("Prawidłowa", LEVEL_NORMAL)
    if value_mg_dl < 200:
        return Classification("Stan przedcukrzycowy", LEVEL_WARNING)
    return Classification("Zakres cukrzycowy", LEVEL_DANGER)
