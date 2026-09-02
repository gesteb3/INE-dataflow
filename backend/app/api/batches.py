"""Endpoints para consultar historial y auditoría."""

import psycopg
from fastapi import APIRouter, Depends, HTTPException, Query
from uuid import UUID

from app.api.auth import current_user, require_roles
from app.repositories.audit import list_audit_events
from app.repositories.batch_history import list_batch_issues, list_batches
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


@router.get("/audit", response_model=list[AuditEvent], tags=["audit"])
def get_audit_events(
    limit: int = Query(default=100, ge=1, le=200),
    _user: UserInfo = Depends(require_roles("ADMIN")),
) -> list[AuditEvent]:
    try:
        return [AuditEvent(**row) for row in list_audit_events(limit)]
    except psycopg.Error as error:
        raise HTTPException(status_code=503, detail="No se pudo consultar la auditoría") from error
