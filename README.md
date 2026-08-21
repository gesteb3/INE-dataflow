# INE DataFlow

INE DataFlow es un proyecto académico para el Instituto Nacional de Estadística de Guatemala. Su objetivo es construir un flujo de recepción y procesamiento de archivos CSV provenientes de encuestas, con validación de calidad, almacenamiento de registros válidos y errores, y visualización posterior de la información.

## Estado del proyecto

El proyecto se encuentra en la fase 3: ya existe un esqueleto mínimo del backend con FastAPI y una prueba automatizada del endpoint de salud. Todavía no se implementan la carga y validación de CSV, el frontend, la base de datos, los contenedores ni los pipelines de CI.

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
├── database/
│   ├── migrations/          # Evolución del esquema, en fases posteriores
│   └── seeds/               # Datos de referencia, en fases posteriores
├── docs/
│   ├── architecture/        # Decisiones y diagramas de arquitectura
│   └── decisions/           # Registro de decisiones técnicas
├── .gitignore
└── README.md
```

Las carpetas vacías se conservan mediante archivos `.gitkeep` hasta que reciban contenido real.

## Documentación de la fase 2

- [Contrato de datos CSV](docs/data-contract.md)
- [Reglas de validación de calidad](docs/validation-rules.md)
- [Catálogo inicial de errores](docs/error-catalog.md)
- [Criterios de aceptación del MVP](docs/acceptance-criteria.md)
- [Documentación del backend](backend/README.md)

## Principios iniciales

- Separar procesamiento, persistencia y presentación.
- Conservar los errores de validación para facilitar auditoría y corrección.
- Mantener configuraciones y secretos fuera del control de versiones.
- Automatizar pruebas y validaciones antes de integrar cambios.
- Avanzar por fases pequeñas y revisables.

## Próxima fase

La siguiente fase deberá definirse explícitamente antes de comenzar. Esta entrega no incluye commits ni cambios fuera de la estructura y documentación inicial.
