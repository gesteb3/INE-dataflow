from datetime import datetime, timezone

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_metrics_exposes_operational_counters(monkeypatch) -> None:
    monkeypatch.setattr("app.api.metrics.database_is_healthy", lambda: True)
    monkeypatch.setattr(
        "app.api.metrics.get_report_summary",
        lambda: {
            "total_batches": 3,
            "confirmed_batches": 2,
            "total_input_rows": 12000,
            "confirmed_valid_rows": 11790,
            "total_rejected_rows": 210,
            "total_validation_errors": 286,
            "last_confirmed_at": datetime.now(timezone.utc),
        },
    )

    response = client.get("/metrics")

    assert response.status_code == 200
    assert "ine_dataflow_database_up 1" in response.text
    assert "ine_dataflow_total_rejected_rows 210" in response.text
