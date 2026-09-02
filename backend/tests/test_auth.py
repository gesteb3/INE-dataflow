from fastapi.testclient import TestClient

from app.main import app


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
