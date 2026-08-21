"""Punto de entrada de la API de INE DataFlow."""

from fastapi import FastAPI
from pydantic import BaseModel

from app.api.uploads import router as uploads_router


class HealthResponse(BaseModel):
    """Respuesta del endpoint de disponibilidad del servicio."""

    status: str
    service: str
    version: str


app = FastAPI(
    title="INE DataFlow API",
    description="API para recepción y procesamiento de encuestas del INE.",
    version="0.1.0",
)

app.include_router(uploads_router, prefix="/api/v1")


@app.get("/health", response_model=HealthResponse, tags=["health"])
def health_check() -> HealthResponse:
    """Indica si la API está disponible."""

    return HealthResponse(
        status="ok",
        service="ine-dataflow-api",
        version="0.1.0",
    )
