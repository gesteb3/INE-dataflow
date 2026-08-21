from io import BytesIO

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_validate_upload_returns_summary_and_errors() -> None:
    content = (
        "record_id,survey_code,interview_date,department_code,municipality_code,"
        "urban_rural,respondent_age,respondent_sex,household_size,monthly_income_gtq\n"
        "HOGAR-0001,ENHOGAR,2026-08-20,01,0101,U,34,F,4,4250.00\n"
        "HOGAR-0001,ENHOGAR,2026-08-20,01,0101,U,34,F,4,4250.00\n"
        "HOGAR-0002,ENHOGAR,2026-08-20,01,0101,X,34,F,4,-1.00\n"
    ).encode("utf-8")

    response = client.post(
        "/api/v1/uploads/validate",
        files={"file": ("encuesta.csv", BytesIO(content), "text/csv")},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "REVIEW_REQUIRED"
    assert body["total_rows"] == 3
    assert body["valid_rows"] == 1
    assert body["rejected_rows"] == 2
    assert {issue["code"] for issue in body["issues"]} == {
        "FIELD-003",
        "FIELD-008",
        "FIELD-012",
    }


def test_validate_upload_rejects_non_csv_file() -> None:
    response = client.post(
        "/api/v1/uploads/validate",
        files={"file": ("encuesta.txt", BytesIO(b"not csv"), "text/plain")},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "REJECTED"
    assert response.json()["issues"][0]["code"] == "FILE-001"
