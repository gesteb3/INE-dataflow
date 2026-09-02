"""Consultas agregadas de solo lectura para reportes y Power BI."""

import psycopg
from psycopg.rows import dict_row
from uuid import UUID

from app.db import database_url


def get_report_summary(batch_id: UUID | None = None) -> dict:
    """Obtiene indicadores generales de lotes, calidad y confirmaciones."""

    with psycopg.connect(database_url(), row_factory=dict_row) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                WITH filtered_batches AS (
                    SELECT *
                    FROM survey_batches
                    WHERE (%s IS NULL OR id = %s)
                )
                SELECT
                    COUNT(*)::INTEGER AS total_batches,
                    COUNT(*) FILTER (WHERE status = 'CONFIRMED')::INTEGER AS confirmed_batches,
                    COALESCE(SUM(total_rows), 0)::INTEGER AS total_input_rows,
                    COALESCE(SUM(valid_rows) FILTER (WHERE status = 'CONFIRMED'), 0)::INTEGER
                        AS confirmed_valid_rows,
                    COALESCE(SUM(rejected_rows), 0)::INTEGER AS total_rejected_rows,
                    (
                        SELECT COUNT(*)::INTEGER
                        FROM validation_errors e
                        INNER JOIN filtered_batches b ON b.id = e.batch_id
                    ) AS total_validation_errors,
                    MAX(confirmed_at) AS last_confirmed_at
                FROM filtered_batches
                """,
                (batch_id, batch_id),
            )
            return cursor.fetchone()


def get_department_report(batch_id: UUID | None = None) -> list[dict]:
    """Obtiene métricas de registros confirmados agrupadas por departamento."""

    with psycopg.connect(database_url(), row_factory=dict_row) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    department_code,
                    COUNT(*)::INTEGER AS valid_records,
                    COUNT(*) FILTER (WHERE urban_rural = 'U')::INTEGER AS urban_records,
                    COUNT(*) FILTER (WHERE urban_rural = 'R')::INTEGER AS rural_records,
                    ROUND(AVG(respondent_age), 2) AS average_age,
                    ROUND(AVG(household_size), 2) AS average_household_size,
                    ROUND(AVG(monthly_income_gtq), 2) AS average_monthly_income_gtq,
                    COALESCE(ROUND(SUM(monthly_income_gtq), 2), 0)::NUMERIC
                        AS total_monthly_income_gtq
                FROM valid_survey_records
                WHERE (%s IS NULL OR batch_id = %s)
                GROUP BY department_code
                ORDER BY department_code
                """,
                (batch_id, batch_id),
            )
            return cursor.fetchall()
