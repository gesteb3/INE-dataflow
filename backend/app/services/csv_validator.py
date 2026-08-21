"""Validación del contrato CSV del MVP."""

import csv
import io
import re
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from uuid import uuid4

from app.schemas.validation import ValidationIssue, ValidationResponse


REQUIRED_COLUMNS = (
    "record_id",
    "survey_code",
    "interview_date",
    "department_code",
    "municipality_code",
    "urban_rural",
    "respondent_age",
    "respondent_sex",
    "household_size",
    "monthly_income_gtq",
)
MAX_FILE_BYTES = 10 * 1024 * 1024
IDENTIFIER_PATTERN = re.compile(r"^[A-Za-z0-9_-]{1,64}$")
CODE_PATTERN = re.compile(r"^[A-Za-z0-9_-]{1,10}$")
SURVEY_PATTERN = re.compile(r"^[A-Z0-9_-]{3,30}$")


@dataclass(frozen=True)
class ValidatedRecord:
    """Fila válida preparada para staging, no para exposición HTTP."""

    row_number: int
    values: dict[str, str]


@dataclass(frozen=True)
class ValidationResult:
    """Respuesta pública y filas válidas internas de una validación."""

    response: ValidationResponse
    valid_records: list[ValidatedRecord]


def _issue(
    code: str,
    severity: str,
    message: str,
    *,
    row: int | None = None,
    column: str | None = None,
    value: str | None = None,
) -> ValidationIssue:
    return ValidationIssue(
        code=code,
        severity=severity,  # type: ignore[arg-type]
        row=row,
        column=column,
        message=message,
        value=value,
    )


def _base_response(file_name: str, issues: list[ValidationIssue], total_rows: int = 0) -> ValidationResponse:
    has_errors = any(item.severity == "ERROR" for item in issues)
    status = "REJECTED" if has_errors else "REVIEW_REQUIRED"
    return ValidationResponse(
        batch_id=str(uuid4()),
        file_name=file_name,
        status=status,
        total_rows=total_rows,
        valid_rows=0,
        rejected_rows=0,
        warning_rows=0,
        issues=issues,
    )


def _validate_row(row: dict[str, str], row_number: int, seen_ids: set[str]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    normalized = {key: value.strip() for key, value in row.items()}

    if normalized != row:
        issues.append(
            _issue(
                "FIELD-013",
                "WARNING",
                "Se eliminaron espacios externos de uno o más campos.",
                row=row_number,
            )
        )

    for column in REQUIRED_COLUMNS:
        if not normalized.get(column, ""):
            issues.append(
                _issue(
                    "FIELD-001",
                    "ERROR",
                    "El campo obligatorio está vacío.",
                    row=row_number,
                    column=column,
                )
            )

    record_id = normalized.get("record_id", "")
    if record_id and not IDENTIFIER_PATTERN.fullmatch(record_id):
        issues.append(
            _issue(
                "FIELD-002",
                "ERROR",
                "record_id contiene caracteres no permitidos.",
                row=row_number,
                column="record_id",
                value=record_id,
            )
        )
    elif record_id in seen_ids:
        issues.append(
            _issue(
                "FIELD-003",
                "ERROR",
                "record_id está duplicado dentro del lote.",
                row=row_number,
                column="record_id",
                value=record_id,
            )
        )
    elif record_id:
        seen_ids.add(record_id)

    survey_code = normalized.get("survey_code", "")
    if survey_code and not SURVEY_PATTERN.fullmatch(survey_code):
        issues.append(
            _issue(
                "FIELD-004",
                "ERROR",
                "survey_code debe usar mayúsculas, números, guion o guion bajo.",
                row=row_number,
                column="survey_code",
                value=survey_code,
            )
        )

    interview_date = normalized.get("interview_date", "")
    if interview_date:
        try:
            parsed_date = datetime.strptime(interview_date, "%Y-%m-%d").date()
        except ValueError:
            issues.append(
                _issue(
                    "FIELD-005",
                    "ERROR",
                    "La fecha no tiene formato YYYY-MM-DD o no es válida.",
                    row=row_number,
                    column="interview_date",
                    value=interview_date,
                )
            )
        else:
            if parsed_date > date.today():
                issues.append(
                    _issue(
                        "FIELD-006",
                        "ERROR",
                        "La fecha de entrevista no puede ser futura.",
                        row=row_number,
                        column="interview_date",
                        value=interview_date,
                    )
                )

    for column in ("department_code", "municipality_code"):
        value = normalized.get(column, "")
        if value and not CODE_PATTERN.fullmatch(value):
            issues.append(
                _issue(
                    "FIELD-007",
                    "ERROR",
                    "El código territorial contiene caracteres no permitidos o supera 10 caracteres.",
                    row=row_number,
                    column=column,
                    value=value,
                )
            )

    if normalized.get("urban_rural") and normalized["urban_rural"] not in {"U", "R"}:
        issues.append(
            _issue(
                "FIELD-008",
                "ERROR",
                "urban_rural solo puede ser U o R.",
                row=row_number,
                column="urban_rural",
                value=normalized["urban_rural"],
            )
        )

    _validate_integer_range(issues, normalized, row_number, "respondent_age", 0, 120, "FIELD-009")

    if normalized.get("respondent_sex") and normalized["respondent_sex"] not in {"F", "M", "X", "NR"}:
        issues.append(
            _issue(
                "FIELD-010",
                "ERROR",
                "respondent_sex solo puede ser F, M, X o NR.",
                row=row_number,
                column="respondent_sex",
                value=normalized["respondent_sex"],
            )
        )

    _validate_integer_range(issues, normalized, row_number, "household_size", 1, 50, "FIELD-011")

    income = normalized.get("monthly_income_gtq", "")
    if income:
        try:
            decimal_income = Decimal(income)
        except InvalidOperation:
            issues.append(
                _issue(
                    "FIELD-012",
                    "ERROR",
                    "monthly_income_gtq debe ser un número válido.",
                    row=row_number,
                    column="monthly_income_gtq",
                    value=income,
                )
            )
        else:
            if decimal_income < 0 or decimal_income.as_tuple().exponent < -2:
                issues.append(
                    _issue(
                        "FIELD-012",
                        "ERROR",
                        "monthly_income_gtq no puede ser negativo y debe tener máximo dos decimales.",
                        row=row_number,
                        column="monthly_income_gtq",
                        value=income,
                    )
                )

    return issues


def _validate_integer_range(
    issues: list[ValidationIssue],
    row: dict[str, str],
    row_number: int,
    column: str,
    minimum: int,
    maximum: int,
    code: str,
) -> None:
    value = row.get(column, "")
    if not value:
        return
    try:
        parsed = int(value)
    except ValueError:
        parsed = None
    if parsed is None or not minimum <= parsed <= maximum:
        issues.append(
            _issue(
                code,
                "ERROR",
                f"{column} debe ser un entero entre {minimum} y {maximum}.",
                row=row_number,
                column=column,
                value=value,
            )
        )


def validate_csv_result(file_name: str, content: bytes) -> ValidationResult:
    """Valida un archivo CSV en memoria sin persistir sus registros."""

    if Path(file_name).suffix.lower() != ".csv":
        return ValidationResult(
            _base_response(
                file_name,
                [_issue("FILE-001", "ERROR", "Solo se aceptan archivos con extensión .csv.")],
            ),
            [],
        )

    if len(content) > MAX_FILE_BYTES:
        return ValidationResult(
            _base_response(
                file_name,
                [_issue("FILE-009", "ERROR", "El archivo supera el límite de 10 MB.")],
            ),
            [],
        )

    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError:
        return ValidationResult(
            _base_response(
                file_name,
                [_issue("FILE-003", "ERROR", "El archivo debe estar codificado en UTF-8.")],
            ),
            [],
        )

    if not text.strip():
        return ValidationResult(
            _base_response(
                file_name,
                [_issue("FILE-002", "ERROR", "El archivo está vacío o no contiene filas de datos.")],
            ),
            [],
        )

    try:
        rows = list(csv.reader(io.StringIO(text, newline=""), strict=True))
    except csv.Error:
        return ValidationResult(
            _base_response(
                file_name,
                [_issue("FILE-008", "ERROR", "La estructura del archivo CSV no se puede interpretar.")],
            ),
            [],
        )

    if len(rows) < 2:
        return ValidationResult(
            _base_response(
                file_name,
                [_issue("FILE-002", "ERROR", "El archivo debe contener encabezado y al menos una fila de datos.")],
            ),
            [],
        )

    header = rows[0]
    data_rows = rows[1:]
    issues: list[ValidationIssue] = []

    if len(set(header)) != len(header):
        issues.append(_issue("FILE-005", "ERROR", "El encabezado contiene columnas duplicadas."))
    missing_columns = [column for column in REQUIRED_COLUMNS if column not in header]
    if missing_columns:
        issues.append(
            _issue(
                "FILE-004",
                "ERROR",
                f"Faltan columnas obligatorias: {', '.join(missing_columns)}.",
            )
        )
    extra_columns = [column for column in header if column not in REQUIRED_COLUMNS]
    if extra_columns:
        issues.append(
            _issue(
                "FILE-006",
                "WARNING",
                f"El archivo contiene columnas no previstas: {', '.join(extra_columns)}.",
            )
        )

    if any(issue.severity == "ERROR" for issue in issues):
        response = _base_response(file_name, issues, len(data_rows))
        response.rejected_rows = len(data_rows)
        return ValidationResult(response, [])

    seen_ids: set[str] = set()
    valid_rows = 0
    rejected_rows = 0
    warning_row_numbers: set[int] = set()
    valid_records: list[ValidatedRecord] = []

    for row_number, values in enumerate(data_rows, start=2):
        if len(values) != len(header):
            issues.append(
                _issue(
                    "FILE-007",
                    "ERROR",
                    "La fila no tiene la misma cantidad de campos que el encabezado.",
                    row=row_number,
                )
            )
            rejected_rows += 1
            continue

        row = dict(zip(header, values))
        normalized = {key: value.strip() for key, value in row.items()}
        row_issues = _validate_row(row, row_number, seen_ids)
        issues.extend(row_issues)
        if any(item.severity == "WARNING" for item in row_issues):
            warning_row_numbers.add(row_number)
        if any(item.severity == "ERROR" for item in row_issues):
            rejected_rows += 1
        else:
            valid_rows += 1
            valid_records.append(ValidatedRecord(row_number=row_number, values=normalized))

    status = "REVIEW_REQUIRED" if rejected_rows or issues else "READY_FOR_CONFIRMATION"
    return ValidationResult(
        response=ValidationResponse(
            batch_id=str(uuid4()),
            file_name=file_name,
            status=status,
            total_rows=len(data_rows),
            valid_rows=valid_rows,
            rejected_rows=rejected_rows,
            warning_rows=len(warning_row_numbers),
            issues=issues,
        ),
        valid_records=valid_records,
    )


def validate_csv(file_name: str, content: bytes) -> ValidationResponse:
    """Valida un CSV y devuelve solo el contrato público de respuesta."""

    return validate_csv_result(file_name, content).response
