"""Métricas operativas en formato Prometheus para monitoreo."""

from datetime import datetime

import psycopg
from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

from app.db import database_is_healthy
from app.repositories.reports import get_report_summary


router = APIRouter()


def _metric(name: str, help_text: str, value: int | float, metric_type: str = "gauge") -> str:
    return f"# HELP {name} {help_text}\n# TYPE {name} {metric_type}\n{name} {value}\n"


@router.get("/metrics", response_class=PlainTextResponse, include_in_schema=True, tags=["monitoring"])
def metrics() -> PlainTextResponse:
    """Publica métricas agregadas sin datos personales para Azure Monitor/Prometheus."""

    database_up = database_is_healthy()
    summary = None
    if database_up:
        try:
            summary = get_report_summary()
        except psycopg.Error:
            summary = None
    lines = [
        _metric("ine_dataflow_up", "Estado de disponibilidad de la API.", 1),
        _metric("ine_dataflow_database_up", "Estado de conexión con PostgreSQL.", int(summary is not None)),
    ]
    if summary is not None:
        for key, help_text in (
            ("total_batches", "Lotes recibidos."),
            ("confirmed_batches", "Lotes confirmados."),
            ("total_input_rows", "Filas recibidas."),
            ("confirmed_valid_rows", "Registros válidos publicados."),
            ("total_rejected_rows", "Filas rechazadas."),
            ("total_validation_errors", "Incidencias de validación."),
        ):
            lines.append(_metric(f"ine_dataflow_{key}", help_text, summary.get(key, 0)))
        last_confirmed = summary.get("last_confirmed_at")
        if isinstance(last_confirmed, datetime):
            lines.append(_metric("ine_dataflow_last_confirmed_timestamp", "Fecha Unix del último lote confirmado.", last_confirmed.timestamp()))
    return PlainTextResponse("".join(lines), media_type="text/plain; version=0.0.4")
