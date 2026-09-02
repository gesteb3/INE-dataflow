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
    assert response.content.startswith(b"\xef\xbb\xbf")
    assert "code,severity,row,column,message,value" in response.text
    assert "FIELD-008,ERROR,4,urban_rural,Valor no permitido,X" in response.text


def test_valid_records_export_returns_clean_csv(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.api.batches.list_valid_records",
        lambda batch_id: [
            {
                "record_id": "R-001",
                "survey_code": "HOGARES-2026",
                "interview_date": "2026-08-21",
                "department_code": "01",
                "municipality_code": "0101",
                "urban_rural": "U",
                "respondent_age": 35,
                "respondent_sex": "F",
                "household_size": 4,
                "monthly_income_gtq": 4500,
            }
        ],
    )

    response = client.get(
        "/api/v1/batches/00000000-0000-0000-0000-000000000001/valid.csv",
        headers=AUTH_HEADERS,
    )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    assert response.content.startswith(b"\xef\xbb\xbf")
    assert "record_id,survey_code,interview_date" in response.text
    assert "R-001,HOGARES-2026,2026-08-21,01,0101,U,35,F,4,4500" in response.text
