from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "FlyRank Auth API is running"}


def test_signup_endpoint(monkeypatch):
    fake_user = SimpleNamespace(
        model_dump=lambda: {"id": "user-123", "email": "test@example.com"}
    )
    fake_response = SimpleNamespace(user=fake_user)

    monkeypatch.setattr(
        "app.main.signup_user",
        lambda email, password: fake_response,
    )

    response = client.post(
        "/auth/signup",
        json={
            "email": "test@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": "Signup successful",
        "user": {"id": "user-123", "email": "test@example.com"},
    }


def test_login_endpoint(monkeypatch):
    fake_user = SimpleNamespace(
        model_dump=lambda: {"id": "user-123", "email": "test@example.com"}
    )
    fake_session = SimpleNamespace(
        access_token="access-token",
        refresh_token="refresh-token",
    )
    fake_response = SimpleNamespace(
        user=fake_user,
        session=fake_session,
    )

    monkeypatch.setattr(
        "app.main.login_user",
        lambda email, password: fake_response,
    )

    response = client.post(
        "/auth/login",
        json={
            "email": "test@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": "Login successful",
        "access_token": "access-token",
        "refresh_token": "refresh-token",
        "user": {"id": "user-123", "email": "test@example.com"},
    }


def test_me_endpoint(monkeypatch):
    fake_user = SimpleNamespace(
        model_dump=lambda: {"id": "user-123", "email": "test@example.com"}
    )

    monkeypatch.setattr(
        "app.main.get_current_user",
        lambda access_token: fake_user,
    )

    response = client.get(
        "/auth/me",
        headers={"Authorization": "Bearer test-token"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "user": {"id": "user-123", "email": "test@example.com"}
    }


def test_me_endpoint_requires_authorization():
    response = client.get("/auth/me")

    assert response.status_code == 401
    assert response.json() == {"detail": "Access token required"}


def test_me_endpoint_rejects_invalid_scheme():
    response = client.get(
        "/auth/me",
        headers={"Authorization": "Basic test-token"},
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Access token required"}


def test_logout_endpoint(monkeypatch):
    calls = []

    def fake_logout(access_token):
        calls.append(access_token)

    monkeypatch.setattr("app.main.logout_user", fake_logout)

    response = client.post(
        "/auth/logout",
        headers={"Authorization": "Bearer test-token"},
    )

    assert response.status_code == 204
    assert response.content == b""
    assert calls == ["test-token"]


def test_logout_endpoint_requires_authorization():
    response = client.post("/auth/logout")

    assert response.status_code == 401
    assert response.json() == {"detail": "Access token required"}


def test_logout_endpoint_rejects_empty_bearer_token():
    response = client.post(
        "/auth/logout",
        headers={"Authorization": "Bearer "},
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Access token required"}