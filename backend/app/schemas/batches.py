"""Modelos para el historial de lotes y sus incidencias."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class BatchSummary(BaseModel):
    batch_id: str
    file_name: str
    status: Literal["REVIEW_REQUIRED", "READY_FOR_CONFIRMATION", "CONFIRMED", "REJECTED"]
    total_rows: int
    valid_rows: int
    rejected_rows: int
    warning_rows: int
    created_at: datetime
    confirmed_at: datetime | None


class AuditEvent(BaseModel):
    action: str
    resource_type: str
    resource_id: str | None
    username: str | None
    details: dict
    created_at: datetime
