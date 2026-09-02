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
