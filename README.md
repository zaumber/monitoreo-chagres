# Monitoreo Forestal — Parque Nacional Chagres
Sistema de monitorea geoespacial del área del parque de chagres, para monitorear la reaccion del parque con respecto a las épocas de sequia y determinar las zonas mas propensas a estas en riesgo debido a la sequia o baja humdedad o propensas a perder bosque

combina datos satelitales (Google Earth Engine), un modelo de machine learning y un dashboard interactivo para predecir zonas de estrés forestal ante eventos de sequía/El Niño en el Parque Nacional Chagres, Panamá.

Demo en vivo: https://monitoreo-chagres.onrender.com/

# ¿Qué hace este proyecto?

El bosque del Parque Nacional Chagres es clave para el abastecimiento de agua del Canal de Panamá y de la ciudad de Panamá. Este proyecto:

Extrae series históricas de NDVI (vigor vegetal), temperatura superficial (LST), precipitación y el índice ONI (El Niño / La Niña) desde 2000 usando Google Earth Engine.
Entrena un modelo de machine learning (Random Forest) que predice anomalías de NDVI a partir de las condiciones climáticas recientes, sin fuga de información (data leakage) temporal.
Aplica ese modelo sobre una grilla espacial del parque para generar un mapa de probabilidad de estrés forestal mes a mes (julio–diciembre 2026).
Presenta todo en un dashboard interactivo (Dash/Plotly) con mapa, gráficos históricos, indicadores y filtros.
