"""Endpoints de reportes agregados para consumo de Power BI."""

from datetime import datetime, timezone

import psycopg
from fastapi import APIRouter, Depends, HTTPException, Query
from uuid import UUID

from app.api.auth import current_user
from app.repositories.reports import get_department_report, get_report_summary
from app.repositories.batch_history import list_batch_issues, list_valid_records
from app.schemas.reports import DepartmentReport, PowerBIReport, ReportSummary
from app.schemas.validation import ValidationIssue
from app.schemas.auth import UserInfo


router = APIRouter()


@router.get("/reports/summary", response_model=ReportSummary, tags=["reports"])
def report_summary(
    batch_id: UUID | None = Query(default=None),
    _user: UserInfo = Depends(current_user),
) -> ReportSummary:
    """Devuelve indicadores generales de procesamiento y calidad."""

    try:
        return ReportSummary(**get_report_summary(batch_id))
    except psycopg.Error as error:
        raise HTTPException(status_code=503, detail="No se pudo consultar el reporte en PostgreSQL") from error


@router.get("/reports/by-department", response_model=list[DepartmentReport], tags=["reports"])
def report_by_department(
    batch_id: UUID | None = Query(default=None),
    _user: UserInfo = Depends(current_user),
) -> list[DepartmentReport]:
    """Devuelve métricas de registros confirmados agrupadas por departamento."""

    try:
        return [DepartmentReport(**row) for row in get_department_report(batch_id)]
    except psycopg.Error as error:
        raise HTTPException(status_code=503, detail="No se pudo consultar el reporte en PostgreSQL") from error


@router.get("/reports/powerbi", response_model=PowerBIReport, tags=["reports"])
def power_bi_report(
    batch_id: UUID | None = Query(default=None),
    _user: UserInfo = Depends(current_user),
) -> PowerBIReport:
    """Entrega todas las fuentes del tablero en una sola respuesta JSON."""

    try:
        return PowerBIReport(
            batch_id=batch_id,
            generated_at=datetime.now(timezone.utc),
            summary=ReportSummary(**get_report_summary(batch_id)),
            departments=[DepartmentReport(**row) for row in get_department_report(batch_id)],
            valid_records=list_valid_records(batch_id),
            issues=[ValidationIssue(**row) for row in list_batch_issues(batch_id)],
        )
    except psycopg.Error as error:
        raise HTTPException(status_code=503, detail="No se pudo consultar el reporte consolidado") from error
