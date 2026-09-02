# Mapa coroplético departamental

## Propósito

El dashboard muestra la cantidad de registros válidos por departamento de Guatemala. Cada departamento se pinta con una intensidad diferente: los tonos más oscuros representan una mayor cantidad de registros válidos.

La aplicación usa el campo `department_code` del reporte de PostgreSQL y lo relaciona con el nombre del departamento que utiliza el GeoJSON.

## Fuente cartográfica

Se utiliza la capa oficial de departamentos del servicio SIG del Instituto Nacional de Bosques (INAB):

`https://sig.inab.gob.gt/server/rest/services/InformacionBase/Basemap_DinCob2016_2020/MapServer/0`

El GeoJSON simplificado está incluido en `frontend/public/guatemala-departments.geojson` para que el mapa funcione dentro de Docker sin depender de una descarga durante la ejecución.

## Estructura del DataFrame

```python
import pandas as pd

df = pd.DataFrame({
    "department_code": ["01", "02", "03"],
    "departamento": ["Guatemala", "El Progreso", "Sacatepéquez"],
    "valor": [1250, 480, 730],
})
```

El nombre de `departamento` debe coincidir exactamente con `properties.depto` en el GeoJSON. Para este proyecto, el backend entrega códigos y el frontend aplica la equivalencia de los 22 departamentos.

## Ejemplo Python con Plotly

```python
import pandas as pd
import plotly.express as px
import requests

geojson_url = (
    "https://sig.inab.gob.gt/server/rest/services/InformacionBase/"
    "Basemap_DinCob2016_2020/MapServer/0/query?where=1%3D1&outFields=depto"
    "&outSR=4326&geometryPrecision=4&maxAllowableOffset=0.01&f=geojson"
)
geojson = requests.get(geojson_url, timeout=30).json()

df = pd.DataFrame({
    "departamento": ["Guatemala", "El Progreso", "Sacatepéquez"],
    "valor": [1250, 480, 730],
})

fig = px.choropleth(
    df,
    geojson=geojson,
    locations="departamento",
    featureidkey="properties.depto",
    color="valor",
    color_continuous_scale="Blues",
    hover_name="departamento",
    labels={"valor": "Registros válidos"},
)
fig.update_geos(fitbounds="locations", visible=False)
fig.update_layout(title="Registros válidos por departamento")
fig.show()
```

Este ejemplo representa el mismo criterio visual utilizado por el dashboard Angular: datos agregados por departamento, límites geográficos oficiales y una escala de color según el valor.
