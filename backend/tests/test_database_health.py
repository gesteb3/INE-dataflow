from app.main import app
from fastapi.testclient import TestClient


client = TestClient(app)


def test_database_health_returns_503_when_database_is_unavailable(monkeypatch) -> None:
    monkeypatch.setattr("app.main.database_is_healthy", lambda: False)

    response = client.get("/health/db")

    assert response.status_code == 503
    assert response.json() == {"detail": "PostgreSQL no está disponible"}
