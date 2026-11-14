"""App: mapa de análogos, ranking y ficha. Ejecutar: streamlit run app/streamlit_app.py"""
import pandas as pd
import pydeck as pdk
import streamlit as st

from analogos.config import DIMENSIONS
from analogos.features import load_features
from analogos.report import ficha
from analogos.similarity import rank_cells, site_profiles
from analogos.validate import evaluate, load_known, novel_candidates

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

if sum(weights.values()) == 0:
    st.warning("Pon al menos un peso mayor que 0.")
    st.stop()

ranked = rank_cells(earth, profiles[(body, site)], weights)
shown = novel_candidates(ranked, known, n=top_n) if only_novel else ranked.head(top_n)

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
    m = evaluate(ranked, known)
    c1, c2 = st.columns(2)
    c1.metric("AUC vs conocidos", f"{m['auc']:.2f}")
    c2.metric(f"Recall@{m['top_pct']:.0f}%", f"{m['recall_at_top_pct']:.2f}")
    st.caption("Con datos sintéticos estas métricas no significan nada.")
    st.dataframe(shown[["rank", "cell_id", "lat", "lon", "score", *DIMENSIONS]].round(3), height=250)
    pick = st.selectbox("Ficha de la celda", shown["cell_id"])
    st.json(ficha(shown[shown["cell_id"] == pick].iloc[0], site, body))
