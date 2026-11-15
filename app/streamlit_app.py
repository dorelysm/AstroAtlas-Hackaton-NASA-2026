"""App AstroAtlas: lugares de la Tierra que se parecen a la Luna y a Marte. Ejecutar: streamlit run app/streamlit_app.py

Diseño según la propuesta de interfaz «AstroAtlas — Propuesta de interfaz» (Figma): nombres claros, lugares con nombre,
guía de tres pasos, métricas explicadas y datos que faltan a la vista. Solo cambia cómo se muestra: el modelo no cambia.
Accesibilidad y usabilidad: ver docs/INTERFAZ.md.
"""
import pandas as pd
import pydeck as pdk
import streamlit as st

from analogos.config import DEMO_DIR, DIMENSIONS, RESULTS_DIR
from analogos.features import load_features
from analogos.lugares import etiqueta
from analogos.presentacion import (ASPECTOS, CONFIABILIDAD, CUERPO_DE, CUERPO_ES, GLOSARIO, IMPORTANCIA, LIMITES_CORTOS, aviso_confiabilidad,
                                   describir_terreno, descripcion_sitio, explicar, id_de_la_tabla, id_del_mapa, nivel_parecido, pct,
                                   pesos_desde_importancia, seleccion_nueva)
from analogos.report import ficha
from analogos.similarity import fit_topo_model, rank_cells, site_profiles
from analogos.validate import evaluate, known_for_body, load_known, novel_candidates

st.set_page_config(page_title="AstroAtlas", page_icon=":material/public:", layout="wide")
# Streamlit marca la página como inglés (lang="en") y no lo cambia por configuración: los lectores de pantalla leerían el español
# con voz inglesa. Este script mínimo lo corrige; sin JavaScript la app funciona igual.
st.html("<script>document.documentElement.lang = 'es';</script>", unsafe_allow_javascript=True)


@st.cache_data(show_spinner="Cargando los datos de la Tierra, la Luna y Marte…")
def load():
    return load_features("earth"), load_features("moon"), load_features("mars"), load_known()


@st.cache_data
def nombres(coords: tuple) -> list:
    """(lugar, país) de cada (lat, lon); sin servicios externos (ver analogos/lugares.py)."""
    return [etiqueta(la, lo) for la, lo in coords]


@st.cache_data(show_spinner="Preparando el modelo de relieve…")
def topo_model_for(_earth):
    """PCA blanqueada de la topografía (ver similarity.py); se ajusta una sola vez."""
    return fit_topo_model(_earth)


try:
    earth, moon, mars, known = load()
except FileNotFoundError as e:
    st.error(str(e))
    st.stop()

profiles = {("moon", s): p for s, p in site_profiles(moon).iterrows()}
profiles |= {("mars", s): p for s, p in site_profiles(mars).iterrows()}

# ---- Cabecera ----
st.title("AstroAtlas")
st.caption("Lugares de la Tierra que se parecen a la Luna y a Marte")
for col, (n, titulo, texto) in zip(st.columns(3), [
        (1, "Elige un sitio", "Un lugar de la Luna o de Marte, justo aquí debajo."),
        (2, "Mira el mapa", "Los puntos naranjas son los lugares de la Tierra que más se le parecen."),
        (3, "Lee la ficha", "Te dice en qué se parece, en qué no y qué datos faltan.")]):
    with col.container(border=True, height="stretch"):
        st.markdown(f"**{n} · {titulo}**")
        st.caption(texto)

# El selector de sitio va en la página (no en la barra lateral): en el móvil la barra lateral empieza cerrada.
with st.container(border=True):
    st.markdown("**1 · Elige un sitio de la Luna o de Marte**")
    options = list(profiles)
    default = options.index(("mars", "Jezero")) if ("mars", "Jezero") in options else 0
    body, site = st.selectbox("Sitio de la Luna o de Marte", options, index=default, label_visibility="collapsed", key="sitio",
                              format_func=lambda k: f"{CUERPO_ES[k[0]]} · {k[1]}")
    if descripcion_sitio(site):
        st.caption(descripcion_sitio(site))
    st.caption(":material/tune: ¿Qué te importa más? Ajusta los aspectos y los filtros en la barra lateral "
               "(en el móvil, ábrela con el icono » de arriba a la izquierda).")

with st.sidebar:
    st.markdown("**2 · ¿Qué te importa más?**")
    niveles = {}
    for d in DIMENSIONS:
        nombre, ayuda = ASPECTOS[d]
        niveles[d] = st.segmented_control(f"{nombre}: ¿cuánto importa?", list(IMPORTANCIA), default="Mucho", required=True, key=f"imp_{d}") or "Mucho"
        st.caption(f"{ayuda}.")
    weights = pesos_desde_importancia(niveles)

    st.markdown("**Filtros**")
    only_novel = st.checkbox("Solo lugares nuevos (lejos de los ya conocidos)")
    st.caption("Quita los lugares a menos de 500 km de un análogo conocido.")
    has_viability = "viable" in earth.columns
    hide_populated = st.checkbox("Ocultar lugares con pueblos cerca", value=has_viability, disabled=not has_viability)
    st.caption("Pueblos de 1 000 habitantes o más a menos de 50 km (NASA SEDAC GRUMP). No cambia la nota; la lista es incompleta para "
               "pueblos pequeños (docs/FUENTES.md).")
    if not has_viability:
        st.caption("Sin datos de población: ejecuta `python -m analogos.data.settlements`.")
    has_veg = "vegetated" in earth.columns
    hide_vegetated = st.checkbox("Ocultar lugares con vegetación", value=has_veg, disabled=not has_veg)
    st.caption("Vegetación según NASA MODIS (NDVI máximo de 0.2 o más). El modelo no tiene dimensión de biología: sin este filtro "
               "salen selvas como «parecidas a Marte». No cambia la nota.")
    with st.expander("Opciones avanzadas"):
        top_n = st.slider("Lugares a mostrar", 10, 500, 100)

if sum(weights.values()) == 0:
    st.warning("Pon al menos un aspecto en «Poco» o más para poder comparar.")
    st.stop()

# ---- Cálculo (el modelo no cambia) ----
known_body = known_for_body(known, body)  # solo los análogos que sirven para este cuerpo
ranked = rank_cells(earth, profiles[(body, site)], weights, topo_model_for(earth))
if has_viability:  # solo información: el orden y la nota no cambian
    ranked = ranked.merge(earth[["cell_id", "viable", "dist_settlement_km", "settlement_name"]], on="cell_id", how="left")
if has_veg:
    ranked = ranked.merge(earth[["cell_id", "veg_ndvi_max", "vegetated"]], on="cell_id", how="left")
# los filtros solo afectan a lo que se MUESTRA; la validación (en «Detalles técnicos») usa `ranked` completo
view = ranked[ranked["viable"].fillna(True).astype(bool)] if (has_viability and hide_populated) else ranked
if has_veg and hide_vegetated:
    view = view[~view["vegetated"].fillna(False).astype(bool)]
shown = (novel_candidates(view, known_body, n=top_n) if only_novel else view.head(top_n)).copy()
if shown.empty:
    st.warning("Con estos filtros no queda ningún lugar. Quita alguno en la barra lateral.")
    st.stop()
lab = nombres(tuple(zip(shown["lat"].round(3), shown["lon"].round(3))))
shown["lugar"], shown["pais"] = [x[0] for x in lab], [x[1] for x in lab]
shown["parecido"] = (shown["score"] * 100).round().astype(int)
shown["detalle"] = shown["pais"] + " · parecido " + shown["parecido"].astype(str) + " %"
top5 = shown.head(5)

# ---- Lugar elegido: selectbox, clic en el mapa o fila de la tabla (cada selección nueva cuenta una sola vez) ----
ids = [str(c) for c in shown["cell_id"]]
if st.session_state.get("ficha_celda") not in ids:
    st.session_state["ficha_celda"] = ids[0]
for clave, elegido in (("mapa", id_del_mapa(st.session_state.get("mapa"))),
                       ("tabla_top", id_de_la_tabla(st.session_state.get("tabla_top"), top5))):
    nuevo = seleccion_nueva(st.session_state.get(f"_ult_{clave}"), elegido)
    st.session_state[f"_ult_{clave}"] = elegido
    if nuevo in ids:
        st.session_state["ficha_celda"] = nuevo
pick = st.session_state["ficha_celda"]

st.warning(aviso_confiabilidad(), title="Son pistas, no certezas", icon=":material/warning:")
with st.expander("¿Qué significan estas palabras?"):
    for termino, definicion in GLOSARIO:
        st.markdown(f"- **{termino}:** {definicion}")

# ---- Mapa y confiabilidad ----
col_map, col_rel = st.columns([3, 2])
with col_map:
    st.header(f"Lugares parecidos a {site} ({CUERPO_ES[body]})")
    sel = shown[shown["cell_id"].astype(str) == pick]
    known_map = known.assign(lugar=known["name"], detalle="Análogo que la ciencia ya usa (para comprobar)")
    layers = [
        pdk.Layer("ScatterplotLayer", shown, id="candidatos", get_position="[lon, lat]", get_radius=110000,
                  get_fill_color="[255, 140 - score * 100, 0, 60 + score * 180]", pickable=True),
        pdk.Layer("ScatterplotLayer", known_map, id="conocidos", get_position="[lon, lat]", get_radius=110000, filled=False,
                  stroked=True, get_line_color="[76, 141, 246, 255]", line_width_min_pixels=3, pickable=True),
        pdk.Layer("ScatterplotLayer", sel, id="elegido", get_position="[lon, lat]", get_radius=170000, filled=False, stroked=True,
                  get_line_color="[255, 255, 255, 255]", line_width_min_pixels=3),
    ]
    # sin zoom con la rueda: así la rueda sigue desplazando la página cuando el cursor pasa por el mapa (hay botones + y −)
    st.pydeck_chart(pdk.Deck(layers=layers, initial_view_state=pdk.ViewState(latitude=20, longitude=0, zoom=0.6),
                             views=[pdk.View(type="MapView", controller={"scrollZoom": False})],
                             tooltip={"text": "{lugar}\n{detalle}"}),
                    on_select="rerun", selection_mode="single-object", key="mapa",
                    alt=f"Mapa del mundo con los lugares más parecidos a {site}. Haz clic en un punto naranja para ver su ficha.")
    st.caption(":orange[●] **Punto naranja lleno:** lugares parecidos (candidatos); haz clic en uno para ver su ficha.  \n"
               ":blue[○] **Anillo azul:** lugares que la ciencia ya usa (para comprobar).  \n"
               "○ **Anillo blanco grande:** el lugar elegido.")

with col_rel:
    rel = CONFIABILIDAD[body]
    with st.container(border=True):
        st.markdown(f"**¿Qué tan confiable es para {CUERPO_ES[body]}?**")
        st.badge(rel["nivel"], color="yellow")
        st.metric("de acierto (50 % = adivinar)", f"{rel['pct']} %")
        st.progress(rel["pct"] / 100)
        st.caption(rel["texto"])
        st.caption(f"Entre {rel['lo']} % y {rel['hi']} % con {rel['n']} lugares de comprobación.")
    with st.container(border=True):
        st.markdown("**Los más parecidos**")
        tabla = pd.DataFrame({"#": top5["rank"].astype(int), "Lugar": top5["lugar"], "País": top5["pais"], "Parecido": top5["parecido"]})
        st.dataframe(tabla, hide_index=True, on_select="rerun", selection_mode="single-row", key="tabla_top",
                     alt=f"Los cinco lugares de la Tierra más parecidos a {site}. Elige una fila para ver su ficha.",
                     column_config={"Parecido": st.column_config.ProgressColumn("Parecido", format="%d %%", min_value=0, max_value=100)})
        st.caption("Elige una fila para ver su ficha. El número (#) es el puesto en la lista completa; se saltan los lugares con pueblos "
                   "o vegetación.")


# ---- Ficha del lugar ----
def _nombre_celda(c: str) -> str:
    r = shown[shown["cell_id"].astype(str) == c].iloc[0]
    return f"{r['lugar']} ({r['pais']}) · {r['parecido']} %"


st.selectbox("Ver la ficha de", ids, key="ficha_celda", format_func=_nombre_celda)
fila = shown[shown["cell_id"].astype(str) == st.session_state["ficha_celda"]].iloc[0]
f = ficha(fila, site, body)
cell = earth[earth["cell_id"] == f["cell_id"]].iloc[0]
usados = [d for d in DIMENSIONS if d in f["scores"] and weights[d] > 0]
with st.container(border=True):
    cab, der = st.columns([3, 2], vertical_alignment="center")
    with cab:
        st.header(fila["lugar"])
        lon180 = ((f["lon"] + 180) % 360) - 180
        st.caption(f"{fila['pais']} · {abs(f['lat']):.1f}° {'N' if f['lat'] >= 0 else 'S'}, "
                   f"{abs(lon180):.1f}° {'E' if lon180 >= 0 else 'O'} · {describir_terreno(cell)}")
    with der:
        st.markdown(f"**Se parece a {site} en un {fila['parecido']} %**")
        st.badge(f"Calculado con {len(usados)} de {len(DIMENSIONS)} aspectos", color="orange")
    rejilla = st.grid(len(DIMENSIONS), min_column_width=125, gap="small")  # 4 tarjetas en escritorio, 2 en el móvil
    for d in DIMENSIONS:
        nombre, _ = ASPECTOS[d]
        score = f["scores"].get(d)
        with rejilla.container(border=True, height="stretch"):
            st.markdown(f"**{nombre}**")
            if score is None:
                st.markdown("**Sin dato**")  # texto normal, no métrica grande: en el móvil «Sin dato» se cortaba
                st.badge("Sin comparar", color="gray")
            else:
                st.metric(nombre, pct(score), label_visibility="collapsed")
                st.progress(min(max(score, 0.0), 1.0))
                etiqueta_n, color = nivel_parecido(score)
                st.badge(etiqueta_n, color=color)
            st.caption(explicar(d, score, cell, profiles[(body, site)], body, site))
            if weights[d] == 0:
                st.caption("No cuenta en la nota (importancia: nada).")
    st.markdown(f"**Lo que la Tierra no puede imitar de {CUERPO_DE[body]}**")
    with st.container(horizontal=True):
        for txt in LIMITES_CORTOS[body]:
            st.badge(txt, color="blue")

with st.expander("Detalles técnicos y validación"):
    m = evaluate(ranked, known_body)
    c1, c2 = st.columns(2)
    c1.metric("AUC contra los análogos conocidos", f"{m['auc']:.2f}")
    c2.metric(f"Recall en el {m['top_pct']:.0f} % mejor", f"{m['recall_at_top_pct']:.2f}")
    st.caption("AUC: 0,5 = azar. Es la medida de este sitio contra los análogos del cuerpo. Muy ruidosas: hay pocos análogos por tipo "
               "y faltan dimensiones (docs/VALIDACION.md y docs/INFORME.md).")
    extra = [c for c in ("viable", "dist_settlement_km", "settlement_name", "veg_ndvi_max") if c in shown.columns]
    st.dataframe(shown[["rank", "cell_id", "lugar", "pais", "lat", "lon", "score", *DIMENSIONS, *extra]].round(3), height=250,
                 alt=f"Tabla técnica de los lugares más parecidos a {site}")
    if "ice" in f["similar"]:
        st.caption("«Hielo o agua» en la Tierra es la cobertura de nieve: coincide por ausencia de nieve, no por hielo subsuperficial "
                   "ni sequedad (docs/VALIDACION_ASPECTO.md).")
    with st.expander("Límites de la analogía (lo que la Tierra no reproduce)"):
        for item in f["limits"]:
            st.markdown(f"- {item}")

with st.expander("Candidatos destacados"):
    st.caption("Regla de selección y valoración honesta en docs/FICHAS_CANDIDATOS.md.")
    fichas_csv = RESULTS_DIR / "fichas_candidatos.csv"
    if not fichas_csv.exists():
        fichas_csv = DEMO_DIR / "results" / "fichas_candidatos.csv"
    if fichas_csv.exists():
        fc = pd.read_csv(fichas_csv)
        cols = [c for c in ("body", "cell_id", "lat", "lon", "n_targets", "score_mean", "ndvi_max", "dust_surface_ugm3",
                            "dist_settlement_km", "nearest_known", "nearest_known_km") if c in fc.columns]
        st.dataframe(fc[cols].round(2), hide_index=True, alt="Candidatos destacados con sus datos de contexto")
        st.caption("Las candidatas lunares salen solo por topografía y se consideran pobres.")

with st.expander("Atlas por aspecto: qué se parece dónde"):
    st.caption("Más detalles en docs/ATLAS_ASPECTOS.md.")

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
        top_a = g[g["rank"] > 0]
        if top_a.empty:
            st.caption("No hay ninguna región que recomendar para este aspecto.")
        else:
            st.dataframe(top_a[["rank", "cell_id", "lat", "lon", "score", "n_targets", "nearest_known", "nearest_known_km"]].round(2),
                         hide_index=True, alt="Regiones recomendadas para este aspecto")
            pts = cel[(cel["body"] == body_a) & (cel["aspect"] == asp)]
            st.pydeck_chart(pdk.Deck(layers=[pdk.Layer("ScatterplotLayer", pts, get_position="[lon, lat]", get_radius=110000,
                                                       get_fill_color="[255, 140 - score * 100, 0, 60 + score * 180]", pickable=True)],
                                     initial_view_state=pdk.ViewState(latitude=20, longitude=0, zoom=0.6),
                                     views=[pdk.View(type="MapView", controller={"scrollZoom": False})],
                                     tooltip={"text": "{cell_id}\nnota: {score}"}),
                            alt="Mapa del mundo con las celdas más parecidas según este aspecto")
        st.caption("Cada aspecto se evalúa por separado. Ningún aspecto llega a confianza alta: hay muy pocos análogos para validarlos.")

with st.expander("Recomendaciones por caso de uso"):
    st.caption("Más detalles en docs/CASOS_DE_USO.md.")
    uc_csv = RESULTS_DIR / "usecases.csv"
    if not uc_csv.exists():
        uc_csv = DEMO_DIR / "results" / "usecases.csv"
    if uc_csv.exists():
        uc = pd.read_csv(uc_csv)
        titles = list(dict.fromkeys(uc["title"]))
        chosen = st.selectbox("Caso de uso", titles)
        view_uc = uc[uc["title"] == chosen]
        st.dataframe(view_uc[["rank", "cell_id", "lat", "lon", "score", "n_targets", "nearest_known", "nearest_known_km"]].round(2),
                     hide_index=True, alt="Regiones recomendadas para este caso de uso")
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
        "- **Nombres de lugares y países:** Natural Earth 1:110m (dominio público).\n"
        "- Procedencia completa, licencias y límites: docs/FUENTES.md y docs/LICENCIAS.md. "
        "Parte de la búsqueda de fuentes y del código se hizo con asistentes de IA y se revisó por el equipo."
    )
