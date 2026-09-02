"""Modelos de respuesta para reportes de calidad y registros válidos."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel

from app.schemas.validation import ValidationIssue


class ReportSummary(BaseModel):
    """Indicadores generales para el tablero de calidad."""

    total_batches: int
    confirmed_batches: int
    total_input_rows: int
    confirmed_valid_rows: int
    total_rejected_rows: int
    total_validation_errors: int
    last_confirmed_at: datetime | None


class DepartmentReport(BaseModel):
    """Métricas de registros válidos agrupadas por departamento."""

    department_code: str
    valid_records: int
    urban_records: int
    rural_records: int
    average_age: Decimal | None
    average_household_size: Decimal | None
    average_monthly_income_gtq: Decimal | None
    total_monthly_income_gtq: Decimal


class PowerBIReport(BaseModel):
    """Respuesta consolidada para crear varias tablas desde una sola consulta M."""

    batch_id: UUID | None
    generated_at: datetime
    summary: ReportSummary
    departments: list[DepartmentReport]
    valid_records: list[dict]
    issues: list[ValidationIssue]
