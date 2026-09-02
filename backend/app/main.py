"""Punto de entrada de la API de INE DataFlow."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.api.uploads import router as uploads_router
from app.api.reports import router as reports_router
from app.api.auth import router as auth_router
from app.api.batches import router as batches_router
from app.api.users import router as users_router
from app.api.ocr import router as ocr_router
from app.db import database_is_healthy


class HealthResponse(BaseModel):
    """Respuesta del endpoint de disponibilidad del servicio."""

    status: str
    service: str
    version: str


class DatabaseHealthResponse(BaseModel):
    """Respuesta del healthcheck de PostgreSQL."""

    status: str
    database: str


app = FastAPI(
    title="INE DataFlow API",
    description="API para recepción y procesamiento de encuestas del INE.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200", "http://127.0.0.1:4200"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PATCH"],
    allow_headers=["*"],
)

app.include_router(uploads_router, prefix="/api/v1")
app.include_router(reports_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")
app.include_router(batches_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")
app.include_router(ocr_router, prefix="/api/v1")


@app.get("/health", response_model=HealthResponse, tags=["health"])
def health_check() -> HealthResponse:
    """Indica si la API está disponible."""

    return HealthResponse(
        status="ok",
        service="ine-dataflow-api",
        version="0.1.0",
    )


@app.get("/health/db", response_model=DatabaseHealthResponse, tags=["health"])
def database_health_check() -> DatabaseHealthResponse:
    """Comprueba conectividad entre la API y PostgreSQL."""

    if not database_is_healthy():
        raise HTTPException(status_code=503, detail="PostgreSQL no está disponible")
    return DatabaseHealthResponse(status="ok", database="postgresql")
