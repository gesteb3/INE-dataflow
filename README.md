# INE DataFlow

INE DataFlow es un proyecto académico para el Instituto Nacional de Estadística de Guatemala. Su objetivo es construir un flujo de recepción y procesamiento de archivos CSV provenientes de encuestas, con validación de calidad, almacenamiento de registros válidos y errores, y visualización posterior de la información.

## Estado del proyecto

El proyecto se encuentra en la fase 7: ya cuenta con backend FastAPI, validación de CSV, Docker Compose, PostgreSQL 16, staging, confirmación de registros válidos, una interfaz Angular y endpoints de reportes de solo lectura para preparar Power BI. El pipeline de CI para Azure DevOps valida pruebas, build y contenedores. Power BI todavía queda para una fase posterior.

## Arquitectura propuesta

```text
Archivo CSV de encuesta
          |
          v
   API de carga (FastAPI)
          |
          v
  Pipeline de procesamiento
  - lectura y normalización
  - validaciones de calidad
  - clasificación de registros
          |
          +--------------------+
          v                    v
 PostgreSQL 16          Registro de errores
 registros válidos      y trazabilidad
          |
          v
 Angular + Power BI
 visualización y análisis
```

Docker Compose coordinará los servicios locales del proyecto. FastAPI expondrá la API para la carga y consulta; PostgreSQL 16 almacenará los resultados y los errores; Angular ofrecerá la interfaz web; y Power BI consumirá datos preparados para análisis. Azure DevOps ejecutará las validaciones automatizadas y las pruebas con pytest. Git y GitHub se utilizarán para el control de versiones y la colaboración.

## Tecnologías

| Área | Tecnología |
| --- | --- |
| Backend | Python + FastAPI |
| Base de datos | PostgreSQL 16 |
| Frontend | Angular |
| Contenedores | Docker Compose |
| Testing | pytest |
| Integración continua | Azure DevOps |
| Visualización | Power BI |
| Control de versiones | Git + GitHub |

## Estructura inicial

```text
.
├── backend/
│   ├── app/                 # Código inicial de la API FastAPI
│   ├── tests/               # Pruebas automatizadas
│   ├── requirements.txt     # Dependencias Python
│   └── pytest.ini           # Configuración de pytest
├── data/
│   └── samples/              # Datos sintéticos para pruebas
│       ├── encuesta_demo.csv # Muestra pequeña con errores intencionales
│       └── encuesta_10000.csv# Muestra de volumen con 10,000 filas válidas
├── scripts/
│   └── generate_synthetic_survey.js # Generador reproducible de datos de prueba
├── database/
│   ├── migrations/          # Evolución del esquema, en fases posteriores
│   └── seeds/               # Datos de referencia, en fases posteriores
├── docs/
│   ├── architecture/        # Decisiones y diagramas de arquitectura
│   └── decisions/           # Registro de decisiones técnicas
├── azure-pipelines.yml      # Pipeline de CI para Azure DevOps
├── .gitignore
└── README.md
```

Las carpetas vacías se conservan mediante archivos `.gitkeep` hasta que reciban contenido real.

## Documentación de la fase 2

- [Contrato de datos CSV](docs/data-contract.md)
- [Reglas de validación de calidad](docs/validation-rules.md)
- [Catálogo inicial de errores](docs/error-catalog.md)
- [Criterios de aceptación del MVP](docs/acceptance-criteria.md)
- [Flujo y diseño del MVP](docs/architecture/mvp-flow.md)
- [Documentación del backend](backend/README.md)
- [Capa de reportes para Power BI](docs/power-bi-reporting.md)
- [OCR de encuestas en papel](docs/ocr.md)

## Ejecutar la API con Docker

Desde la raíz del proyecto:

```bash
docker compose up --build
```

Luego abre [Swagger UI](http://localhost:8001/docs) para explorar los endpoints de la API.

Compose también levanta PostgreSQL 16. El estado de la conexión se puede comprobar en [health de PostgreSQL](http://localhost:8001/health/db).

Las métricas operativas compatibles con Prometheus están disponibles en [http://localhost:8001/metrics](http://localhost:8001/metrics).

La interfaz Angular está disponible en [http://localhost:4200](http://localhost:4200). Desde allí se puede cargar el CSV, revisar sus incidencias y confirmar el lote.

Los reportes agregados están disponibles en [resumen](http://localhost:8001/api/v1/reports/summary) y [métricas por departamento](http://localhost:8001/api/v1/reports/by-department).

## Principios iniciales

- Separar procesamiento, persistencia y presentación.
- Conservar los errores de validación para facilitar auditoría y corrección.
- Mantener configuraciones y secretos fuera del control de versiones.
- Automatizar pruebas y validaciones antes de integrar cambios.
- Avanzar por fases pequeñas y revisables.

## Ejecutar el frontend

Desde la raíz del proyecto:

```bash
docker compose up --build
```

Luego abre [http://localhost:4200](http://localhost:4200), selecciona `data/samples/encuesta_demo.csv`, valida el archivo y confirma el lote después de revisar sus incidencias.

Para una prueba de volumen, usa `data/samples/encuesta_10000.csv`. Es un archivo sintético de 10,000 filas válidas y no contiene datos personales reales.

## Integración continua

El archivo `azure-pipelines.yml` se ejecuta en cada cambio dirigido a `main` y en pull requests hacia `main`. Actualmente realiza:

- Instalación de dependencias y pruebas del backend con pytest.
- Instalación de dependencias, pruebas y build de Angular.
- Validación de Docker Compose.
- Construcción de las imágenes de API y frontend.

Para activarlo en Azure DevOps, crear un pipeline nuevo apuntando al repositorio de GitHub y seleccionar `azure-pipelines.yml`.

## Próxima fase

La siguiente fase será definir el modelo de consumo para Power BI, los indicadores del dashboard y las medidas de seguridad antes de publicar datos fuera del entorno local.
