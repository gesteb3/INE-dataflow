from fastapi.testclient import TestClient

from app.main import app
from app.schemas.auth import UserInfo
from app.services.auth import create_access_token


client = TestClient(app)
AUTH_HEADERS = {
    "Authorization": f"Bearer {create_access_token(UserInfo(username='tester', full_name='Test User', role='ADMIN'))}"
}


def test_issue_export_returns_csv(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.api.batches.list_batch_issues",
        lambda batch_id: [
            {
                "code": "FIELD-008",
                "severity": "ERROR",
                "row": 4,
                "column": "urban_rural",
                "message": "Valor no permitido",
                "value": "X",
            }
        ],
    )

    response = client.get(
        "/api/v1/batches/00000000-0000-0000-0000-000000000001/issues.csv",
        headers=AUTH_HEADERS,
    )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    assert "code,severity,row,column,message,value" in response.text
    assert "FIELD-008,ERROR,4,urban_rural,Valor no permitido,X" in response.text
