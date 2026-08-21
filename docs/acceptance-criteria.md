# Criterios de aceptación del MVP

Estos criterios describen el comportamiento esperado del flujo de procesamiento. No constituyen todavía pruebas automatizadas ni una implementación.

## Carga y estructura

- [ ] Se acepta un archivo CSV con codificación UTF-8 y encabezado válido.
- [ ] Se rechaza un archivo vacío, con extensión incorrecta, sin columnas obligatorias o con encabezados duplicados.
- [ ] Se informa claramente cuando una fila tiene una cantidad de campos distinta a la del encabezado.
- [ ] El procesamiento no continúa cuando el archivo tiene un error estructural que impide interpretar sus filas.

## Validación de registros

- [ ] Cada fila se valida según el contrato vigente y produce un estado: válida o rechazada.
- [ ] Los campos obligatorios vacíos generan un error identificable.
- [ ] Fechas, enumeraciones, enteros, decimales y rangos se validan con reglas explícitas.
- [ ] Los `record_id` duplicados no se almacenan como registros válidos.
- [ ] Las advertencias no rechazan el registro, pero quedan registradas.

## Trazabilidad

- [ ] Cada carga tiene un identificador de lote.
- [ ] Cada error conserva código, fila, columna cuando corresponda y mensaje legible.
- [ ] El resultado informa totales de filas leídas, válidas, rechazadas y advertencias.
- [ ] Un error de una fila no elimina silenciosamente las demás filas procesables.
- [ ] Los logs técnicos no exponen datos personales completos.

## Calidad y operación

- [ ] Las reglas del contrato y el catálogo de errores son la referencia común para backend, base de datos, pruebas y visualizaciones.
- [ ] El procesamiento de un archivo de prueba sintético de al menos 1,000 filas produce un resumen reproducible.
- [ ] El mismo archivo y las mismas reglas producen el mismo resultado al reprocesarse.
- [ ] Los registros válidos y los errores quedan preparados para almacenarse por separado en PostgreSQL.

## Fuera de alcance del MVP

- [ ] No se implementa todavía la imputación estadística.
- [ ] No se implementan reglas avanzadas de valores atípicos.
- [ ] No se incorporan datos personales directos sin una revisión de privacidad.
- [ ] No se define todavía el dashboard de Power BI ni la interfaz final de Angular.
