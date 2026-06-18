import json
import os
import numpy as np
import pandas as pd
from dash import Dash, dcc, html, Input, Output
import dash_leaflet as dl
import plotly.graph_objects as go
from plotly.subplots import make_subplots

app = Dash(__name__)

MESES = {
    "2026-07": "Julio 2026",
    "2026-08": "Agosto 2026",
    "2026-09": "Septiembre 2026",
    "2026-10": "Octubre 2026",
    "2026-11": "Noviembre 2026",
    "2026-12": "Diciembre 2026",
}

COLORES_RIESGO = {
    "alto":      "#d73027",
    "moderado":  "#fee08b",
    "bajo":      "#1a9850",
    "sin_datos": "#cccccc",
}

# ── Datos ─────────────────────────────────────────────────────────────────────
df_ndvi   = pd.read_csv("data/ndvi_mensual_chagres_2000.csv",   parse_dates=["fecha"])
df_lst    = pd.read_csv("data/lst_mensual_chagres_2000.csv",    parse_dates=["fecha"])
df_precip = pd.read_csv("data/precip_mensual_chagres_2000.csv", parse_dates=["fecha"])
df_oni    = pd.read_csv("data/oni_mensual_2000.csv",            parse_dates=["fecha"])

for df in [df_ndvi, df_lst, df_precip, df_oni]:
    df["fecha"] = df["fecha"].dt.to_period("M").dt.to_timestamp()

pred_records = []
for mes_key in MESES:
    path = f"predicciones_map/pred_{mes_key.replace('-','_')}.geojson"
    with open(path, encoding="utf-8") as f:
        gj = json.load(f)
    ndvi_vals = [
        feat["properties"]["ndvi_pred"]
        for feat in gj["features"]
        if feat["properties"].get("ndvi_pred") is not None
    ]
    if ndvi_vals:
        pred_records.append({
            "fecha":     pd.Timestamp(mes_key + "-01"),
            "ndvi_pred": np.mean(ndvi_vals),
        })

df_pred = pd.DataFrame(pred_records)
AÑO_MIN = int(df_ndvi["fecha"].dt.year.min())
AÑO_MAX = 2026


def cargar_geojson(mes_key):
    path = f"predicciones_map/pred_{mes_key.replace('-', '_')}.geojson"
    with open(path, encoding="utf-8") as f:
        return json.load(f)


# ── Layout ────────────────────────────────────────────────────────────────────
CARD = {
    "background": "#fff",
    "borderRadius": "12px",
    "boxShadow": "0 2px 10px rgba(0,0,0,0.08)",
    "padding": "20px",
}

app.layout = html.Div([

    # ── Header ────────────────────────────────────────────────────────────────
    html.Div([
        html.H2("🌿 Monitoreo Forestal — Parque Nacional Chagres",
                style={"margin": 0, "color": "#2d6a4f", "fontSize": "1.4rem"}),
        html.P("Sistema de monitoreo geoespacial · Predicción de zonas de estrés forestal ante eventos de sequía",
               style={"margin": "5px 0 0 0", "color": "#666", "fontSize": "0.85rem"}),
    ], style={
        "padding": "18px 32px",
        "background": "#f0f7f4",
        "borderBottom": "2px solid #2d6a4f",
    }),

    # ── Cuerpo principal ──────────────────────────────────────────────────────
    html.Div([

        # ══ FILA 1: Mapa (izq) + NDVI (der) ══════════════════════════════════
        html.Div([

            # Mapa
            html.Div([
                html.Div([
                    html.Label("Mes predicho:", style={
                        "fontWeight": "600", "fontSize": "0.85rem",
                        "color": "#444", "marginBottom": "8px", "display": "block"
                    }),
                    dcc.Dropdown(
                        id="selector-mes",
                        options=[{"label": v, "value": k} for k, v in MESES.items()],
                        value="2026-07",
                        clearable=False,
                        style={"marginBottom": "14px", "fontSize": "0.88rem"}
                    ),
                    # Leyenda
                    html.Div([
                        html.Div([
                            html.Span(style={
                                "display": "inline-block", "width": "14px", "height": "14px",
                                "backgroundColor": color, "borderRadius": "3px",
                                "marginRight": "7px", "verticalAlign": "middle"
                            }),
                            html.Span(label, style={"fontSize": "0.8rem", "verticalAlign": "middle"})
                        ], style={"marginBottom": "6px"})
                        for label, color in [
                            ("Alto  (≥ 70%)",     "#d73027"),
                            ("Moderado (45–70%)", "#fee08b"),
                            ("Bajo  (< 45%)",     "#1a9850"),
                            ("Sin datos",         "#cccccc"),
                        ]
                    ], style={"marginBottom": "14px"}),
                    html.Div(id="panel-info"),
                ], style={"marginBottom": "12px"}),

                # Mapa propiamente
                dl.Map(
                    id="mapa-principal",
                    center=[9.2, -79.5], zoom=9,
                    children=[
                        dl.TileLayer(
                            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
                            attribution="© OpenStreetMap"
                        ),
                        dl.LayerGroup(id="capa-prediccion"),
                    ],
                    style={"height": "340px", "width": "100%", "borderRadius": "8px"}
                ),
            ], style={**CARD, "flex": "1"}),

            html.Div(style={"width": "24px"}),  # separador

            # NDVI
            html.Div([
                dcc.Graph(id="grafica-ndvi", config={"displayModeBar": False},
                          style={"height": "100%"}),
            ], style={**CARD, "flex": "1.4", "minHeight": "480px"}),

        ], style={"display": "flex", "alignItems": "stretch", "marginBottom": "24px"}),

        # ══ FILA 2: LST (izq) + Precipitación (centro) + ONI (der) ══════════
        html.Div([

            html.Div([
                dcc.Graph(id="grafica-lst", config={"displayModeBar": False},
                          style={"height": "280px"}),
            ], style={**CARD, "flex": "1"}),

            html.Div(style={"width": "24px"}),

            html.Div([
                dcc.Graph(id="grafica-precip", config={"displayModeBar": False},
                          style={"height": "280px"}),
            ], style={**CARD, "flex": "1"}),

            html.Div(style={"width": "24px"}),

            html.Div([
                dcc.Graph(id="grafica-oni", config={"displayModeBar": False},
                          style={"height": "280px"}),
            ], style={**CARD, "flex": "1"}),

        ], style={"display": "flex", "alignItems": "stretch", "marginBottom": "24px"}),

        # ══ Slider de años (al fondo, afecta todas las gráficas) ═════════════
        html.Div([
            html.Label("📅 Filtrar rango de años:",
                       style={"fontWeight": "600", "fontSize": "0.88rem",
                              "color": "#444", "marginBottom": "10px", "display": "block"}),
            dcc.RangeSlider(
                id="filtro-años",
                min=AÑO_MIN, max=AÑO_MAX,
                value=[2015, AÑO_MAX],
                marks={y: str(y) for y in range(AÑO_MIN, AÑO_MAX + 1, 3)},
                step=1,
                tooltip={"placement": "bottom", "always_visible": False},
            ),
        ], style={**CARD, "marginBottom": "24px"}),

    ], style={
        "padding": "28px 32px",
        "background": "#f4f6f8",
        "minHeight": "calc(100vh - 70px)",
    }),

], style={"fontFamily": "Segoe UI, sans-serif", "margin": 0})


# ── Callback: mapa ────────────────────────────────────────────────────────────
@app.callback(
    Output("capa-prediccion", "children"),
    Output("panel-info", "children"),
    Input("selector-mes", "value"),
)
def actualizar_mapa(mes_key):
    geojson = cargar_geojson(mes_key)

    capas = []
    for nivel, color in COLORES_RIESGO.items():
        feats = [f for f in geojson["features"]
                 if f["properties"].get("riesgo", "sin_datos") == nivel]
        if not feats:
            continue
        capas.append(dl.GeoJSON(
            data={"type": "FeatureCollection", "features": feats},
            id=f"capa-{nivel}",
            style={"color": "#333", "weight": 0.8,
                   "fillColor": color, "fillOpacity": 0.75},
            hoverStyle={"weight": 2, "color": "#111", "fillOpacity": 0.95},
        ))

    features = geojson["features"]
    total = len(features)
    conteo = {k: 0 for k in COLORES_RIESGO}
    for f in features:
        conteo[f["properties"].get("riesgo", "sin_datos")] += 1

    info = html.Div([
        html.P(f"Total zonas: {total}",
               style={"margin": "3px 0", "fontSize": "0.82rem", "color": "#555"}),
        html.P(f"🔴 Alto: {conteo['alto']}  ({conteo['alto']/total*100:.0f}%)",
               style={"margin": "3px 0", "fontSize": "0.82rem"}),
        html.P(f"🟡 Moderado: {conteo['moderado']}  ({conteo['moderado']/total*100:.0f}%)",
               style={"margin": "3px 0", "fontSize": "0.82rem"}),
        html.P(f"🟢 Bajo: {conteo['bajo']}  ({conteo['bajo']/total*100:.0f}%)",
               style={"margin": "3px 0", "fontSize": "0.82rem"}),
    ])

    return capas, info


# ── Callback: gráficas ────────────────────────────────────────────────────────
@app.callback(
    Output("grafica-ndvi",   "figure"),
    Output("grafica-lst",    "figure"),
    Output("grafica-precip", "figure"),
    Output("grafica-oni",    "figure"),
    Input("filtro-años", "value"),
)
def actualizar_graficas(rango):
    año_ini, año_fin = rango
    f0 = pd.Timestamp(f"{año_ini}-01-01")
    f1 = pd.Timestamp(f"{año_fin}-12-31")

    def fil(df):
        return df[(df["fecha"] >= f0) & (df["fecha"] <= f1)]

    ndvi_f   = fil(df_ndvi)
    lst_f    = fil(df_lst)
    precip_f = fil(df_precip)
    oni_f    = fil(df_oni)
    pred_f   = fil(df_pred)

    BASE = dict(
        paper_bgcolor="#fff",
        plot_bgcolor="#fafafa",
        margin=dict(l=52, r=20, t=40, b=36),
        font=dict(family="Segoe UI", size=11, color="#333"),
        hovermode="x unified",
        legend=dict(orientation="h", y=1.12, x=0, font=dict(size=10)),
    )

    def ejes(fig):
        fig.update_xaxes(showgrid=True, gridcolor="#eee", tickformat="%b %Y")
        fig.update_yaxes(showgrid=True, gridcolor="#eee")
        return fig

    # ── NDVI ─────────────────────────────────────────────────────────────────
    fig_ndvi = go.Figure(layout={**BASE, "title": "NDVI histórico y predicción"})
    fig_ndvi.add_trace(go.Scatter(
        x=ndvi_f["fecha"], y=ndvi_f["ndvi"],
        name="Histórico", line=dict(color="#2d6a4f", width=2), mode="lines",
    ))
    if not pred_f.empty:
        ultimo = ndvi_f.iloc[-1] if not ndvi_f.empty else None
        xp = ([ultimo["fecha"]] + list(pred_f["fecha"])) if ultimo is not None else list(pred_f["fecha"])
        yp = ([ultimo["ndvi"]]  + list(pred_f["ndvi_pred"])) if ultimo is not None else list(pred_f["ndvi_pred"])
        fig_ndvi.add_trace(go.Scatter(
            x=xp, y=yp, name="Predicción",
            line=dict(color="#e63946", width=2, dash="dot"),
            mode="lines+markers", marker=dict(size=6),
        ))
        fig_ndvi.add_vrect(
            x0=pred_f["fecha"].min(), x1=pred_f["fecha"].max(),
            fillcolor="rgba(230,57,70,0.07)", line_width=0,
        )
    ejes(fig_ndvi)

    # ── LST ───────────────────────────────────────────────────────────────────
    fig_lst = go.Figure(layout={**BASE, "title": "Temperatura superficial LST (°C)"})
    fig_lst.add_trace(go.Scatter(
        x=lst_f["fecha"], y=lst_f["lst_celsius"],
        name="LST (°C)", line=dict(color="#e07b39", width=1.8),
        fill="tozeroy", fillcolor="rgba(224,123,57,0.1)", mode="lines",
    ))
    ejes(fig_lst)

    # ── Precipitación ─────────────────────────────────────────────────────────
    fig_precip = go.Figure(layout={**BASE, "title": "Precipitación mensual (mm)"})
    fig_precip.add_trace(go.Bar(
        x=precip_f["fecha"], y=precip_f["precip_mm"],
        name="Precip. (mm)", marker_color="#457b9d", opacity=0.8,
    ))
    ejes(fig_precip)

    # ── ONI ───────────────────────────────────────────────────────────────────
    fig_oni = go.Figure(layout={**BASE, "title": "Índice ONI — El Niño / La Niña"})
    fig_oni.add_trace(go.Bar(
        x=oni_f["fecha"], y=oni_f["oni"],
        name="ONI",
        marker_color=[
            "#d73027" if v >= 0.5 else ("#4575b4" if v <= -0.5 else "#aaaaaa")
            for v in oni_f["oni"]
        ],
        opacity=0.85,
    ))
    for umbral, color in [(0.5, "rgba(215,48,39,0.5)"), (-0.5, "rgba(69,117,180,0.5)")]:
        fig_oni.add_hline(y=umbral, line_dash="dash", line_color=color, line_width=1)
    ejes(fig_oni)

    return fig_ndvi, fig_lst, fig_precip, fig_oni


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8050)), debug=False)