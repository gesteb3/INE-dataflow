"""Conexión mínima a PostgreSQL para healthchecks del servicio."""

import os

import psycopg


def database_url() -> str:
    """Obtiene la URL de PostgreSQL desde el entorno."""

    return os.getenv(
        "DATABASE_URL",
        "postgresql://ine_dataflow:ine_dataflow_dev@localhost:5433/inedataflow",
    )


def database_is_healthy() -> bool:
    """Comprueba que PostgreSQL acepta una consulta sencilla."""

    try:
        with psycopg.connect(database_url(), connect_timeout=2) as connection:
            connection.execute("SELECT 1")
    except psycopg.Error:
        return False
    return True
