# Backend

Esqueleto inicial de la API de INE DataFlow construido con FastAPI.

## Alcance actual

- Punto de entrada de la aplicación en `app/main.py`.
- Endpoint `GET /health` para comprobar disponibilidad.
- Prueba automatizada del endpoint con pytest.
- Sin conexión a PostgreSQL y sin procesamiento de archivos CSV todavía.

## Ejecución local

Desde esta carpeta, crear un entorno virtual e instalar las dependencias:

```bash
python -m venv .venv
source .venv/bin/activate       # Linux/macOS
.venv\\Scripts\\Activate.ps1    # Windows PowerShell
pip install -r requirements.txt
```

Iniciar la API:

```bash
uvicorn app.main:app --reload
```

La documentación interactiva estará disponible en `http://127.0.0.1:8000/docs` y el estado del servicio en `http://127.0.0.1:8000/health`.

Ejecutar las pruebas desde la raíz del repositorio o desde esta carpeta:

```bash
pytest
```
