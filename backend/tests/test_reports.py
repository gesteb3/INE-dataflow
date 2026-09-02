from decimal import Decimal

from fastapi.testclient import TestClient

from app.main import app
from app.schemas.auth import UserInfo
from app.services.auth import create_access_token


client = TestClient(app)
AUTH_HEADERS = {
    "Authorization": f"Bearer {create_access_token(UserInfo(username='tester', full_name='Test User', role='ADMIN'))}"
}


def test_report_summary_returns_aggregated_indicators(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.api.reports.get_report_summary",
        lambda: {
            "total_batches": 3,
            "confirmed_batches": 2,
            "total_input_rows": 120,
            "confirmed_valid_rows": 100,
            "total_rejected_rows": 20,
            "total_validation_errors": 21,
            "last_confirmed_at": None,
        },
    )

    response = client.get("/api/v1/reports/summary", headers=AUTH_HEADERS)

    assert response.status_code == 200
    assert response.json() == {
        "total_batches": 3,
        "confirmed_batches": 2,
        "total_input_rows": 120,
        "confirmed_valid_rows": 100,
        "total_rejected_rows": 20,
        "total_validation_errors": 21,
        "last_confirmed_at": None,
    }


def test_department_report_returns_power_bi_rows(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.api.reports.get_department_report",
        lambda: [
            {
                "department_code": "01",
                "valid_records": 50,
                "urban_records": 30,
                "rural_records": 20,
                "average_age": Decimal("35.50"),
                "average_household_size": Decimal("3.20"),
                "average_monthly_income_gtq": Decimal("2500.00"),
                "total_monthly_income_gtq": Decimal("125000.00"),
            }
        ],

    )

    response = client.get("/api/v1/reports/by-department", headers=AUTH_HEADERS)

    assert response.status_code == 200
    assert response.json()[0]["department_code"] == "01"
    assert response.json()[0]["valid_records"] == 50
