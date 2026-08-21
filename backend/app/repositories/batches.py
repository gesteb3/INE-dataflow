"""Persistencia de lotes, staging y confirmación de registros válidos."""

from datetime import date
from decimal import Decimal
from uuid import UUID

import psycopg
from psycopg.rows import dict_row

from app.db import database_url
from app.schemas.validation import ConfirmationResponse, ValidationResponse
from app.services.csv_validator import ValidatedRecord


class BatchNotFoundError(Exception):
    """El lote solicitado no existe."""


class BatchAlreadyConfirmedError(Exception):
    """El lote ya fue confirmado y no debe procesarse dos veces."""


class BatchNotConfirmableError(Exception):
    """El estado actual del lote no permite confirmarlo."""


def _to_date(value: str) -> date:
    return date.fromisoformat(value)


def _to_decimal(value: str) -> Decimal | None:
    return Decimal(value) if value else None


def persist_validation_result(
    response: ValidationResponse,
    valid_records: list[ValidatedRecord],
) -> None:
    """Guarda el resultado de validación como lote pendiente de revisión."""

    with psycopg.connect(database_url()) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO survey_batches
                    (id, file_name, status, total_rows, valid_rows, rejected_rows, warning_rows)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    UUID(response.batch_id),
                    response.file_name,
                    response.status,
                    response.total_rows,
                    response.valid_rows,
                    response.rejected_rows,
                    response.warning_rows,
                ),
            )

            for issue in response.issues:
                cursor.execute(
                    """
                    INSERT INTO validation_errors
                        (batch_id, row_number, code, severity, column_name, message, received_value)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        UUID(response.batch_id),
                        issue.row,
                        issue.code,
                        issue.severity,
                        issue.column,
                        issue.message,
                        issue.value,
                    ),
                )

            for record in valid_records:
                values = record.values
                cursor.execute(
                    """
                    INSERT INTO staged_survey_records
                        (batch_id, row_number, record_id, survey_code, interview_date,
                         department_code, municipality_code, urban_rural, respondent_age,
                         respondent_sex, household_size, monthly_income_gtq)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        UUID(response.batch_id),
                        record.row_number,
                        values["record_id"],
                        values["survey_code"],
                        _to_date(values["interview_date"]),
                        values["department_code"],
                        values["municipality_code"],
                        values["urban_rural"],
                        int(values["respondent_age"]),
                        values["respondent_sex"],
                        int(values["household_size"]),
                        _to_decimal(values["monthly_income_gtq"]),
                    ),
                )


def confirm_batch(batch_id: UUID) -> ConfirmationResponse:
    """Mueve filas válidas de staging a la tabla definitiva."""

    with psycopg.connect(database_url(), row_factory=dict_row) as connection:
        with connection.transaction():
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT status, valid_rows FROM survey_batches WHERE id = %s FOR UPDATE",
                    (batch_id,),
                )
                batch = cursor.fetchone()
                if batch is None:
                    raise BatchNotFoundError
                if batch["status"] == "CONFIRMED":
                    raise BatchAlreadyConfirmedError
                if batch["status"] == "REJECTED":
                    raise BatchNotConfirmableError

                cursor.execute(
                    """
                    INSERT INTO valid_survey_records
                        (batch_id, record_id, survey_code, interview_date, department_code,
                         municipality_code, urban_rural, respondent_age, respondent_sex,
                         household_size, monthly_income_gtq)
                    SELECT batch_id, record_id, survey_code, interview_date, department_code,
                           municipality_code, urban_rural, respondent_age, respondent_sex,
                           household_size, monthly_income_gtq
                    FROM staged_survey_records
                    WHERE batch_id = %s
                    ON CONFLICT (batch_id, record_id) DO NOTHING
                    """,
                    (batch_id,),
                )
                cursor.execute(
                    """
                    UPDATE survey_batches
                    SET status = 'CONFIRMED', confirmed_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                    RETURNING confirmed_at, valid_rows
                    """,
                    (batch_id,),
                )
                confirmed = cursor.fetchone()

    return ConfirmationResponse(
        batch_id=str(batch_id),
        status="CONFIRMED",
        valid_rows=confirmed["valid_rows"],
        confirmed_at=confirmed["confirmed_at"],
    )
