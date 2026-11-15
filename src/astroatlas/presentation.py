"""Presentation texts and rules of the app, in Spanish and English (Figma interface proposal; see docs/app/interface.md).

It only changes how the results are SHOWN; the model, the data and the validation figures are neither touched nor language-dependent.
The texts live in `i18n.py`; the logic (which sentence fits each situation) is here. All functions take `lang`
("es" or "en"; English by default). The reliability figures come from docs/preregistrations/validation-set-3.md (three sets of analogs
together, descriptive).
"""
import pandas as pd

from .config import DIMENSIONS, LANDINGS_CSV
from .i18n import ATLAS_WHY_EN, CASES_EN, CONFIDENCE_EN, t

ASPECTOS = list(DIMENSIONS)  # topo, thermal, ice, geo

# Importance -> model weight (without touching the model scale: 0 to 1). The keys do not depend on the language.
IMPORTANCE = {"none": 0.0, "low": 0.33, "some": 0.66, "high": 1.0}

# Reliability per body: hit rate = mean u (50 % = guessing) with the three analog sets together
RELIABILITY = {
    "moon": {"pct": 58, "lo": 55, "hi": 62, "n": 20},
    "mars": {"pct": 60, "lo": 52, "hi": 67, "n": 40},
}


def body_name(body: str, lang: str = "en") -> str:
    return t(lang, f"cuerpo_{body}")


def body_name_of(body: str, lang: str = "en") -> str:
    return t(lang, f"cuerpo_de_{body}")


def aspect_info(dim: str, lang: str = "en") -> tuple[str, str]:
    """(clear name, question it answers) of an aspect."""
    return t(lang, f"aspecto_{dim}"), t(lang, f"ayuda_{dim}")


def importance_label(clave: str, lang: str = "en") -> str:
    return t(lang, f"imp_{clave}")


def reliability(body: str, lang: str = "en") -> dict:
    """Reliability figures of a body with its label and explanation in the requested language."""
    return {**RELIABILITY[body], "nivel": t(lang, "conf_nivel"), "texto": t(lang, f"conf_{body}")}


def short_limits(body: str, lang: str = "en") -> list[str]:
    return t(lang, f"limites_{body}")


def glossary(lang: str = "en") -> list[tuple[str, str]]:
    return t(lang, "glosario_lista")


def reliability_notice(lang: str = "en") -> str:
    return t(lang, "aviso", luna=RELIABILITY["moon"]["pct"], marte=RELIABILITY["mars"]["pct"])


def match_level(score: float, lang: str = "en") -> tuple[str, str]:
    """(label, st.badge colour) for a score from 0 to 1."""
    if score >= 0.8:
        return t(lang, "nivel_alto"), "green"
    if score >= 0.5:
        return t(lang, "nivel_medio"), "yellow"
    return t(lang, "nivel_bajo"), "red"


def pct(x: float, lang: str = "en") -> str:
    """Percentage: "82 %" in Spanish (with a space) and "82%" in English."""
    return f"{round(100 * x)} %" if lang == "es" else f"{round(100 * x)}%"


def coordinates(lat: float, lon: float, lang: str = "en") -> str:
    """"32.5° N, 37.5° E" (in Spanish, west = "O")."""
    lon180 = ((lon + 180) % 360) - 180
    ns = t(lang, "orient_n") if lat >= 0 else t(lang, "orient_s")
    eo = t(lang, "orient_e") if lon180 >= 0 else t(lang, "orient_o")
    return f"{abs(lat):.1f}° {ns}, {abs(lon180):.1f}° {eo}"


def map_selection_id(status) -> str | None:
    """Cell chosen by clicking an orange point on the map (`candidatos` layer); None if there is no selection."""
    try:
        objs = status["selection"]["objects"].get("candidatos") or []
    except (KeyError, TypeError, AttributeError):
        return None
    return str(objs[0].get("cell_id")) if objs else None


def table_selection_id(status, tabla: pd.DataFrame) -> str | None:
    """Cell of the row chosen in a table with a `cell_id` column; None if there is no selection."""
    try:
        filas = status["selection"]["rows"]
    except (KeyError, TypeError, AttributeError):
        return None
    return str(tabla.iloc[filas[0]]["cell_id"]) if filas else None


def new_selection(ultima: str | None, actual: str | None) -> str | None:
    """A map or table selection counts only once: returns `actual` if it differs from the last one applied."""
    return actual if actual and actual != ultima else None


def weights_from_importance(niveles: dict[str, str]) -> dict[str, float]:
    return {d: IMPORTANCE[niveles.get(d, "high")] for d in DIMENSIONS}


# Sites with their own sentence (the CSV notes are technical); the rest use "Landing site (year)"
SITIOS_CON_FRASE = ("Jezero", "Oxia Planum", "Arcadia Planitia", "Shackleton rim", "Malapert massif", "Mare Tranquillitatis pit")


def site_description(site: str, lang: str = "en") -> str:
    """One sentence about the target site (own plain text, or mission and year from the landings CSV)."""
    if site in SITIOS_CON_FRASE:
        return t(lang, f"desc_{site}")
    try:
        a = pd.read_csv(LANDINGS_CSV)
        r = a[a["mission"] == site]
        if not r.empty:
            y = r["year"].iloc[0]
            return t(lang, "sitio_aterrizaje", year=int(y)) if pd.notna(y) else t(lang, "sitio_aterrizaje_gen")
    except (OSError, KeyError, ValueError):
        pass
    return ""


def describe_terrain(row: pd.Series, lang: str = "en") -> str:
    """Short sentence about the terrain of an Earth cell, from its own characteristics."""
    b, s = row.get("geo__basalt_frac"), row.get("topo__slope_mean_deg")
    partes = []
    if pd.notna(b) and b >= 0.5:
        partes.append(t(lang, "terreno_volcanica"))
    elif pd.notna(b) and b >= 0.2:
        partes.append(t(lang, "terreno_algo_volcanica"))
    if pd.notna(s):
        partes.append(t(lang, "terreno_llano" if s < 2 else "terreno_ondulado" if s < 6 else "terreno_montanoso"))
    return ", ".join(partes) if partes else t(lang, "terreno_sin")


def explain(dim: str, score: float | None, row: pd.Series, profile: pd.Series, body: str, site: str, lang: str = "en") -> str:
    """One sentence saying what the similarity of an aspect means for this cell."""
    if dim == "thermal" and score is None:
        return t(lang, "ex_thermal_marte" if body == "mars" else "ex_thermal_falta")
    if score is None:
        return t(lang, "ex_sin_comparar")
    if dim == "topo":
        cs, ps = row.get("topo__slope_mean_deg"), profile.get("topo__slope_mean_deg")
        if pd.isna(cs) or pd.isna(ps) or ps <= 0 or score >= 0.8:
            return t(lang, "ex_topo_igual", sitio=site)
        r = cs / ps
        if r > 1.25:
            return t(lang, "ex_topo_rugoso", sitio=site)
        if r < 0.8:
            return t(lang, "ex_topo_llano", sitio=site)
        return t(lang, "ex_topo_forma", sitio=site)
    if dim == "thermal":
        ct, pt = row.get("thermal__t_max_k"), profile.get("thermal__t_max_k")
        if pd.notna(ct) and pd.notna(pt) and abs(ct - pt) >= 15:
            return t(lang, "ex_thermal_calor" if ct > pt else "ex_thermal_frio", sitio=site)
        return t(lang, "ex_thermal_igual", sitio=site)
    if dim == "ice":
        nieve = row.get("ice__water_frac")
        if score >= 0.7 and pd.notna(nieve) and nieve < 0.1:
            return t(lang, "ex_ice_sin_nieve")
        return t(lang, "ex_ice_nieve" if score >= 0.7 else "ex_ice_no")
    if dim == "geo":
        b = row.get("geo__basalt_frac")
        if pd.notna(b) and b >= 0.5:
            return t(lang, "ex_geo_si", de=t(lang, f"geo_de_{body}"))
        if pd.notna(b) and b >= 0.2:
            return t(lang, "ex_geo_algo", de=t(lang, f"geo_cuerpo_{body}"))
        return t(lang, "ex_geo_poco")
    return ""


# ---- texts from the results files (they are in Spanish): in English they are translated if there is an exact translation ----
def translate_case(titulo: str, lang: str = "en") -> str:
    return CASES_EN.get(titulo, titulo) if lang == "en" else titulo


def translate_confidence(nivel: str, lang: str = "en") -> str:
    return CONFIDENCE_EN.get(nivel, nivel) if lang == "en" else nivel


def translate_why(texto: str, lang: str = "en") -> str:
    return ATLAS_WHY_EN.get(texto, texto) if lang == "en" else texto
