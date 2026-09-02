"""Endpoints de reportes agregados para consumo de Power BI."""

import psycopg
from fastapi import APIRouter, Depends, HTTPException

from app.api.auth import current_user
from app.repositories.reports import get_department_report, get_report_summary
from app.schemas.reports import DepartmentReport, ReportSummary
from app.schemas.auth import UserInfo


router = APIRouter()


@router.get("/reports/summary", response_model=ReportSummary, tags=["reports"])
def report_summary(_user: UserInfo = Depends(current_user)) -> ReportSummary:
    """Devuelve indicadores generales de procesamiento y calidad."""

    try:
        return ReportSummary(**get_report_summary())
    except psycopg.Error as error:
        raise HTTPException(status_code=503, detail="No se pudo consultar el reporte en PostgreSQL") from error


@router.get("/reports/by-department", response_model=list[DepartmentReport], tags=["reports"])
def report_by_department(_user: UserInfo = Depends(current_user)) -> list[DepartmentReport]:
    """Devuelve métricas de registros confirmados agrupadas por departamento."""

    try:
        return [DepartmentReport(**row) for row in get_department_report()]
    except psycopg.Error as error:
        raise HTTPException(status_code=503, detail="No se pudo consultar el reporte en PostgreSQL") from error
