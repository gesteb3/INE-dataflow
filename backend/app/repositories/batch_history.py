"""Consultas de solo lectura para el historial operativo."""

from uuid import UUID

import psycopg
from psycopg.rows import dict_row

from app.db import database_url


def list_batches(limit: int = 50) -> list[dict]:
    with psycopg.connect(database_url(), row_factory=dict_row) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id::TEXT AS batch_id, file_name, status, total_rows,
                       valid_rows, rejected_rows, warning_rows, created_at, confirmed_at
                FROM survey_batches
                ORDER BY created_at DESC
                LIMIT %s
                """,
                (limit,),
            )
            return cursor.fetchall()


def list_batch_issues(batch_id: UUID) -> list[dict]:
    with psycopg.connect(database_url(), row_factory=dict_row) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT code, severity, row_number AS row, column_name AS column,
                       message, received_value AS value
                FROM validation_errors
                WHERE batch_id = %s
                ORDER BY id
                """,
                (batch_id,),
            )
            return cursor.fetchall()


def list_valid_records(batch_id: UUID) -> list[dict]:
    """Devuelve únicamente las filas publicadas de un lote confirmado."""

    with psycopg.connect(database_url(), row_factory=dict_row) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT v.record_id, v.survey_code, v.interview_date::TEXT AS interview_date,
                       v.department_code, v.municipality_code, v.urban_rural,
                       v.respondent_age, v.respondent_sex, v.household_size,
                       v.monthly_income_gtq
                FROM valid_survey_records v
                INNER JOIN survey_batches b ON b.id = v.batch_id
                WHERE v.batch_id = %s AND b.status = 'CONFIRMED'
                ORDER BY v.id
                """,
                (batch_id,),
            )
            return cursor.fetchall()
