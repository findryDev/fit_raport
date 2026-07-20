import re


def _create_api_key(client, name="test-key") -> str:
    # client.post podąża za przekierowaniem 303 na /account, gdzie sesyjny
    # "flash" z nowym kluczem jest pokazywany i od razu usuwany (one-time reveal) -
    # trzeba go odczytać z tej samej odpowiedzi, a nie z kolejnego GET.
    response = client.post("/account/api-keys", data={"name": name})
    match = re.search(r'<code class="new-key-value">([^<]+)</code>', response.text)
    assert match, "nie znaleziono nowo wygenerowanego klucza API w HTML"
    return match.group(1)


def test_api_requires_key(registered_client):
    response = registered_client.post("/api/v1/weight", json={"value_kg": 80})
    assert response.status_code == 401


def test_api_rejects_invalid_key(registered_client):
    response = registered_client.post(
        "/api/v1/weight", json={"value_kg": 80}, headers={"X-API-Key": "frk_invalid"}
    )
    assert response.status_code == 401


def test_api_weight_create_and_list(registered_client):
    key = _create_api_key(registered_client)
    headers = {"X-API-Key": key}

    create = registered_client.post("/api/v1/weight", json={"value_kg": 82.5, "note": "z API"}, headers=headers)
    assert create.status_code == 201
    body = create.json()
    assert body["value_kg"] == 82.5
    assert body["source"] == "api"

    listing = registered_client.get("/api/v1/weight", headers=headers)
    assert listing.status_code == 200
    assert len(listing.json()) == 1


def test_api_blood_pressure_create(registered_client):
    key = _create_api_key(registered_client)
    response = registered_client.post(
        "/api/v1/blood-pressure",
        json={"systolic": 120, "diastolic": 80, "pulse": 70},
        headers={"X-API-Key": key},
    )
    assert response.status_code == 201
    assert response.json()["systolic"] == 120


def test_api_heart_rate_create(registered_client):
    key = _create_api_key(registered_client)
    response = registered_client.post(
        "/api/v1/heart-rate", json={"bpm": 62, "context": "resting"}, headers={"X-API-Key": key}
    )
    assert response.status_code == 201
    assert response.json()["bpm"] == 62


def test_api_glucose_create(registered_client):
    key = _create_api_key(registered_client)
    response = registered_client.post(
        "/api/v1/glucose", json={"value_mg_dl": 95, "context": "fasting"}, headers={"X-API-Key": key}
    )
    assert response.status_code == 201
    assert response.json()["context"] == "fasting"


def test_api_validation_rejects_out_of_range(registered_client):
    key = _create_api_key(registered_client)
    response = registered_client.post("/api/v1/weight", json={"value_kg": 1000}, headers={"X-API-Key": key})
    assert response.status_code == 422


def test_delete_api_key_revokes_access(registered_client):
    html = registered_client.post("/account/api-keys", data={"name": "to-delete"}).text
    key = re.search(r'<code class="new-key-value">([^<]+)</code>', html).group(1)
    key_id = re.search(r'/account/api-keys/(\d+)/delete', html).group(1)

    ok = registered_client.post("/api/v1/weight", json={"value_kg": 70}, headers={"X-API-Key": key})
    assert ok.status_code == 201

    registered_client.post(f"/account/api-keys/{key_id}/delete")

    revoked = registered_client.post("/api/v1/weight", json={"value_kg": 70}, headers={"X-API-Key": key})
    assert revoked.status_code == 401
