"""Endpoints para consultar historial, incidencias y auditoría."""

import csv
from io import StringIO

import psycopg
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from uuid import UUID

from app.api.auth import current_user, require_roles
from app.repositories.audit import list_audit_events
from app.repositories.batch_history import list_batch_issues, list_batches, list_valid_records
from app.schemas.auth import UserInfo
from app.schemas.batches import AuditEvent, BatchSummary
from app.schemas.validation import ValidationIssue


router = APIRouter()


@router.get("/batches", response_model=list[BatchSummary], tags=["batches"])
def get_batches(
    limit: int = Query(default=50, ge=1, le=100),
    _user: UserInfo = Depends(current_user),
) -> list[BatchSummary]:
    try:
        return [BatchSummary(**row) for row in list_batches(limit)]
    except psycopg.Error as error:
        raise HTTPException(status_code=503, detail="No se pudo consultar el historial") from error


@router.get("/batches/{batch_id}/issues", response_model=list[ValidationIssue], tags=["batches"])
def get_batch_issues(batch_id: UUID, _user: UserInfo = Depends(current_user)) -> list[ValidationIssue]:
    try:
        return [ValidationIssue(**row) for row in list_batch_issues(batch_id)]
    except psycopg.Error as error:
        raise HTTPException(status_code=503, detail="No se pudieron consultar las incidencias") from error


@router.get("/batches/{batch_id}/issues.csv", tags=["batches"])
def export_batch_issues(batch_id: UUID, _user: UserInfo = Depends(current_user)) -> StreamingResponse:
    """Descarga las incidencias de un lote para corregir y volver a procesar."""

    try:
        issues = list_batch_issues(batch_id)
    except psycopg.Error as error:
        raise HTTPException(status_code=503, detail="No se pudieron exportar las incidencias") from error

    output = StringIO(newline="")
    # BOM para que Excel detecte UTF-8 y respete tildes y eñes al abrir el CSV.
    output.write("\ufeff")
    writer = csv.writer(output)
    writer.writerow(["code", "severity", "row", "column", "message", "value"])
    for issue in issues:
        writer.writerow([
            issue.get("code"),
            issue.get("severity"),
            issue.get("row"),
            issue.get("column"),
            issue.get("message"),
            issue.get("value"),
        ])
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="errores-{batch_id}.csv"'},
    )


@router.get("/batches/{batch_id}/valid.csv", tags=["batches"])
def export_batch_valid_records(batch_id: UUID, _user: UserInfo = Depends(current_user)) -> StreamingResponse:
    """Descarga el dataset limpio publicado de un lote confirmado."""

    try:
        records = list_valid_records(batch_id)
    except psycopg.Error as error:
        raise HTTPException(status_code=503, detail="No se pudo exportar la encuesta limpia") from error

    output = StringIO(newline="")
    output.write("\ufeff")
    writer = csv.writer(output)
    columns = [
        "record_id", "survey_code", "interview_date", "department_code",
        "municipality_code", "urban_rural", "respondent_age", "respondent_sex",
        "household_size", "monthly_income_gtq",
    ]
    writer.writerow(columns)
    for record in records:
        writer.writerow([record.get(column) for column in columns])
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="encuesta-limpia-{batch_id}.csv"'},
    )


@router.get("/audit", response_model=list[AuditEvent], tags=["audit"])
def get_audit_events(
    limit: int = Query(default=100, ge=1, le=200),
    _user: UserInfo = Depends(require_roles("ADMIN")),
) -> list[AuditEvent]:
    try:
        return [AuditEvent(**row) for row in list_audit_events(limit)]
    except psycopg.Error as error:
        raise HTTPException(status_code=503, detail="No se pudo consultar la auditoría") from error
