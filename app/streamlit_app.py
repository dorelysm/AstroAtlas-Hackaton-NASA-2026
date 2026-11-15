"""App: mapa de análogos, ranking y ficha. Ejecutar: streamlit run app/streamlit_app.py"""
import pandas as pd
import pydeck as pdk
import streamlit as st

from analogos.config import DEMO_DIR, DIMENSIONS, RESULTS_DIR
from analogos.features import load_features
from analogos.report import ficha
from analogos.similarity import fit_topo_model, rank_cells, site_profiles
from analogos.validate import evaluate, known_for_body, load_known, novel_candidates

st.set_page_config(page_title="Análogos terrestres", layout="wide")
st.title("Análogos terrestres para la Luna y Marte")
st.markdown(
    "Elige un sitio de la Luna o de Marte en la barra lateral: el mapa muestra las celdas de la Tierra que más se le parecen "
    "en **topografía, térmica, hielo y geología** (NASA y otras agencias, datos abiertos)."
)
st.info(
    "**Son hipótesis, no hallazgos.** La validación contra análogos conocidos sale cerca del azar y varias dimensiones "
    "tienen datos limitados o vacíos (p. ej. la térmica de Marte). Más en el informe del proyecto (`docs/INFORME.md`).",
    icon="⚠️",
)


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
    options = list(profiles)
    default = options.index(("mars", "Jezero")) if ("mars", "Jezero") in options else 0
    body, site = st.selectbox("Sitio objetivo", options, index=default, format_func=lambda k: f"{k[0]} · {k[1]}")
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
    has_veg = "vegetated" in earth.columns
    hide_vegetated = st.checkbox("Ocultar puntos con vegetación (NDVI máx. ≥ 0.2)", value=has_veg, disabled=not has_veg,
                                 help="Marca de vegetación (NASA MODIS MOD13C2, 2019). El modelo no tiene dimensión de biología: "
                                      "sin este filtro salen selvas como 'parecidas a Marte'. No cambia el score ni la validación.")

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
if has_veg:
    ranked = ranked.merge(earth[["cell_id", "veg_ndvi_max", "vegetated"]], on="cell_id", how="left")
# el filtro de viabilidad solo afecta a lo que se MUESTRA; la validación (más abajo) usa `ranked` completo
view = ranked[ranked["viable"].fillna(True).astype(bool)] if (has_viability and hide_populated) else ranked
if has_veg and hide_vegetated:
    view = view[~view["vegetated"].fillna(False).astype(bool)]
shown = novel_candidates(view, known_body, n=top_n) if only_novel else view.head(top_n)

col_map, col_info = st.columns([3, 2])
with col_map:
    layers = [
        pdk.Layer("ScatterplotLayer", shown, get_position="[lon, lat]", get_radius=110000,
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
    extra = [c for c in ("viable", "dist_settlement_km", "settlement_name", "veg_ndvi_max") if c in shown.columns]
    st.dataframe(shown[["rank", "cell_id", "lat", "lon", "score", *DIMENSIONS, *extra]].round(3), height=250)
    pick = st.selectbox("Ficha de la celda", shown["cell_id"])
    f = ficha(shown[shown["cell_id"] == pick].iloc[0], site, body)
    st.subheader(f"Ficha: {f['cell_id']}  ({f['lat']:.1f}°, {f['lon']:.1f}°)")
    st.caption(f"Parecida a **{f['site']}** ({f['body']}) · puntaje global {f['score']:.2f} · puesto {f['rank']}")
    for dim in DIMENSIONS:
        if dim in f["scores"]:
            st.progress(min(max(f["scores"][dim], 0.0), 1.0), text=f"{dim}: {f['scores'][dim]:.2f}")
        else:
            st.caption(f"{dim}: sin dato")
    if f["similar"]:
        st.success("Se parece en: " + ", ".join(f["similar"]))
    if "ice" in f["similar"]:
        st.caption("⚠️ Ojo con «ice»: en la Tierra es la cobertura de nieve. Coincide por **ausencia de nieve**, no por hielo "
                   "subsuperficial ni sequedad (ver docs/VALIDACION_ASPECTO.md).")
    if f["different"]:
        st.warning("Es distinta en: " + ", ".join(f["different"]))
    if f["no_data"]:
        st.caption("No se pudo comparar: " + ", ".join(f["no_data"]))
    with st.expander("Límites de la analogía (lo que la Tierra no reproduce)"):
        for item in f["limits"]:
            st.markdown(f"- {item}")

with st.expander("Candidatos destacados (ver docs/FICHAS_CANDIDATOS.md)"):
    fichas_csv = RESULTS_DIR / "fichas_candidatos.csv"
    if not fichas_csv.exists():
        fichas_csv = DEMO_DIR / "results" / "fichas_candidatos.csv"
    if fichas_csv.exists():
        fc = pd.read_csv(fichas_csv)
        cols = [c for c in ("body", "cell_id", "lat", "lon", "n_targets", "score_mean", "ndvi_max", "dust_surface_ugm3",
                            "dist_settlement_km", "nearest_known", "nearest_known_km") if c in fc.columns]
        st.dataframe(fc[cols].round(2), hide_index=True)
        st.caption("Regla de selección y valoración honesta (las candidatas lunares salen solo por topografía y se consideran pobres) "
                   "en `docs/FICHAS_CANDIDATOS.md`.")

with st.expander("Atlas por aspecto: qué se parece dónde (ver docs/ATLAS_ASPECTOS.md)"):
    def _res(name):
        p = RESULTS_DIR / name
        return p if p.exists() else DEMO_DIR / "results" / name

    if _res("atlas_regiones.csv").exists() and _res("atlas_celdas.csv").exists():
        reg, cel = pd.read_csv(_res("atlas_regiones.csv")), pd.read_csv(_res("atlas_celdas.csv"))
        ca, cb = st.columns(2)
        body_a = ca.selectbox("Cuerpo", ["mars", "moon"], format_func=lambda b: {"mars": "Marte", "moon": "Luna"}[b], key="atlas_body")
        asp = cb.selectbox("Aspecto", ["geo", "topo", "thermal", "ice"], key="atlas_aspect",
                           format_func=lambda a: {"geo": "Geología", "topo": "Topografía", "thermal": "Térmica", "ice": "Hielo / agua"}[a])
        g = reg[(reg["body"] == body_a) & (reg["aspect"] == asp)]
        conf = g["confidence"].iloc[0]
        msg = f"**Confianza: {conf}.** {g['why'].iloc[0]}"
        (st.warning if conf in ("baja", "muy baja", "sin datos") else st.info)(msg)
        top = g[g["rank"] > 0]
        if top.empty:
            st.caption("No hay ninguna región que recomendar para este aspecto.")
        else:
            st.dataframe(top[["rank", "cell_id", "lat", "lon", "score", "n_targets", "nearest_known", "nearest_known_km"]].round(2),
                         hide_index=True)
            pts = cel[(cel["body"] == body_a) & (cel["aspect"] == asp)]
            st.pydeck_chart(pdk.Deck(layers=[pdk.Layer("ScatterplotLayer", pts, get_position="[lon, lat]", get_radius=110000,
                                                       get_fill_color="[255, 140 - score * 100, 0, 60 + score * 180]", pickable=True)],
                                     initial_view_state=pdk.ViewState(latitude=20, longitude=0, zoom=0.6),
                                     tooltip={"text": "{cell_id}\nscore: {score}"}))
        st.caption("Cada aspecto se evalúa por separado. Ningún aspecto llega a confianza alta: hay muy pocos análogos para validarlos.")

with st.expander("Recomendaciones por caso de uso (ver docs/CASOS_DE_USO.md)"):
    uc_csv = RESULTS_DIR / "usecases.csv"
    if not uc_csv.exists():
        uc_csv = DEMO_DIR / "results" / "usecases.csv"
    if uc_csv.exists():
        uc = pd.read_csv(uc_csv)
        titles = list(dict.fromkeys(uc["title"]))
        chosen = st.selectbox("Caso de uso", titles)
        view_uc = uc[uc["title"] == chosen]
        st.dataframe(view_uc[["rank", "cell_id", "lat", "lon", "score", "n_targets", "nearest_known", "nearest_known_km"]].round(2),
                     hide_index=True)
        st.caption("Solo el caso de terreno basáltico de Marte da una recomendación defendible; en frío y hielo el puntaje alto o bajo "
                   "refleja los límites de la Tierra como análogo (la «nieve» no es hielo subsuperficial). Son hipótesis. "
                   "El caso «Hielo en el suelo y permafrost» usa el mapa de permafrost de Obu et al. (2018) y objetivos de Marte con hielo "
                   "expuesto publicado; son regiones de permafrost real (Groenlandia libre de hielo y Ártico canadiense), no una predicción.")

with st.expander("Créditos y fuentes de datos"):
    st.markdown(
        "- **Luna:** LRO LOLA, LRO Diviner, Lunar Prospector GRS, LROC (NASA/ASU), pits de LROC QuickMap (Losarcos y Dombard 2026, CC BY 4.0).\n"
        "- **Marte:** MGS MOLA, Mars Odyssey GRS, Mars Global Cave Candidate Catalog (USGS, Cushing).\n"
        "- **Tierra:** Copernicus DEM GLO-90 (ESA; contiene datos modificados de Copernicus), NASA MODIS (LST, nieve, NDVI), "
        "NASA GLDAS y MERRA-2, NASA SEDAC GRUMP (CIESIN), GLiM (Hartmann y Moosdorf 2012, CC BY 3.0), "
        "capa de análogos del USGS (Hunter 2020), Pyroduct (Romio y Lobosco 2024, CC BY 4.0).\n"
        "- Procedencia completa, licencias y límites: `docs/FUENTES.md` y `docs/LICENCIAS.md`. "
        "Parte de la búsqueda de fuentes y del código se hizo con asistentes de IA y se revisó por el equipo."
    )
