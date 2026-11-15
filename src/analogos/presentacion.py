"""Textos y reglas de presentación de la app, en español e inglés (propuesta de interfaz de Figma; ver docs/INTERFAZ.md).

Solo cambia cómo se MUESTRAN los resultados; el modelo, los datos y las cifras de validación no se tocan ni dependen del idioma.
Los textos viven en `i18n.py`; aquí está la lógica (qué frase corresponde a cada situación). Todas las funciones reciben `lang`
(«es» o «en»; español por defecto). Las cifras de confiabilidad salen de docs/PREREGISTRO_VALIDACION3.md (tres conjuntos de análogos
juntos, descriptivo).
"""
import pandas as pd

from .config import DIMENSIONS, LANDINGS_CSV
from .i18n import ATLAS_WHY_EN, CASOS_EN, CONFIANZA_EN, t

ASPECTOS = list(DIMENSIONS)  # topo, thermal, ice, geo

# Importancia -> peso del modelo (sin tocar la escala del modelo: 0 a 1). Las claves no dependen del idioma.
IMPORTANCIA = {"none": 0.0, "low": 0.33, "some": 0.66, "high": 1.0}

# Confiabilidad por cuerpo: acierto = u medio (50 % = adivinar) con los tres conjuntos de análogos juntos
CONFIABILIDAD = {
    "moon": {"pct": 58, "lo": 55, "hi": 62, "n": 20},
    "mars": {"pct": 60, "lo": 52, "hi": 67, "n": 40},
}


def cuerpo(body: str, lang: str = "es") -> str:
    return t(lang, f"cuerpo_{body}")


def cuerpo_de(body: str, lang: str = "es") -> str:
    return t(lang, f"cuerpo_de_{body}")


def aspecto(dim: str, lang: str = "es") -> tuple[str, str]:
    """(nombre claro, pregunta que responde) de un aspecto."""
    return t(lang, f"aspecto_{dim}"), t(lang, f"ayuda_{dim}")


def etiqueta_importancia(clave: str, lang: str = "es") -> str:
    return t(lang, f"imp_{clave}")


def confiabilidad(body: str, lang: str = "es") -> dict:
    """Cifras de confiabilidad de un cuerpo con su etiqueta y su explicación en el idioma pedido."""
    return {**CONFIABILIDAD[body], "nivel": t(lang, "conf_nivel"), "texto": t(lang, f"conf_{body}")}


def limites_cortos(body: str, lang: str = "es") -> list[str]:
    return t(lang, f"limites_{body}")


def glosario(lang: str = "es") -> list[tuple[str, str]]:
    return t(lang, "glosario_lista")


def aviso_confiabilidad(lang: str = "es") -> str:
    return t(lang, "aviso", luna=CONFIABILIDAD["moon"]["pct"], marte=CONFIABILIDAD["mars"]["pct"])


def nivel_parecido(score: float, lang: str = "es") -> tuple[str, str]:
    """(etiqueta, color de st.badge) para un puntaje de 0 a 1."""
    if score >= 0.8:
        return t(lang, "nivel_alto"), "green"
    if score >= 0.5:
        return t(lang, "nivel_medio"), "yellow"
    return t(lang, "nivel_bajo"), "red"


def pct(x: float, lang: str = "es") -> str:
    """Porcentaje: «82 %» en español (con espacio) y «82%» en inglés."""
    return f"{round(100 * x)} %" if lang == "es" else f"{round(100 * x)}%"


def coordenadas(lat: float, lon: float, lang: str = "es") -> str:
    """«32.5° N, 37.5° E» (en español, oeste = «O»)."""
    lon180 = ((lon + 180) % 360) - 180
    ns = t(lang, "orient_n") if lat >= 0 else t(lang, "orient_s")
    eo = t(lang, "orient_e") if lon180 >= 0 else t(lang, "orient_o")
    return f"{abs(lat):.1f}° {ns}, {abs(lon180):.1f}° {eo}"


def id_del_mapa(estado) -> str | None:
    """Celda elegida al hacer clic en un punto naranja del mapa (capa `candidatos`); None si no hay selección."""
    try:
        objs = estado["selection"]["objects"].get("candidatos") or []
    except (KeyError, TypeError, AttributeError):
        return None
    return str(objs[0].get("cell_id")) if objs else None


def id_de_la_tabla(estado, tabla: pd.DataFrame) -> str | None:
    """Celda de la fila elegida en una tabla con columna `cell_id`; None si no hay selección."""
    try:
        filas = estado["selection"]["rows"]
    except (KeyError, TypeError, AttributeError):
        return None
    return str(tabla.iloc[filas[0]]["cell_id"]) if filas else None


def seleccion_nueva(ultima: str | None, actual: str | None) -> str | None:
    """La selección del mapa o de la tabla solo cuenta una vez: devuelve `actual` si es distinta de la última aplicada."""
    return actual if actual and actual != ultima else None


def pesos_desde_importancia(niveles: dict[str, str]) -> dict[str, float]:
    return {d: IMPORTANCIA[niveles.get(d, "high")] for d in DIMENSIONS}


# Sitios con una frase propia (las notas de los CSV son técnicas); el resto usa «Sitio de aterrizaje (año)»
SITIOS_CON_FRASE = ("Jezero", "Oxia Planum", "Arcadia Planitia", "Shackleton rim", "Malapert massif", "Mare Tranquillitatis pit")


def descripcion_sitio(site: str, lang: str = "es") -> str:
    """Una frase del sitio objetivo (texto claro propio o misión y año del CSV de aterrizajes)."""
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


def describir_terreno(row: pd.Series, lang: str = "es") -> str:
    """Frase corta del terreno de una celda de la Tierra, a partir de sus propias características."""
    b, s = row.get("geo__basalt_frac"), row.get("topo__slope_mean_deg")
    partes = []
    if pd.notna(b) and b >= 0.5:
        partes.append(t(lang, "terreno_volcanica"))
    elif pd.notna(b) and b >= 0.2:
        partes.append(t(lang, "terreno_algo_volcanica"))
    if pd.notna(s):
        partes.append(t(lang, "terreno_llano" if s < 2 else "terreno_ondulado" if s < 6 else "terreno_montanoso"))
    return ", ".join(partes) if partes else t(lang, "terreno_sin")


def explicar(dim: str, score: float | None, row: pd.Series, profile: pd.Series, body: str, site: str, lang: str = "es") -> str:
    """Una frase que dice qué significa el parecido de un aspecto para esta celda."""
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


# ---- textos de los archivos de resultados (están en español): en inglés se traducen si hay traducción exacta ----
def traducir_caso(titulo: str, lang: str = "es") -> str:
    return CASOS_EN.get(titulo, titulo) if lang == "en" else titulo


def traducir_confianza(nivel: str, lang: str = "es") -> str:
    return CONFIANZA_EN.get(nivel, nivel) if lang == "en" else nivel


def traducir_why(texto: str, lang: str = "es") -> str:
    return ATLAS_WHY_EN.get(texto, texto) if lang == "en" else texto
