# Backend

Esqueleto inicial de la API de INE DataFlow construido con FastAPI.

## Alcance actual

- Punto de entrada de la aplicación en `app/main.py`.
- Endpoint `GET /health` para comprobar disponibilidad.
- Endpoint `GET /health/db` para comprobar conexión con PostgreSQL.
- Endpoint `POST /api/v1/uploads/validate` para validar un CSV y guardar el lote en staging.
- Endpoint `POST /api/v1/uploads/{batch_id}/confirm` para publicar las filas válidas después de la revisión.
- Prueba automatizada del endpoint con pytest.
- Persistencia de lotes, errores y registros válidos mediante PostgreSQL.

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
- Healthcheck PostgreSQL: `http://localhost:8001/health/db`
- Esquema OpenAPI: `http://localhost:8001/openapi.json`

En Swagger, usar `POST /api/v1/uploads/validate`, seleccionar el archivo `data/samples/encuesta_demo.csv` y presionar **Execute**. El resultado mostrará registros válidos, rechazados, advertencias y códigos de error. Después de revisar el resultado, usar el `batch_id` devuelto en `POST /api/v1/uploads/{batch_id}/confirm`.

El puerto externo predeterminado es `8001` porque `8000` puede estar ocupado por otro servicio local. Se puede cambiar con la variable `INE_DATAFLOW_API_PORT`.

PostgreSQL queda disponible en el puerto local `5433` y usa las variables de `.env.example`. Las credenciales reales deben mantenerse en un archivo `.env` local, que no se sube a Git. La interfaz Angular queda disponible en `http://localhost:4200` cuando se levanta todo el Compose.

Para detener el servicio:

```bash
docker compose down
```

Ejecutar las pruebas desde la raíz del repositorio o desde esta carpeta:

```bash
pytest
```
