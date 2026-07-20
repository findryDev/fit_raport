def test_add_weight_entry_shows_on_dashboard(registered_client):
    registered_client.post("/reports/waga/add", data={"value": 80.5, "note": "poranna"})
    response = registered_client.get("/")
    assert "80.5 kg" in response.text


def test_bmi_computed_from_weight_and_height(registered_client):
    registered_client.post("/reports/waga/add", data={"value": 90})
    response = registered_client.get("/reports/bmi")
    assert response.status_code == 200
    # 90 kg / (1.80 m)^2 = 27.8
    assert "27.8" in response.text


def test_blood_pressure_entry_and_classification(registered_client):
    registered_client.post("/reports/cisnienie/add", data={"systolic": 170, "diastolic": 105})
    response = registered_client.get("/reports/cisnienie")
    assert "170/105" in response.text
    assert "Nadciśnienie" in response.text


def test_edit_entry_updates_value(registered_client):
    registered_client.post("/reports/waga/add", data={"value": 80})
    entry_id_row = registered_client.get("/reports/waga")
    # pierwszy (jedyny) wpis ma id=1 w świeżej bazie testowej
    edit_form = registered_client.get("/reports/waga/1/edit")
    assert edit_form.status_code == 200

    registered_client.post("/reports/waga/1/edit", data={"value": 77.5})
    updated = registered_client.get("/reports/waga")
    assert "77.5 kg" in updated.text


def test_delete_entry_removes_it(registered_client):
    registered_client.post("/reports/waga/add", data={"value": 80})
    registered_client.post("/reports/waga/1/delete")
    response = registered_client.get("/reports/waga")
    assert "80 kg" not in response.text
    assert "Brak wpisów" in response.text


def test_unknown_metric_returns_404(registered_client):
    response = registered_client.get("/reports/nieznany")
    assert response.status_code == 404


def test_cannot_add_entry_directly_to_virtual_bmi_metric(registered_client):
    response = registered_client.post("/reports/bmi/add", data={"value": 25})
    assert response.status_code == 404
