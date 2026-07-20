def test_dashboard_redirects_when_not_logged_in(client):
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/login"


def test_register_then_dashboard_accessible(registered_client):
    response = registered_client.get("/")
    assert response.status_code == 200


def test_register_duplicate_email_rejected(client):
    payload = {
        "email": "dup@example.com",
        "password": "testpass123",
        "password_confirm": "testpass123",
    }
    first = client.post("/register", data=payload)
    assert first.status_code in (200, 303)

    client.post("/logout")
    second = client.post("/register", data=payload)
    assert second.status_code == 400
    assert "już istnieje" in second.text


def test_register_password_mismatch_rejected(client):
    response = client.post(
        "/register",
        data={"email": "x@example.com", "password": "testpass123", "password_confirm": "different"},
    )
    assert response.status_code == 400


def test_login_wrong_password_rejected(registered_client):
    registered_client.post("/logout")
    response = registered_client.post(
        "/login", data={"email": "test@example.com", "password": "wrong-password"}
    )
    assert response.status_code == 400


def test_login_success(registered_client):
    registered_client.post("/logout")
    response = registered_client.post(
        "/login", data={"email": "test@example.com", "password": "testpass123"}, follow_redirects=False
    )
    assert response.status_code == 303
    assert response.headers["location"] == "/"


def test_logout_clears_session(registered_client):
    registered_client.post("/logout")
    response = registered_client.get("/", follow_redirects=False)
    assert response.status_code == 303
