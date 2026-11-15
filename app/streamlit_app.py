"""AstroAtlas app: places on Earth that resemble the Moon and Mars. Run: streamlit run app/streamlit_app.py

Available in Spanish and English (language selector at the top of the sidebar; also `?lang=en` in the address). Design after the
interface proposal "AstroAtlas — Interface proposal" (Figma). It only changes how things are shown: the model does not change.
Accessibility, usability and languages: see docs/app/interface.md.
"""
import pandas as pd
import pydeck as pdk
import streamlit as st

from astroatlas.config import DEMO_DIR, DIMENSIONS, RESULTS_DIR
from astroatlas.features import load_features
from astroatlas.i18n import LANGUAGES, t
from astroatlas.imagery import WINDOW_KM, credit, body_view, view_available, earth_view
from astroatlas.places import label
from astroatlas.presentation import (RELIABILITY, IMPORTANCE, aspect_info, reliability_notice, reliability, coordinates, body_name,
                                   body_name_of, describe_terrain, site_description, importance_label, explain, glossary,
                                   table_selection_id, map_selection_id, short_limits, match_level, pct, weights_from_importance,
                                   new_selection, translate_case, translate_confidence, translate_why)
from astroatlas.report import ficha
from astroatlas.similarity import fit_topo_model, rank_cells, site_profiles
from astroatlas.validate import evaluate, known_for_body, load_known, novel_candidates

st.set_page_config(page_title="AstroAtlas", page_icon=":material/public:", layout="wide")

# Language: first control of the sidebar. It is synchronised with the address (?lang=en) so the English version can be shared.
_inicial = st.query_params.get("lang")  # ?lang=en and ?lang=es (the control uses ?lang=English / ?lang=Español, which are valid too)
if "lang" not in st.session_state and _inicial in LANGUAGES:
    st.session_state["lang"] = _inicial
with st.sidebar:
    lang = st.segmented_control(t("en", "idioma_label"), list(LANGUAGES), format_func=LANGUAGES.get, default="en", required=True,
                                key="lang") or "en"
    st.query_params["lang"] = lang
    st.caption(t(lang, "idioma_ayuda"))

# Streamlit marks the page as English (lang="en") and does not change it through configuration: screen readers would read the Spanish
# with an English voice (or the other way round). This minimal script sets the chosen language; without JavaScript the app works the same.
st.html(f"<script>document.documentElement.lang = '{lang}';</script>", unsafe_allow_javascript=True)


def pie():
    """Footer with the authorship, in the chosen language (also when the page stops for lack of data or filters)."""
    st.divider()
    st.caption(t(lang, "pie"))


class NoImage(Exception):
    """The NASA imagery service did not respond (exceptions are not cached, so it is retried)."""


@st.cache_data(ttl="7d", max_entries=300, show_spinner=False)
def body_image(cuerpo_: str, lat: float, lon: float) -> bytes:
    datos = body_view(cuerpo_, lat, lon)
    if datos is None:
        raise NoImage
    return datos


@st.cache_data(ttl="7d", max_entries=300, show_spinner=False)
def earth_image(lat: float, lon: float, capa: str) -> bytes:
    datos = earth_view(lat, lon, layer=capa)
    if datos is None:
        raise NoImage
    return datos


@st.cache_data(show_spinner=t("en", "cargando"))
def load():
    return load_features("earth"), load_features("moon"), load_features("mars"), load_known()


@st.cache_data
def nombres(coords: tuple, idioma: str) -> list:
    """(place, country) of each (lat, lon) in the chosen language; no external services (see astroatlas/places.py)."""
    return [label(la, lo, idioma) for la, lo in coords]


@st.cache_data(show_spinner=t("en", "cargando_modelo"))
def topo_model_for(_earth):
    """Whitened PCA of the topography (see similarity.py); fitted only once."""
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
st.caption(t(lang, "subtitulo"))
for col, n in zip(st.columns(3), (1, 2, 3)):
    with col.container(border=True, height="stretch"):
        st.markdown(f"**{n} · {t(lang, f'paso{n}')}**")
        st.caption(t(lang, f"paso{n}_texto"))

# The site selector goes in the page (not in the sidebar): on mobile the sidebar starts closed.
with st.container(border=True):
    st.markdown(f"**{t(lang, 'sitio_titulo')}**")
    options = list(profiles)
    default = options.index(("mars", "Jezero")) if ("mars", "Jezero") in options else 0
    body, site = st.selectbox(t(lang, "sitio_label"), options, index=default, label_visibility="collapsed", key="sitio",
                              format_func=lambda k: f"{body_name(k[0], lang)} · {k[1]}")
    if site_description(site, lang):
        st.caption(site_description(site, lang))
    st.caption(t(lang, "ajusta_hint"))

with st.sidebar:
    st.markdown(f"**{t(lang, 'importa_titulo')}**")
    niveles = {}
    for d in DIMENSIONS:
        nombre, ayuda = aspect_info(d, lang)
        niveles[d] = st.segmented_control(t(lang, "imp_label", nombre=nombre), list(IMPORTANCE), default="high", required=True,
                                          key=f"imp_{d}", format_func=lambda k: importance_label(k, lang)) or "high"
        st.caption(f"{ayuda}.")
    weights = weights_from_importance(niveles)

    st.markdown(f"**{t(lang, 'filtros')}**")
    only_novel = st.checkbox(t(lang, "f_nuevos"))
    st.caption(t(lang, "f_nuevos_ayuda"))
    has_viability = "viable" in earth.columns
    hide_populated = st.checkbox(t(lang, "f_pueblos"), value=has_viability, disabled=not has_viability)
    st.caption(t(lang, "f_pueblos_ayuda"))
    if not has_viability:
        st.caption(t(lang, "sin_poblacion"))
    has_veg = "vegetated" in earth.columns
    hide_vegetated = st.checkbox(t(lang, "f_veg"), value=has_veg, disabled=not has_veg)
    st.caption(t(lang, "f_veg_ayuda"))
    with st.expander(t(lang, "avanzadas")):
        top_n = st.slider(t(lang, "mostrar"), 10, 500, 100)

if sum(weights.values()) == 0:
    st.warning(t(lang, "sin_pesos"))
    pie()
    st.stop()

# ---- Computation (the model does not change) ----
known_body = known_for_body(known, body)  # only the analogs that serve this body
ranked = rank_cells(earth, profiles[(body, site)], weights, topo_model_for(earth))
if has_viability:  # information only: the order and the score do not change
    ranked = ranked.merge(earth[["cell_id", "viable", "dist_settlement_km", "settlement_name"]], on="cell_id", how="left")
if has_veg:
    ranked = ranked.merge(earth[["cell_id", "veg_ndvi_max", "vegetated"]], on="cell_id", how="left")
# the filters only affect what is SHOWN; the validation (in "Technical details") uses the full `ranked`
view = ranked[ranked["viable"].fillna(True).astype(bool)] if (has_viability and hide_populated) else ranked
if has_veg and hide_vegetated:
    view = view[~view["vegetated"].fillna(False).astype(bool)]
shown = (novel_candidates(view, known_body, n=top_n) if only_novel else view.head(top_n)).copy()
if shown.empty:
    st.warning(t(lang, "sin_lugares"))
    pie()
    st.stop()
lab = nombres(tuple(zip(shown["lat"].round(3), shown["lon"].round(3))), lang)
shown["lugar"], shown["pais"] = [x[0] for x in lab], [x[1] for x in lab]
shown["parecido"] = (shown["score"] * 100).round().astype(int)
shown["detalle"] = [t(lang, "tooltip_detalle", pais=p, n=n) for p, n in zip(shown["pais"], shown["parecido"])]
top5 = shown.head(5)

# ---- Chosen place: selectbox, map click or table row (each new selection counts only once) ----
ids = [str(c) for c in shown["cell_id"]]
if st.session_state.get("profile_cell") not in ids:
    st.session_state["profile_cell"] = ids[0]
for clave, elegido in (("mapa", map_selection_id(st.session_state.get("mapa"))),
                       ("tabla_top", table_selection_id(st.session_state.get("tabla_top"), top5))):
    nuevo = new_selection(st.session_state.get(f"_ult_{clave}"), elegido)
    st.session_state[f"_ult_{clave}"] = elegido
    if nuevo in ids:
        st.session_state["profile_cell"] = nuevo
pick = st.session_state["profile_cell"]

st.warning(reliability_notice(lang), title=t(lang, "aviso_titulo"), icon=":material/warning:")
with st.expander(t(lang, "glosario_titulo")):
    for termino, definicion in glossary(lang):
        st.markdown(f"- **{termino}:** {definicion}")

# ---- Mapa y reliability ----
col_map, col_rel = st.columns([3, 2])
with col_map:
    st.header(t(lang, "mapa_titulo", sitio=site, cuerpo=body_name(body, lang)))
    sel = shown[shown["cell_id"].astype(str) == pick]
    known_map = known.assign(lugar=known["name"], detalle=t(lang, "tooltip_conocido"))
    layers = [
        pdk.Layer("ScatterplotLayer", shown, id="candidatos", get_position="[lon, lat]", get_radius=110000,
                  get_fill_color="[255, 140 - score * 100, 0, 60 + score * 180]", pickable=True),
        pdk.Layer("ScatterplotLayer", known_map, id="conocidos", get_position="[lon, lat]", get_radius=110000, filled=False,
                  stroked=True, get_line_color="[76, 141, 246, 255]", line_width_min_pixels=3, pickable=True),
        pdk.Layer("ScatterplotLayer", sel, id="elegido", get_position="[lon, lat]", get_radius=170000, filled=False, stroked=True,
                  get_line_color="[255, 255, 255, 255]", line_width_min_pixels=3),
    ]
    # no wheel zoom: so the wheel keeps scrolling the page when the cursor passes over the map (there are + and − buttons)
    st.pydeck_chart(pdk.Deck(layers=layers, initial_view_state=pdk.ViewState(latitude=20, longitude=0, zoom=0.6),
                             views=[pdk.View(type="MapView", controller={"scrollZoom": False})],
                             tooltip={"text": "{lugar}\n{detalle}"}),
                    on_select="rerun", selection_mode="single-object", key="mapa", alt=t(lang, "mapa_alt", sitio=site))
    st.caption("  \n".join(t(lang, "leyenda_lista")))

with col_rel:
    rel = reliability(body, lang)
    with st.container(border=True):
        st.markdown(f"**{t(lang, 'conf_titulo', cuerpo=body_name(body, lang))}**")
        st.badge(rel["nivel"], color="yellow")
        st.metric(t(lang, "conf_metrica"), pct(rel["pct"] / 100, lang))
        st.progress(rel["pct"] / 100)
        st.caption(rel["texto"])
        st.caption(t(lang, "conf_rango", lo=rel["lo"], hi=rel["hi"], n=rel["n"]))
    with st.container(border=True):
        st.markdown(f"**{t(lang, 'top_titulo')}**")
        c_lugar, c_pais, c_par = t(lang, "col_lugar"), t(lang, "col_pais"), t(lang, "col_parecido")
        tabla = pd.DataFrame({"#": top5["rank"].astype(int), c_lugar: top5["lugar"], c_pais: top5["pais"], c_par: top5["parecido"]})
        st.dataframe(tabla, hide_index=True, on_select="rerun", selection_mode="single-row", key="tabla_top",
                     alt=t(lang, "top_alt", sitio=site),
                     column_config={c_par: st.column_config.ProgressColumn(c_par, format="%d %%", min_value=0, max_value=100)})
        st.caption(t(lang, "top_nota"))


# ---- Place profile ----
def _nombre_celda(c: str) -> str:
    r = shown[shown["cell_id"].astype(str) == c].iloc[0]
    return f"{r['lugar']} ({r['pais']}) · {pct(r['parecido'] / 100, lang)}"


st.selectbox(t(lang, "ver_ficha"), ids, key="profile_cell", format_func=_nombre_celda)
fila = shown[shown["cell_id"].astype(str) == st.session_state["profile_cell"]].iloc[0]
f = ficha(fila, site, body)
cell = earth[earth["cell_id"] == f["cell_id"]].iloc[0]
usados = [d for d in DIMENSIONS if d in f["scores"] and weights[d] > 0]
with st.container(border=True):
    cab, der = st.columns([3, 2], vertical_alignment="center")
    with cab:
        st.header(fila["lugar"])
        st.caption(f"{fila['pais']} · {coordinates(f['lat'], f['lon'], lang)} · {describe_terrain(cell, lang)}")
    with der:
        st.markdown(f"**{t(lang, 'se_parece', sitio=site, n=fila['parecido'])}**")
        st.badge(t(lang, "calculado", n=len(usados), total=len(DIMENSIONS)), color="orange")
    # ---- Visual comparison: the Moon or Mars site against the Earth place (orbital views at the same scale) ----
    st.markdown(f"**{t(lang, 'comp_titulo', sitio=site, lugar=fila['lugar'])}**")
    capa = st.segmented_control(t(lang, "comp_capa"), ["modis", "bluemarble"], default="modis", required=True, key="capa_tierra",
                                format_func=lambda c: t(lang, f"comp_capa_{c}")) or "modis"
    st.caption(t(lang, "comp_intro", km=int(WINDOW_KM)))
    objetivo = (moon if body == "moon" else mars)
    objetivo = objetivo[objetivo["site"] == site].iloc[0]
    col_body, col_earth = st.columns(2)
    with col_body:
        if not view_available(body, float(objetivo["lat"])):
            st.caption(t(lang, "comp_polar"))
        else:
            try:
                with st.spinner(t(lang, "comp_cargando")):
                    foto = body_image(body, round(float(objetivo["lat"]), 4), round(float(objetivo["lon"]), 4))
                st.image(foto, caption=t(lang, "comp_pie_cuerpo", sitio=site, cuerpo=body_name(body, lang)),
                         alt=t(lang, "comp_alt_cuerpo", sitio=site, cuerpo=body_name(body, lang)))
                st.caption(t(lang, "comp_credito", credit=credit(body, lang=lang)))
            except NoImage:
                st.caption(t(lang, "comp_error"))
    with col_earth:
        try:
            with st.spinner(t(lang, "comp_cargando")):
                foto = earth_image(round(float(f["lat"]), 4), round(float(f["lon"]), 4), capa)
            st.image(foto, caption=t(lang, "comp_pie_tierra", lugar=fila["lugar"], pais=fila["pais"]),
                     alt=t(lang, "comp_alt_tierra", lugar=fila["lugar"], pais=fila["pais"]))
            st.caption(t(lang, "comp_credito", credit=credit("earth", capa, lang)))
        except NoImage:
            st.caption(t(lang, "comp_error"))
    rejilla = st.grid(len(DIMENSIONS), min_column_width=125, gap="small")  # 4 cards on desktop, 2 on mobile
    for d in DIMENSIONS:
        nombre, _ = aspect_info(d, lang)
        score = f["scores"].get(d)
        with rejilla.container(border=True, height="stretch"):
            st.markdown(f"**{nombre}**")
            if score is None:
                st.markdown(f"**{t(lang, 'sin_dato')}**")  # normal text, not a large metric: on mobile "No data" was cut off
                st.badge(t(lang, "sin_comparar"), color="gray")
            else:
                st.metric(nombre, pct(score, lang), label_visibility="collapsed")
                st.progress(min(max(score, 0.0), 1.0))
                etiqueta_n, color = match_level(score, lang)
                st.badge(etiqueta_n, color=color)
            st.caption(explain(d, score, cell, profiles[(body, site)], body, site, lang))
            if weights[d] == 0:
                st.caption(t(lang, "no_cuenta"))
    st.markdown(f"**{t(lang, 'no_imitar', cuerpo=body_name_of(body, lang))}**")
    with st.container(horizontal=True):
        for txt in short_limits(body, lang):
            st.badge(txt, color="blue")

with st.expander(t(lang, "tec_titulo")):
    m = evaluate(ranked, known_body)
    c1, c2 = st.columns(2)
    c1.metric(t(lang, "tec_auc"), f"{m['auc']:.2f}")
    c2.metric(t(lang, "tec_recall", n=f"{m['top_pct']:.0f}"), f"{m['recall_at_top_pct']:.2f}")
    st.caption(t(lang, "tec_nota"))
    extra = [c for c in ("viable", "dist_settlement_km", "settlement_name", "veg_ndvi_max") if c in shown.columns]
    st.dataframe(shown[["rank", "cell_id", "lugar", "pais", "lat", "lon", "score", *DIMENSIONS, *extra]].round(3), height=250,
                 alt=t(lang, "tec_tabla_alt", sitio=site))
    if "ice" in f["similar"]:
        st.caption(t(lang, "tec_hielo_nota"))
    with st.expander(t(lang, "tec_limites")):
        for item in (f["limits"] if lang == "es" else t(lang, f"limites_largos_{body}")):
            st.markdown(f"- {item}")

with st.expander(t(lang, "cand_titulo")):
    st.caption(t(lang, "cand_regla"))
    profiles_csv = RESULTS_DIR / "candidate_profiles.csv"
    if not profiles_csv.exists():
        profiles_csv = DEMO_DIR / "results" / "candidate_profiles.csv"
    if profiles_csv.exists():
        fc = pd.read_csv(profiles_csv)
        cols = [c for c in ("body", "cell_id", "lat", "lon", "n_targets", "score_mean", "ndvi_max", "dust_surface_ugm3",
                            "dist_settlement_km", "nearest_known", "nearest_known_km") if c in fc.columns]
        st.dataframe(fc[cols].round(2), hide_index=True, alt=t(lang, "cand_alt"))
        st.caption(t(lang, "cand_nota"))

with st.expander(t(lang, "atlas_titulo")):
    st.caption(t(lang, "atlas_mas"))

    def _res(name):
        p = RESULTS_DIR / name
        return p if p.exists() else DEMO_DIR / "results" / name

    if _res("atlas_regions.csv").exists() and _res("atlas_cells.csv").exists():
        reg, cel = pd.read_csv(_res("atlas_regions.csv")), pd.read_csv(_res("atlas_cells.csv"))
        ca, cb = st.columns(2)
        body_a = ca.selectbox(t(lang, "atlas_cuerpo"), ["mars", "moon"], format_func=lambda b: body_name(b, lang), key="atlas_body")
        asp = cb.selectbox(t(lang, "atlas_aspecto"), ["geo", "topo", "thermal", "ice"], key="atlas_aspect",
                           format_func=lambda a: t(lang, "atlas_hielo") if a == "ice" else aspect_info(a, lang)[0])
        g = reg[(reg["body"] == body_a) & (reg["aspect"] == asp)]
        conf = g["confidence"].iloc[0]
        msg = f"**{t(lang, 'atlas_confianza')}: {translate_confidence(conf, lang)}.** {translate_why(g['why'].iloc[0], lang)}"
        (st.warning if conf in ("baja", "muy baja", "sin datos") else st.info)(msg)
        top_a = g[g["rank"] > 0]
        if top_a.empty:
            st.caption(t(lang, "atlas_ninguna"))
        else:
            st.dataframe(top_a[["rank", "cell_id", "lat", "lon", "score", "n_targets", "nearest_known", "nearest_known_km"]].round(2),
                         hide_index=True, alt=t(lang, "atlas_tabla_alt"))
            pts = cel[(cel["body"] == body_a) & (cel["aspect"] == asp)]
            st.pydeck_chart(pdk.Deck(layers=[pdk.Layer("ScatterplotLayer", pts, get_position="[lon, lat]", get_radius=110000,
                                                       get_fill_color="[255, 140 - score * 100, 0, 60 + score * 180]", pickable=True)],
                                     initial_view_state=pdk.ViewState(latitude=20, longitude=0, zoom=0.6),
                                     views=[pdk.View(type="MapView", controller={"scrollZoom": False})],
                                     tooltip={"text": "{cell_id}\n" + ("score" if lang == "en" else "nota") + ": {score}"}),
                            alt=t(lang, "atlas_mapa_alt"))
        st.caption(t(lang, "atlas_nota"))

with st.expander(t(lang, "casos_titulo")):
    st.caption(t(lang, "casos_mas"))
    uc_csv = RESULTS_DIR / "usecases.csv"
    if not uc_csv.exists():
        uc_csv = DEMO_DIR / "results" / "usecases.csv"
    if uc_csv.exists():
        uc = pd.read_csv(uc_csv)
        titles = list(dict.fromkeys(uc["title"]))
        chosen = st.selectbox(t(lang, "casos_label"), titles, format_func=lambda x: translate_case(x, lang))
        view_uc = uc[uc["title"] == chosen]
        st.dataframe(view_uc[["rank", "cell_id", "lat", "lon", "score", "n_targets", "nearest_known", "nearest_known_km"]].round(2),
                     hide_index=True, alt=t(lang, "casos_alt"))
        st.caption(t(lang, "casos_nota"))

with st.expander(t(lang, "creditos_titulo")):
    st.markdown(t(lang, "creditos"))

pie()
