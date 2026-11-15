"""Textos y reglas de presentación de la app (docs de diseño: AstroAtlas, propuesta de interfaz en Figma).

Solo cambia cómo se MUESTRAN los resultados; el modelo, los datos y las cifras de validación no se tocan.
Las cifras de confiabilidad salen de docs/PREREGISTRO_VALIDACION3.md (tres conjuntos de análogos juntos, descriptivo).
"""
import pandas as pd

from .config import DIMENSIONS, LANDINGS_CSV

CUERPO_ES = {"moon": "Luna", "mars": "Marte"}
CUERPO_DE = {"moon": "la Luna", "mars": "Marte"}

# Aspecto -> (nombre claro, pregunta que responde)
ASPECTOS = {
    "topo": ("Relieve", "Qué tan plano o montañoso es"),
    "thermal": ("Temperatura", "Calor de día y frío de noche"),
    "ice": ("Hielo o agua", "Si hay hielo o agua en el suelo"),
    "geo": ("Geología", "Si es roca volcánica (basalto)"),
}

# Importancia -> peso del modelo (sin tocar la escala del modelo: 0 a 1)
IMPORTANCIA = {"No importa": 0.0, "Importa poco": 0.33, "Importa algo": 0.66, "Importa mucho": 1.0}

# Confiabilidad por cuerpo: acierto = u medio (50 % = adivinar) con los tres conjuntos de análogos juntos
CONFIABILIDAD = {
    "moon": {"pct": 58, "lo": 55, "hi": 62, "n": 20, "nivel": "Confianza baja",
             "texto": "Supera el azar por poco. Reconoce los lugares volcánicos y de impacto; falla con los fríos."},
    "mars": {"pct": 60, "lo": 52, "hi": 67, "n": 40, "nivel": "Confianza baja",
             "texto": "Reconoce bien los lugares secos y volcánicos. Falla con los lugares fríos y con hielo."},
}

LIMITES_CORTOS = {
    "moon": ["Gravedad: 1/6 de la terrestre", "Sin atmósfera (vacío)", "Radiación sin protección", "Polvo abrasivo en el suelo"],
    "mars": ["Gravedad: 38 % de la terrestre", "Atmósfera muy delgada", "Radiación alta", "Percloratos en el suelo"],
}


def aviso_confiabilidad() -> str:
    m, M = CONFIABILIDAD["moon"], CONFIABILIDAD["mars"]
    return (f"El método acierta ≈ {m['pct']} % en la Luna y ≈ {M['pct']} % en Marte. Como referencia: 50 % sería adivinar. "
            "Úsalo para encontrar lugares que valga la pena revisar con expertos.")


def nivel_parecido(score: float) -> tuple[str, str]:
    """(etiqueta, color de st.badge) para un puntaje de 0 a 1."""
    if score >= 0.8:
        return "Muy parecido", "green"
    if score >= 0.5:
        return "Parecido medio", "orange"
    return "Poco parecido", "red"


def pct(x: float) -> str:
    return f"{round(100 * x)} %"


def pesos_desde_importancia(niveles: dict[str, str]) -> dict[str, float]:
    return {d: IMPORTANCIA[niveles.get(d, "Importa mucho")] for d in DIMENSIONS}


# Frases claras para los sitios que no son aterrizajes históricos (las notas de los CSV son técnicas)
DESCRIPCIONES = {
    "Jezero": "Cráter con un antiguo delta de río. Aquí está el rover Perseverance.",
    "Oxia Planum": "Llanura con arcillas, sitio del rover europeo ExoMars.",
    "Arcadia Planitia": "Llanura del norte de Marte con hielo cerca de la superficie.",
    "Shackleton rim": "Borde de un cráter en el polo sur de la Luna, con zonas en sombra permanente.",
    "Malapert massif": "Montaña cerca del polo sur de la Luna, con luz solar casi continua.",
    "Mare Tranquillitatis pit": "Hoyo en el Mar de la Tranquilidad, posible entrada a un tubo de lava.",
}


def descripcion_sitio(site: str) -> str:
    """Una frase del sitio objetivo (texto claro propio o misión y año del CSV de aterrizajes)."""
    if site in DESCRIPCIONES:
        return DESCRIPCIONES[site]
    try:
        a = pd.read_csv(LANDINGS_CSV)
        r = a[a["mission"] == site]
        if not r.empty:
            y = r["year"].iloc[0]
            return f"Sitio de aterrizaje ({int(y)})" if pd.notna(y) else "Sitio de aterrizaje o candidato"
    except (OSError, KeyError, ValueError):
        pass
    return ""


def describir_terreno(row: pd.Series) -> str:
    """Frase corta del terreno de una celda de la Tierra, a partir de sus propias características."""
    b, s = row.get("geo__basalt_frac"), row.get("topo__slope_mean_deg")
    partes = []
    if pd.notna(b) and b >= 0.5:
        partes.append("roca volcánica")
    elif pd.notna(b) and b >= 0.2:
        partes.append("algo de roca volcánica")
    if pd.notna(s):
        partes.append("llano" if s < 2 else "ondulado" if s < 6 else "montañoso")
    return ", ".join(partes) if partes else "terreno sin descripción"


def explicar(dim: str, score: float | None, row: pd.Series, profile: pd.Series, body: str, site: str) -> str:
    """Una frase que dice qué significa el parecido de un aspecto para esta celda."""
    cuerpo = CUERPO_DE[body]
    if dim == "thermal" and score is None:
        return ("No hay un mapa de temperatura de Marte que sirva para comparar." if body == "mars"
                else "Falta el dato de temperatura para comparar este lugar.")
    if score is None:
        return "No se pudo comparar este aspecto."
    if dim == "topo":
        cs, ps = row.get("topo__slope_mean_deg"), profile.get("topo__slope_mean_deg")
        if pd.isna(cs) or pd.isna(ps) or ps <= 0 or score >= 0.8:
            return f"El terreno tiene pendientes y rugosidad parecidas a {site}."
        r = cs / ps
        if r > 1.25:
            return f"El terreno es algo más rugoso que en {site}."
        if r < 0.8:
            return f"El terreno es algo más llano que en {site}."
        return f"La pendiente media es parecida, pero la forma del relieve difiere de {site}."
    if dim == "thermal":
        ct, pt = row.get("thermal__t_max_k"), profile.get("thermal__t_max_k")
        if pd.notna(ct) and pd.notna(pt) and abs(ct - pt) >= 15:
            return f"Hace más {'calor' if ct > pt else 'frío'} que en {site} en el mes más cálido."
        return f"Temperaturas máximas y rango entre día y noche parecidos a {site}."
    if dim == "ice":
        nieve = row.get("ice__water_frac")
        if score >= 0.7 and pd.notna(nieve) and nieve < 0.1:
            return "Ojo: coincide porque no hay nieve, no porque haya hielo bajo el suelo."
        if score >= 0.7:
            return "Coincide en cobertura de nieve, que es solo una pista del hielo bajo el suelo."
        return "En la Tierra se mide con la nieve; aquí no coincide con el hielo del sitio."
    if dim == "geo":
        b = row.get("geo__basalt_frac")
        if pd.notna(b) and b >= 0.5:
            return f"Es roca volcánica (basalto), como gran parte de {'Marte' if body == 'mars' else 'los mares lunares'}."
        if pd.notna(b) and b >= 0.2:
            return f"Tiene algo de roca volcánica (basalto), el tipo de roca de {cuerpo}."
        return "Tiene poca roca volcánica (basalto)."
    return ""
