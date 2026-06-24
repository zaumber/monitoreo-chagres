# Monitoreo Forestal — Parque Nacional Chagres

Sistema de monitoreo geoespacial que combina imágenes satelitales (Google Earth Engine), un modelo de machine learning y un dashboard interactivo para predecir zonas de estrés forestal ante eventos de sequía en el Parque Nacional Chagres, Panamá.

Demo: [añadir aquí el link de Render]

## Descripción

El Parque Nacional Chagres abastece de agua al Canal de Panamá y a la ciudad de Panamá. Este proyecto extrae series históricas de NDVI, temperatura superficial (LST), precipitación y el índice ONI (El Niño / La Niña) desde el año 2000, entrena un modelo de regresión para predecir anomalías de NDVI a partir de las condiciones climáticas recientes, y aplica ese modelo sobre una grilla espacial del parque para generar un mapa de riesgo de estrés forestal mes a mes.

El resultado se presenta en un dashboard interactivo construido con Dash, con mapa, gráficos históricos, indicadores y filtros.

## Contenido

- [Fuentes de datos](#fuentes-de-datos)
- [Modelo de machine learning](#modelo-de-machine-learning)
- [Dashboard](#dashboard)
- [Estructura del repositorio](#estructura-del-repositorio)
- [Instalación](#instalación)
- [Uso](#uso)
- [Despliegue](#despliegue)
- [Limitaciones](#limitaciones)
- [Tecnologías](#tecnologías)

## Fuentes de datos

Los índices se calculan directamente sobre las colecciones de Google Earth Engine, no se descargan productos pre-calculados.

- NDVI: `MODIS/061/MOD13A3`, mensual, 1 km. Se escala por 0.0001 y se reduce con la media (`reduceRegion`) sobre la geometría del parque.
- LST (temperatura superficial): `MODIS/061/MOD11A2`, agregado de 8 días a mensual. Conversión de Kelvin a Celsius (×0.02 − 273.15).
- Precipitación: `ECMWF/ERA5_LAND/MONTHLY_AGGR`, mensual, ~9 km. Conversión de metros a milímetros.
- ONI (El Niño / La Niña): serie mensual de NOAA, descargada como CSV y reestructurada a formato largo.

## Modelo de machine learning

El modelo predice la anomalía de NDVI respecto a la climatología mensual histórica del parque (Random Forest).

Variables predictoras: lags de 1 a 3 meses de NDVI/anomalía, ONI, LST y precipitación, promedio móvil de 3 meses, y componentes cíclicas del mes (seno/coseno).

Validación con `TimeSeriesSplit` (5 folds) para evitar fuga de información temporal, y un conjunto de prueba final con los últimos 12 meses.

La salida es una probabilidad de estrés forestal, clasificada en tres niveles de riesgo:

- Alto: probabilidad ≥ 70%
- Moderado: probabilidad entre 45% y 70%
- Bajo: probabilidad < 45%

El modelo entrenado se guarda en `modelo_chagres.pkl` junto con la climatología necesaria para reconstruir el NDVI absoluto.

Para la predicción espacial, el parque se divide en una grilla regular (~5 km por celda). El modelo se aplica celda por celda, combinando el NDVI histórico propio de cada celda con las variables climáticas globales, y el resultado se exporta como un GeoJSON por mes en `predicciones_map/`.

## Dashboard

Construido con Dash y Plotly. Incluye:

- Mapa interactivo (dash-leaflet) con las celdas del parque coloreadas según su nivel de riesgo de estrés forestal.
- Cuatro gráficos históricos: NDVI (con la predicción a futuro superpuesta), LST, precipitación e índice ONI.
- Panel de indicadores con el conteo y porcentaje de zonas en cada nivel de riesgo para el mes seleccionado.
- Filtros: selector de mes predicho, rango de años para las gráficas históricas, y [añadir aquí el tercer filtro si ya está implementado].

## Estructura del repositorio

```
app.py                          Dashboard Dash (desplegado en Render)
final-2.ipynb                   Pipeline completo: GEE, features, modelo, predicción espacial
chagres_geometry.geojson        Geometría del Parque Nacional Chagres
data/
  ndvi_mensual_chagres_2000.csv
  lst_mensual_chagres_2000.csv
  precip_mensual_chagres_2000.csv
  oni_mensual_2000.csv
predicciones_map/
  pred_2026_07.geojson ... pred_2026_12.geojson
modelo_chagres.pkl               Modelo Random Forest entrenado
requirements.txt
```

## Instalación

Requiere Python 3.10 o superior.

```bash
git clone <url-del-repo>
cd <nombre-del-repo>
pip install -r requirements.txt
```

## Uso

```bash
python app.py
```

La aplicación queda disponible en `http://localhost:8050`.

El notebook `final-2.ipynb` requiere autenticación con Google Earth Engine (`ee.Authenticate()`) y un proyecto de GEE activo para regenerar los datos desde cero. Los archivos CSV y GeoJSON ya generados permiten correr el dashboard sin necesidad de re-ejecutar el notebook.

## Despliegue

El dashboard está desplegado en [Render](https://render.com) como Web Service de Python, ejecutando `app.py` (servidor Flask/Dash, puerto tomado de la variable de entorno `PORT`).

## Limitaciones

- El pronóstico del índice ONI para los meses futuros usa una aproximación simple, no un pronóstico oficial actualizado de NOAA.
- La grilla espacial (~5 km por celda) es una simplificación y no sustituye un análisis de teledetección de alta resolución.
- Quedó fuera del alcance la propuesta de app móvil o formulario de registro de observaciones de especies.
- No se usó PostgreSQL/PostGIS; los datos se manejan en archivos CSV y GeoJSON.

## Tecnologías

Python, Google Earth Engine (`ee`, `geemap`), Pandas, NumPy, Geopandas, Shapely, Scikit-learn, Dash, Plotly, dash-leaflet, Render.

## Autor

[Tu nombre aquí]
