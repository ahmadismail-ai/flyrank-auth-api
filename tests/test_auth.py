import pytest
from fastapi import HTTPException

from app import auth


class FakeAuth:
    def __init__(self, response=None, error=None):
        self.response = response
        self.error = error

    def sign_up(self, credentials):
        if self.error:
            raise self.error
        return self.response

    def sign_in_with_password(self, credentials):
        if self.error:
            raise self.error
        return self.response

    def get_user(self, access_token):
        if self.error:
            raise self.error
        return self.response


class FakeSupabase:
    def __init__(self, auth_client):
        self.auth = auth_client


class FakeResponse:
    def __init__(self, user=None, session=None):
        self.user = user
        self.session = session


def test_signup_user_success(monkeypatch):
    response = FakeResponse(user={"id": "123"})
    monkeypatch.setattr(auth, "supabase", FakeSupabase(FakeAuth(response=response)))

    result = auth.signup_user("test@example.com", "password")

    assert result.user == {"id": "123"}


def test_signup_user_failure(monkeypatch):
    monkeypatch.setattr(
        auth,
        "supabase",
        FakeSupabase(FakeAuth(error=Exception("Supabase error"))),
    )

    with pytest.raises(HTTPException) as exc:
        auth.signup_user("test@example.com", "password")

    assert exc.value.status_code == 400
    assert exc.value.detail == "Signup failed"


def test_login_user_success(monkeypatch):
    response = FakeResponse(
        user={"id": "123"},
        session={"access_token": "token"},
    )
    monkeypatch.setattr(auth, "supabase", FakeSupabase(FakeAuth(response=response)))

    result = auth.login_user("test@example.com", "password")

    assert result.user == {"id": "123"}
    assert result.session == {"access_token": "token"}


def test_login_user_failure(monkeypatch):
    monkeypatch.setattr(
        auth,
        "supabase",
        FakeSupabase(FakeAuth(error=Exception("Invalid credentials"))),
    )

    with pytest.raises(HTTPException) as exc:
        auth.login_user("test@example.com", "wrong")

    assert exc.value.status_code == 401
    assert exc.value.detail == "Invalid credentials"


def test_get_current_user_success(monkeypatch):
    response = FakeResponse(user={"id": "123"})
    monkeypatch.setattr(auth, "supabase", FakeSupabase(FakeAuth(response=response)))

    result = auth.get_current_user("valid-token")

    assert result == {"id": "123"}


def test_get_current_user_failure(monkeypatch):
    monkeypatch.setattr(
        auth,
        "supabase",
        FakeSupabase(FakeAuth(error=Exception("Invalid token"))),
    )

    with pytest.raises(HTTPException) as exc:
        auth.get_current_user("invalid-token")

    assert exc.value.status_code == 401
    assert exc.value.detail == "Invalid or expired token"

def test_logout_user_success(monkeypatch):
    class FakeAdmin:
        def sign_out(self, access_token, scope):
            assert access_token == "valid-token"
            assert scope == "global"

    class FakeAuthWithAdmin:
        admin = FakeAdmin()

    monkeypatch.setattr(
        auth,
        "supabase",
        FakeSupabase(FakeAuthWithAdmin()),
    )

    result = auth.logout_user("valid-token")

    assert result is None


def test_logout_user_failure(monkeypatch):
    class FakeAdmin:
        def sign_out(self, access_token, scope):
            raise Exception("Invalid token")

    class FakeAuthWithAdmin:
        admin = FakeAdmin()

    monkeypatch.setattr(
        auth,
        "supabase",
        FakeSupabase(FakeAuthWithAdmin()),
    )

    with pytest.raises(HTTPException) as exc:
        auth.logout_user("invalid-token")

    assert exc.value.status_code == 401
    assert exc.value.detail == "Invalid or expired token"
