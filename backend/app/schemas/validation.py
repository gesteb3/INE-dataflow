"""Modelos de respuesta para la validación de cargas CSV."""

from typing import Literal

from pydantic import BaseModel


class ValidationIssue(BaseModel):
    """Error o advertencia detectado durante una carga."""

    code: str
    severity: Literal["ERROR", "WARNING"]
    row: int | None = None
    column: str | None = None
    message: str
    value: str | None = None


class ValidationResponse(BaseModel):
    """Resumen completo de una validación de archivo."""

    batch_id: str
    file_name: str
    status: Literal["READY_FOR_CONFIRMATION", "REVIEW_REQUIRED", "REJECTED"]
    total_rows: int
    valid_rows: int
    rejected_rows: int
    warning_rows: int
    issues: list[ValidationIssue]
