from app.main import app
from app.schemas.auth import UserInfo
from app.services.auth import create_access_token
from fastapi.testclient import TestClient


client = TestClient(app)


def test_ocr_rejects_more_than_five_files() -> None:
    token = create_access_token(UserInfo(username="operator@ine.local", full_name="Operador", role="OPERATOR"))
    files = [("files", (f"encuesta-{index}.png", b"demo", "image/png")) for index in range(6)]

    response = client.post("/api/v1/ocr/preview", files=files, headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 400
    assert "5" in response.json()["detail"]
