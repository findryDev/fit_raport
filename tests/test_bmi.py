from app.services.bmi import calculate_bmi


def test_calculate_bmi_normal():
    assert calculate_bmi(weight_kg=70, height_cm=175) == 22.9


def test_calculate_bmi_rounds_to_one_decimal():
    assert calculate_bmi(weight_kg=80.456, height_cm=180) == round(80.456 / 1.8**2, 1)
