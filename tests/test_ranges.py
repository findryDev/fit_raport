import pytest

from app.services.ranges import (
    LEVEL_DANGER,
    LEVEL_HIGH,
    LEVEL_LOW,
    LEVEL_NORMAL,
    LEVEL_WARNING,
    classify_blood_pressure,
    classify_bmi,
    classify_glucose,
    classify_heart_rate,
)


@pytest.mark.parametrize(
    "bmi,expected_level",
    [(17.0, LEVEL_WARNING), (22.0, LEVEL_NORMAL), (27.0, LEVEL_WARNING), (32.0, LEVEL_DANGER)],
)
def test_classify_bmi(bmi, expected_level):
    assert classify_bmi(bmi).level == expected_level


def test_classify_blood_pressure_optimal():
    result = classify_blood_pressure(110, 70)
    assert result.level == LEVEL_NORMAL


def test_classify_blood_pressure_hypotension():
    assert classify_blood_pressure(85, 55).level == LEVEL_LOW


def test_classify_blood_pressure_stage_2_hypertension():
    assert classify_blood_pressure(165, 105).level == LEVEL_DANGER


def test_classify_heart_rate_bradycardia():
    assert classify_heart_rate(50).level == LEVEL_WARNING


def test_classify_heart_rate_normal():
    assert classify_heart_rate(75).level == LEVEL_NORMAL


def test_classify_heart_rate_tachycardia():
    assert classify_heart_rate(120).level == LEVEL_HIGH


def test_classify_glucose_fasting_normal():
    assert classify_glucose(90, "fasting").level == LEVEL_NORMAL


def test_classify_glucose_fasting_diabetic_range():
    assert classify_glucose(140, "fasting").level == LEVEL_DANGER


def test_classify_glucose_after_meal_prediabetic():
    assert classify_glucose(160, "after_meal").level == LEVEL_WARNING
