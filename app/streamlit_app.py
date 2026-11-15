"""AstroAtlas app: places on Earth that resemble the Moon and Mars. Run: streamlit run app/streamlit_app.py

Available in Spanish and English (language selector at the top of the sidebar; also `?lang=en` in the address). Design after the
interface proposal "AstroAtlas — Interface proposal" (Figma). It only changes how things are shown: the model does not change.
Accessibility, usability and languages: see docs/app/interface.md.
"""
import re
from datetime import date

import altair as alt
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
from astroatlas.regions import REGIONS, macro_region
from astroatlas.report import ficha
from astroatlas.report_pdf import build_report
from astroatlas.risks import KEYS as RISK_KEYS, RGB, RGB_UNKNOWN, level_name, risk_levels, risk_values, target_slope_level
from astroatlas.sensitivity import rank_span, sensitivity
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


@st.cache_data(show_spinner=False)
def sens_table(_earth, _profile, _topo, body_: str, site_: str, weights_t: tuple, cell_id: str, visible_t: tuple):
    """Rank of one place when each aspect is switched off in turn (cached per site, weights, place and visible cells)."""
    return sensitivity(_earth, _profile, dict(weights_t), _topo, cell_id, set(visible_t))


LEVEL_TEXT = {"low": "riesgo_bajo", "medium": "riesgo_medio", "high": "riesgo_alto", "unknown": "riesgo_sin_dato"}
LEVEL_BADGE = {"low": "green", "medium": "orange", "high": "red", "unknown": "gray"}


def risk_label(level) -> str:
    return t(lang, LEVEL_TEXT[level_name(level)])


@st.cache_data
def featured_candidates() -> list:
    """Top two cells of the basaltic-terrain-for-Mars use case (the featured mission case)."""
    csv = RESULTS_DIR / "usecases.csv"
    csv = csv if csv.exists() else DEMO_DIR / "results" / "usecases.csv"
    uc = pd.read_csv(csv)
    top = uc[uc["use_case"] == "basalto_marte"].sort_values("rank").head(2)
    return [{"cell_id": r.cell_id, "lat": float(r.lat), "lon": float(r.lon), "score": float(r.score)} for r in top.itertuples()]


FEATURED_NOTE = {"earth_24_43": "destacado_harrat", "earth_23_39": "destacado_haruj"}


def go_featured(cell_id: str):
    """Callback of the featured-case button: Mars (Jezero), volcanic terrain only, and the first candidate opened."""
    st.session_state["sitio"] = ("mars", "Jezero")
    st.session_state["only_volcanic"] = True
    st.session_state["profile_cell"] = cell_id


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

# ---- Featured mission case: the best-supported use of the tool ----
_feat = featured_candidates()
if _feat:
    with st.container(border=True):
        st.markdown(f"**{t(lang, 'destacado_titulo')}**")
        st.caption(t(lang, "destacado_texto"))
        for col, c in zip(st.columns(len(_feat)), _feat):
            lugar_c, pais_c = nombres(((round(c["lat"], 3), round(c["lon"], 3)),), lang)[0]
            risk_c = risk_levels(pd.DataFrame([earth[earth["cell_id"] == c["cell_id"]].iloc[0]])).iloc[0]["overall"]
            with col:
                st.markdown(f"**{t(lang, 'destacado_cand', lugar=lugar_c, pais=pais_c, n=round(100 * c['score']))}**")
                if c["cell_id"] in FEATURED_NOTE:
                    st.caption(t(lang, FEATURED_NOTE[c["cell_id"]]))
                st.badge(f"{t(lang, 'riesgo_general')}: {risk_label(risk_c)}", color=LEVEL_BADGE[level_name(risk_c)])
        st.button(t(lang, "destacado_boton"), on_click=go_featured, args=(_feat[0]["cell_id"],), key="go_featured",
                  icon=":material/travel_explore:")
        st.caption(t(lang, "destacado_nota"))

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
    only_volcanic = st.checkbox(t(lang, "f_volc"), key="only_volcanic")
    st.caption(t(lang, "f_volc_ayuda"))
    sel_regions = st.multiselect(t(lang, "f_region"), REGIONS, default=REGIONS, key="regions",
                                 format_func=lambda k: t(lang, f"region_{k}"))
    st.caption(t(lang, "f_region_ayuda"))
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
ranked["region"] = macro_region(ranked["lat"].values, ranked["lon"].values)
ranked = ranked.merge(earth[["cell_id", "geo__basalt_frac"]], on="cell_id", how="left", suffixes=("", "_cell"))
# the filters only affect what is SHOWN; the validation (in "Technical details") uses the full `ranked`
view = ranked[ranked["viable"].fillna(True).astype(bool)] if (has_viability and hide_populated) else ranked
if has_veg and hide_vegetated:
    view = view[~view["vegetated"].fillna(False).astype(bool)]
if set(sel_regions) != set(REGIONS):
    view = view[view["region"].isin(sel_regions)]
if only_volcanic:
    view = view[view["geo__basalt_frac"].fillna(0) >= 0.5]
shown = (novel_candidates(view, known_body, n=top_n) if only_novel else view.head(top_n)).copy()
if shown.empty:
    st.warning(t(lang, "sin_lugares"))
    pie()
    st.stop()
lab = nombres(tuple(zip(shown["lat"].round(3), shown["lon"].round(3))), lang)
shown["lugar"], shown["pais"] = [x[0] for x in lab], [x[1] for x in lab]
shown["parecido"] = (shown["score"] * 100).round().astype(int)
shown["detalle"] = [t(lang, "tooltip_detalle", pais=p, n=n) for p, n in zip(shown["pais"], shown["parecido"])]
# field-site risk indicators (information only; they never change the score)
_rk = risk_levels(earth.set_index("cell_id").reindex(shown["cell_id"].values).reset_index(drop=True))
shown["riesgo"] = _rk["overall"].values
shown["riesgo_txt"] = [t(lang, "tooltip_riesgo", pais=p, nivel=risk_label(v)) for p, v in zip(shown["pais"], shown["riesgo"])]
_rgb = [RGB.get(int(v), RGB_UNKNOWN) if pd.notna(v) else RGB_UNKNOWN for v in shown["riesgo"]]
shown["rr"], shown["gg"], shown["bb"] = [c[0] for c in _rgb], [c[1] for c in _rgb], [c[2] for c in _rgb]
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


# ---- Mapa y reliability ----
col_map, col_rel = st.columns([3, 2])
with col_map:
    st.header(t(lang, "mapa_titulo", sitio=site, cuerpo=body_name(body, lang)))
    color_mode = st.segmented_control(t(lang, "mapa_color_label"), ["sim", "risk"], default="sim", required=True, key="map_color",
                                      format_func=lambda k: t(lang, "mapa_color_sim" if k == "sim" else "mapa_color_riesgo")) or "sim"
    sel = shown[shown["cell_id"].astype(str) == pick]
    known_map = known.assign(lugar=known["name"], detalle=t(lang, "tooltip_conocido"))
    layers = [
        pdk.Layer("ScatterplotLayer", shown, id="candidatos", get_position="[lon, lat]", get_radius=110000,
                  get_fill_color=("[255, 140 - score * 100, 0, 60 + score * 180]" if color_mode == "sim" else "[rr, gg, bb, 210]"),
                  pickable=True),
        pdk.Layer("ScatterplotLayer", known_map, id="conocidos", get_position="[lon, lat]", get_radius=110000, filled=False,
                  stroked=True, get_line_color="[76, 141, 246, 255]", line_width_min_pixels=3, pickable=True),
        pdk.Layer("ScatterplotLayer", sel, id="elegido", get_position="[lon, lat]", get_radius=170000, filled=False, stroked=True,
                  get_line_color="[255, 255, 255, 255]", line_width_min_pixels=3),
    ]
    # no wheel zoom: so the wheel keeps scrolling the page when the cursor passes over the map (there are + and − buttons)
    st.pydeck_chart(pdk.Deck(layers=layers, initial_view_state=pdk.ViewState(latitude=20, longitude=0, zoom=0.6),
                             views=[pdk.View(type="MapView", controller={"scrollZoom": False})],
                             tooltip={"text": "{lugar}\n" + ("{detalle}" if color_mode == "sim" else "{riesgo_txt}")}),
                    on_select="rerun", selection_mode="single-object", key="mapa", alt=t(lang, "mapa_alt", sitio=site))
    st.caption("  \n".join(t(lang, "leyenda_lista" if color_mode == "sim" else "leyenda_riesgo")))

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


st.info(reliability_notice(lang), title=t(lang, "aviso_titulo"), icon=":material/target:")
with st.expander(t(lang, "glosario_titulo")):
    for termino, definicion in glossary(lang):
        st.markdown(f"- **{termino}:** {definicion}")

# ---- Place profile ----
def _nombre_celda(c: str) -> str:
    r = shown[shown["cell_id"].astype(str) == c].iloc[0]
    return f"{r['lugar']} ({r['pais']}) · {pct(r['parecido'] / 100, lang)}"


st.selectbox(t(lang, "ver_ficha"), ids, key="profile_cell", format_func=_nombre_celda)
fila = shown[shown["cell_id"].astype(str) == st.session_state["profile_cell"]].iloc[0]
f = ficha(fila, site, body)
cell = earth[earth["cell_id"] == f["cell_id"]].iloc[0]
usados = [d for d in DIMENSIONS if d in f["scores"] and weights[d] > 0]
target_profile = profiles[(body, site)]

# rank sensitivity: the place's rank when each aspect is switched off in turn
sens = sens_table(earth, target_profile, topo_model_for(earth), body, site, tuple(sorted(weights.items())), str(f["cell_id"]),
                  tuple(sorted(view["cell_id"].astype(str))))


def scenario_label(key: str) -> str:
    return t(lang, "sens_todas") if key == "all" else t(lang, "sens_sin", aspecto=aspect_info(key, lang)[0].lower())


def sens_summary() -> str | None:
    """Plain-language reading of the sensitivity table (None if there is only one active aspect)."""
    lo, hi = rank_span(sens)
    if len(sens) < 2 or hi == 0:
        return None
    key = "sens_estable" if hi - lo <= max(3, 0.5 * lo) else "sens_varia"
    return t(lang, key, k=hi, lo=lo, hi=hi)


# field-site risks of this place and of the target site itself
cell_risk = risk_levels(pd.DataFrame([cell])).iloc[0]
cell_values = risk_values(cell)
target_v, target_lvl = target_slope_level(target_profile)


def make_pdf() -> bytes:
    """Site feasibility report (built only when the user clicks the download button)."""
    objective = (moon if body == "moon" else mars)
    objective = objective[objective["site"] == site].iloc[0]
    imgs = []
    try:
        imgs.append((body_image(body, round(float(objective["lat"]), 4), round(float(objective["lon"]), 4))
                     if view_available(body, float(objective["lat"])) else None,
                     t(lang, "comp_pie_cuerpo", sitio=site, cuerpo=body_name(body, lang)), credit(body, lang=lang)))
    except NoImage:
        imgs.append((None, t(lang, "comp_pie_cuerpo", sitio=site, cuerpo=body_name(body, lang)), credit(body, lang=lang)))
    try:
        imgs.append((earth_image(round(float(f["lat"]), 4), round(float(f["lon"]), 4), capa),
                     t(lang, "comp_pie_tierra", lugar=fila["lugar"], pais=fila["pais"]), credit("earth", capa, lang)))
    except NoImage:
        imgs.append((None, t(lang, "comp_pie_tierra", lugar=fila["lugar"], pais=fila["pais"]), credit("earth", capa, lang)))
    rel_ = reliability(body, lang)
    aspects = []
    for d in DIMENSIONS:
        sc = f["scores"].get(d)
        aspects.append({"name": aspect_info(d, lang)[0], "pct": None if sc is None else round(100 * sc),
                        "level": t(lang, "sin_comparar") if sc is None else match_level(sc, lang)[0],
                        "text": explain(d, sc, cell, target_profile, body, site, lang)})
    sens_rows = [{"scenario": scenario_label(r.scenario), "rank": "-" if pd.isna(r["rank"]) else f"#{int(r['rank'])} / {int(r.n)}",
                  "score": "-" if pd.isna(r.score) else pct(r.score, lang)} for _, r in sens.iterrows()]
    risks = [{"name": t(lang, f"r_{k}"), "level": level_name(cell_risk[k]), "level_text": risk_label(cell_risk[k]),
              "value": "-" if pd.isna(cell_values[k]) else t(lang, f"rv_{k}", v=cell_values[k])} for k in RISK_KEYS]
    return build_report({
        "date": date.today().isoformat(), "place": fila["lugar"], "country": fila["pais"], "site": site, "body_name": body_name(body, lang),
        "coords": coordinates(f["lat"], f["lon"], lang), "terrain": describe_terrain(cell, lang), "match_pct": int(fila["parecido"]),
        "n_aspects": len(usados), "n_total": len(DIMENSIONS), "aspects": aspects, "reliability": rel_,
        "sensitivity": {"summary": sens_summary() or t(lang, "sens_una"), "rows": sens_rows},
        "risk_overall": (risk_label(cell_risk["overall"]), level_name(cell_risk["overall"])), "risks": risks,
        "target_risk": None if pd.isna(target_v) else t(lang, "riesgo_objetivo", sitio=site, v=target_v, nivel=risk_label(target_lvl)),
        "limits": f["limits"] if lang == "es" else t(lang, f"limites_largos_{body}"), "images": imgs}, lang)


with st.container(border=True):
    cab, der = st.columns([3, 2], vertical_alignment="center")
    with cab:
        st.header(fila["lugar"])
        st.caption(f"{fila['pais']} · {coordinates(f['lat'], f['lon'], lang)} · {describe_terrain(cell, lang)}")
    with der:
        st.markdown(f"**{t(lang, 'se_parece', sitio=site, n=fila['parecido'])}**")
        st.badge(t(lang, "calculado", n=len(usados), total=len(DIMENSIONS)), color="orange")
        _slug = lambda s: re.sub(r"[^A-Za-z0-9]+", "_", s).strip("_")
        st.download_button(t(lang, "pdf_boton"), data=make_pdf, mime="application/pdf", icon=":material/download:", on_click="ignore",
                           file_name=t(lang, "pdf_archivo", lugar=_slug(fila["lugar"]), sitio=_slug(site)), key="pdf_dl")
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
    # ---- Field-site risks (indicative) ----
    st.markdown(f"**{t(lang, 'riesgo_titulo')}**")
    st.badge(f"{t(lang, 'riesgo_general')}: {risk_label(cell_risk['overall'])}", color=LEVEL_BADGE[level_name(cell_risk["overall"])])
    for k in RISK_KEYS:
        val = "-" if pd.isna(cell_values[k]) else t(lang, f"rv_{k}", v=cell_values[k])
        st.markdown(f"- **{t(lang, f'r_{k}')}**: {val} · {risk_label(cell_risk[k])}")
    if not pd.isna(target_v):
        st.caption(t(lang, "riesgo_objetivo", sitio=site, v=target_v, nivel=risk_label(target_lvl)))
    st.caption(t(lang, "riesgo_nota"))
    st.caption(t(lang, "riesgo_no_evaluado"))

# ---- Sensitivity: how much does the rank depend on each aspect? ----
with st.expander(t(lang, "sens_titulo")):
    ok = sens["rank"].notna()
    if len(sens) < 2:
        st.caption(t(lang, "sens_una"))
    elif not ok.any():
        st.caption(t(lang, "sens_una"))
    else:
        st.caption(t(lang, "sens_intro", lugar=fila["lugar"], n=int(sens["n"].iloc[0])))
        labels = [scenario_label(k) for k in sens["scenario"]]
        chart_df = pd.DataFrame({"scenario": labels, "rank": sens["rank"].astype("float")})
        base = alt.Chart(chart_df).encode(y=alt.Y("scenario:N", sort=None, title=None, axis=alt.Axis(labelLimit=260)), x=alt.X("rank:Q", title=t(lang, "sens_col_puesto")))
        st.altair_chart(base.mark_bar(color="#FF8C42") + base.mark_text(align="left", dx=4, color="#E6EDF3").encode(text="rank:Q"),
                        width="stretch")
        st.caption(t(lang, "sens_alt", lugar=fila["lugar"]))
        tops = nombres(tuple(zip(sens["top_lat"].round(3), sens["top_lon"].round(3))), lang)
        st.dataframe(pd.DataFrame({t(lang, "sens_col_escenario"): labels,
                                   t(lang, "sens_col_puesto"): [None if pd.isna(r) else int(r) for r in sens["rank"]],
                                   t(lang, "sens_col_parecido"): [None if pd.isna(s) else pct(s, lang) for s in sens["score"]],
                                   t(lang, "sens_col_primero"): [f"{a} ({b})" for a, b in tops]}), hide_index=True,
                     alt=t(lang, "sens_alt", lugar=fila["lugar"]))
        st.markdown(sens_summary())

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
