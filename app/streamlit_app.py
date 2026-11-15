"""App: mapa de análogos, ranking y ficha. Ejecutar: streamlit run app/streamlit_app.py"""
import pandas as pd
import pydeck as pdk
import streamlit as st

from analogos.config import DIMENSIONS
from analogos.features import load_features
from analogos.report import ficha
from analogos.similarity import fit_topo_model, rank_cells, site_profiles
from analogos.validate import evaluate, known_for_body, load_known, novel_candidates

st.set_page_config(page_title="Análogos terrestres", layout="wide")
st.title("Análogos terrestres para la Luna y Marte")


@st.cache_data
def load():
    return load_features("earth"), load_features("moon"), load_features("mars"), load_known()


try:
    earth, moon, mars, known = load()
except FileNotFoundError as e:
    st.error(str(e))
    st.stop()

profiles = {("moon", s): p for s, p in site_profiles(moon).iterrows()}
profiles |= {("mars", s): p for s, p in site_profiles(mars).iterrows()}

with st.sidebar:
    body, site = st.selectbox("Sitio objetivo", list(profiles), format_func=lambda k: f"{k[0]} · {k[1]}")
    st.caption("Pesos por dimensión")
    weights = {d: st.slider(d, 0.0, 1.0, 1.0, 0.05) for d in DIMENSIONS}
    top_n = st.slider("Celdas a mostrar", 10, 500, 100)
    only_novel = st.checkbox("Solo candidatos lejos de análogos conocidos (>500 km)")
    has_viability = "viable" in earth.columns
    hide_populated = st.checkbox("Ocultar puntos cerca de poblaciones (≥ 1 000 hab. a < 50 km)", value=has_viability,
                                 disabled=not has_viability,
                                 help="Marca de viabilidad (NASA SEDAC GRUMP). No cambia el score ni la validación. "
                                      "Lista incompleta para pueblos pequeños; ver docs/FUENTES.md.")
    if not has_viability:
        st.caption("Sin datos de viabilidad: ejecuta `python -m analogos.data.settlements`.")

if sum(weights.values()) == 0:
    st.warning("Pon al menos un peso mayor que 0.")
    st.stop()

@st.cache_data
def topo_model_for(_earth):
    """PCA blanqueada de la topografía (ver similarity.py); se ajusta una sola vez."""
    return fit_topo_model(_earth)


known_body = known_for_body(known, body)  # solo los análogos que sirven para este cuerpo
ranked = rank_cells(earth, profiles[(body, site)], weights, topo_model_for(earth))
if has_viability:  # solo información: el orden y el score no cambian
    ranked = ranked.merge(earth[["cell_id", "viable", "dist_settlement_km", "settlement_name"]], on="cell_id", how="left")
# el filtro de viabilidad solo afecta a lo que se MUESTRA; la validación (más abajo) usa `ranked` completo
view = ranked[ranked["viable"].fillna(True).astype(bool)] if (has_viability and hide_populated) else ranked
shown = novel_candidates(view, known_body, n=top_n) if only_novel else view.head(top_n)

col_map, col_info = st.columns([3, 2])
with col_map:
    layers = [
        pdk.Layer("ScatterplotLayer", shown, get_position="[lon, lat]", get_radius=150000,
                  get_fill_color="[255, 140 - score * 100, 0, 60 + score * 180]", pickable=True),
        pdk.Layer("ScatterplotLayer", known, get_position="[lon, lat]", get_radius=90000,
                  get_fill_color="[40, 120, 255, 220]"),
    ]
    st.pydeck_chart(pdk.Deck(layers=layers, initial_view_state=pdk.ViewState(latitude=20, longitude=0, zoom=0.6),
                             tooltip={"text": "{cell_id}\nscore: {score}"}))
    st.caption("Naranja: celdas candidatas. Azul: análogos conocidos (validación).")

with col_info:
    m = evaluate(ranked, known_body)
    c1, c2 = st.columns(2)
    c1.metric("AUC vs conocidos", f"{m['auc']:.2f}")
    c2.metric(f"Recall@{m['top_pct']:.0f}%", f"{m['recall_at_top_pct']:.2f}")
    st.caption("Muy ruidosas: hay pocos análogos por tipo y faltan dimensiones (ver docs/VALIDACION.md).")
    extra = [c for c in ("viable", "dist_settlement_km", "settlement_name") if c in shown.columns]
    st.dataframe(shown[["rank", "cell_id", "lat", "lon", "score", *DIMENSIONS, *extra]].round(3), height=250)
    pick = st.selectbox("Ficha de la celda", shown["cell_id"])
    st.json(ficha(shown[shown["cell_id"] == pick].iloc[0], site, body))
