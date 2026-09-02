from fastapi.testclient import TestClient

from datetime import datetime, timezone
from uuid import uuid4

from app.main import app
from app.schemas.auth import UserInfo
from app.services.auth import create_access_token


client = TestClient(app)


def test_login_returns_bearer_token(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.api.auth.find_active_user",
        lambda username: {
            "username": "admin@ine.local",
            "full_name": "Administrador INE DataFlow",
            "role": "ADMIN",
            "password_hash": "pbkdf2_sha256$310000$aW5lLWRhdGFmbG93LWRlbW8tc2FsdA==$AFlqbRHqFxbaUvoEHlB8kgaPiImoyyXvqKcVYAvJXVw=",
        },
    )
    monkeypatch.setattr("app.api.auth.record_audit_event", lambda *args, **kwargs: None)

    response = client.post(
        "/api/v1/auth/login",
        json={"username": "admin@ine.local", "password": "INEDataFlow2026!"},
    )

    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert response.json()["user"]["role"] == "ADMIN"


def test_protected_report_requires_authentication() -> None:
    response = client.get("/api/v1/reports/summary")

    assert response.status_code == 401


def test_issue_export_requires_authentication() -> None:
    response = client.get("/api/v1/batches/00000000-0000-0000-0000-000000000000/issues.csv")

    assert response.status_code == 401


def test_user_administration_requires_admin() -> None:
    token = create_access_token(UserInfo(username="operator@ine.local", full_name="Operador", role="OPERATOR"))
    response = client.get("/api/v1/users", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403


def test_admin_can_create_user_and_register_audit(monkeypatch) -> None:
    user_id = uuid4()
    created = {
        "id": user_id,
        "username": "operator@ine.local",
        "full_name": "Operador INE",
        "role": "OPERATOR",
        "is_active": True,
        "created_at": datetime.now(timezone.utc),
    }
    audit_events: list[tuple] = []
    monkeypatch.setattr("app.api.users.create_user", lambda *args: created)
    monkeypatch.setattr("app.api.users.record_audit_event", lambda *args: audit_events.append(args))
    token = create_access_token(UserInfo(username="admin@ine.local", full_name="Admin", role="ADMIN"))

    response = client.post(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {token}"},
        json={"username": "operator@ine.local", "full_name": "Operador INE", "password": "SecurePass123!", "role": "OPERATOR"},
    )

    assert response.status_code == 201
    assert response.json()["role"] == "OPERATOR"
    assert audit_events[0][1] == "USER_CREATED"
