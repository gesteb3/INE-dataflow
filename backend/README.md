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

La documentación interactiva estará disponible en `http://127.0.0.1:8000/docs` y el estado del servicio en `http://127.0.0.1:8000/health` cuando se ejecute directamente con Uvicorn.

## Ejecución con Docker Compose

Desde la raíz del repositorio:

```bash
docker compose up --build
```

Con el contenedor activo, abrir:

- Swagger UI: `http://localhost:8001/docs`
- ReDoc: `http://localhost:8001/redoc`
- Healthcheck: `http://localhost:8001/health`
- Esquema OpenAPI: `http://localhost:8001/openapi.json`

El puerto externo predeterminado es `8001` porque `8000` puede estar ocupado por otro servicio local. Se puede cambiar con la variable `INE_DATAFLOW_API_PORT`.

Para detener el servicio:

```bash
docker compose down
```

Ejecutar las pruebas desde la raíz del repositorio o desde esta carpeta:

```bash
pytest
```
