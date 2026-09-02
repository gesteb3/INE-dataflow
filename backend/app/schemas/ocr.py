"""Contratos para la lectura preliminar de encuestas escaneadas."""

from typing import Literal

from pydantic import BaseModel


class OCRFileResult(BaseModel):
    file_name: str
    status: Literal["PROCESSED", "ERROR"]
    extracted_text: str
    fields: dict[str, str | None]
    message: str | None = None

