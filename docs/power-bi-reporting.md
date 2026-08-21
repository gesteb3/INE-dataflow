# Capa de reportes para Power BI

## Objetivo

Esta capa expone únicamente datos agregados y de solo lectura para que Power BI pueda consumir indicadores del MVP sin conectarse directamente a las tablas operativas de PostgreSQL.

## Endpoints disponibles

Con Docker Compose activo:

| Endpoint | Uso |
| --- | --- |
| `GET /api/v1/reports/summary` | Indicadores generales de lotes, filas válidas, rechazadas y errores. |
| `GET /api/v1/reports/by-department` | Registros válidos, distribución urbana/rural, edad, tamaño del hogar e ingresos por departamento. |

URLs locales:

```text
http://localhost:8001/api/v1/reports/summary
http://localhost:8001/api/v1/reports/by-department
```

## Consumo inicial desde Power BI Desktop

1. Abrir **Obtener datos > Web**.
2. Seleccionar **Opciones avanzadas** si se solicita una URL completa.
3. Introducir uno de los endpoints anteriores.
4. Elegir **Anónimo** para el entorno local del MVP.
5. Cargar el resultado JSON y convertirlo en tabla.

La conexión local solo funciona mientras la API esté ejecutándose en la computadora. Para publicar un informe en Power BI Service será necesario definir una infraestructura accesible, autenticación, red segura y una política de protección de datos.

## Indicadores iniciales sugeridos

- Lotes recibidos y confirmados.
- Filas procesadas, válidas y rechazadas.
- Total de errores de validación.
- Registros válidos por departamento.
- Distribución urbana y rural.
- Promedio de edad, tamaño del hogar e ingreso mensual.

Los datos actuales son sintéticos y sirven únicamente para la demostración académica.
