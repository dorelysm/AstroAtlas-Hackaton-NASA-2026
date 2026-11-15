"""Atlas por aspecto: para cada dimensión, qué lugares de la Tierra se parecen a los objetivos de la Luna o de Marte SOLO por ese aspecto.

El reto dice que un lugar puede ser un excelente análogo geológico y uno pobre en temperatura. Un ranking global mezcla todo; aquí cada
aspecto se evalúa por separado y lleva una etiqueta de CONFIANZA que sale de los resultados de validación ya medidos (no de una opinión).
El puntaje de una celda es la media, sobre todos los objetivos del cuerpo con dato en ese aspecto, de su similitud en esa dimensión.

    python -m analogos.atlas
"""
from dataclasses import dataclass

import pandas as pd

from .config import DIMENSIONS, FEATURES_DIR, RESULTS_DIR
from .features import load_features
from .similarity import fit_topo_model, site_profiles
from .usecases import UseCase, pick_regions, score_use_case
from .validate import haversine_km, load_known

MIN_USEFUL_SCORE = 0.10  # por debajo, ninguna celda se parece de verdad: no se lista (un empate en ~0 no es una recomendación)
ASPECT_LABEL = {"topo": "Topografía", "thermal": "Térmica", "ice": "Hielo / agua", "geo": "Geología"}


@dataclass(frozen=True)
class Confidence:
    level: str   # alta | media | baja | muy baja | sin datos
    why: str
    doc: str


# Etiquetas de confianza. Cada una cita el resultado medido que la justifica (docs/VALIDACION_ASPECTO.md y PREREGISTRO_*.md).
CONFIDENCE: dict[tuple[str, str], Confidence] = {
    ("moon", "topo"): Confidence("baja", "Con la capa del USGS (cráteres frente a controles igual de llanos) no hay señal: AUC 0,48. "
                                 "Por análogos etiquetados, +0,14 con intervalo que incluye el cero.", "PREREGISTRO_LLANURA.md"),
    ("mars", "topo"): Confidence("baja", "La ventaja inicial (AUC 0,567) desaparece al controlar por terreno llano (0,494). "
                                 "Por análogos etiquetados, +0,15, no concluyente.", "PREREGISTRO_LLANURA.md"),
    ("moon", "geo"): Confidence("media", "Dirección correcta (+0,64) pero con 1 a 3 análogos por grupo; el p mínimo alcanzable es 0,25. "
                                "El proxy lunar (FeO) y la roca basáltica de la Tierra no miden lo mismo.", "VALIDACION_ASPECTO.md"),
    ("mars", "geo"): Confidence("media", "Dirección correcta (+0,97) pero descansa en un solo análogo (Craters of the Moon). "
                                "La geología de Marte satura en casi todo el planeta.", "VALIDACION_ASPECTO.md"),
    ("moon", "thermal"): Confidence("muy baja", "En contra (−0,48) con una sola referencia (Haughton, polar) frente a objetivos casi todos ecuatoriales. "
                                    "La térmica de la Tierra son medias mensuales, no el pico real.", "VALIDACION_ASPECTO.md"),
    ("mars", "thermal"): Confidence("sin datos", "Marte no tiene térmica en el modelo (decisión: no hay un mapa comparable).", "FUENTES.md"),
    ("moon", "ice"): Confidence("muy baja", "Solo 2 objetivos lunares (los polares) tienen dato de hielo y ningún análogo lleva esa etiqueta: no evaluable. "
                                "La nieve de la Tierra no equivale al hielo de agua de la Luna.", "VALIDACION_ASPECTO.md"),
    ("mars", "ice"): Confidence("muy baja", "Falla donde debía acertar (Valles Secos, −0,75): la nieve no mide sequedad. "
                                "La humedad del suelo (GLDAS) no mejora.", "PREREGISTRO_HIELO.md"),
}


def aspect_case(body: str, aspect: str, targets: list[str]) -> UseCase:
    w = {d: 1.0 if d == aspect else 0.0 for d in DIMENSIONS}
    return UseCase(f"atlas_{body}_{aspect}", f"{ASPECT_LABEL[aspect]} ({body})", body, targets, w, "", [])


def run(features_dir=FEATURES_DIR, n_regions: int = 5, n_cells: int = 40) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Devuelve (regiones, celdas): las n mejores regiones separadas y las n mejores celdas por (cuerpo, aspecto)."""
    earth = load_features("earth", features_dir)
    topo = fit_topo_model(earth)
    known = load_known()
    regions, cells = [], []
    for body in ("moon", "mars"):
        profiles = site_profiles(load_features(body, features_dir))
        k = known[known["analog_of"].fillna("").str.contains(body)]
        for aspect in DIMENSIONS:
            conf = CONFIDENCE[(body, aspect)]
            with_data = [s for s in profiles.index if _has_data(profiles.loc[s], aspect)]
            if not with_data:
                regions.append({"body": body, "aspect": aspect, "rank": 0, "confidence": conf.level, "why": conf.why, "n_targets": 0})
                continue
            s = score_use_case(aspect_case(body, aspect, with_data), earth, profiles, topo)
            s = s.merge(earth[[c for c in ("cell_id", "viable", "vegetated") if c in earth.columns]], on="cell_id", how="left")
            ok = s[s["viable"].fillna(True).astype(bool) & ~s["vegetated"].fillna(False).astype(bool)]
            if ok["score"].max() < MIN_USEFUL_SCORE:
                regions.append({"body": body, "aspect": aspect, "rank": 0, "confidence": conf.level, "n_targets": len(with_data),
                                "why": f"Ninguna celda de la Tierra supera {MIN_USEFUL_SCORE:.2f} de parecido en este aspecto (máximo {ok['score'].max():.3f}). " + conf.why})
                continue
            ok = ok[ok["score"] >= MIN_USEFUL_SCORE]
            for rank, (_, r) in enumerate(pick_regions(ok, n_regions).iterrows(), 1):
                d = haversine_km(r["lat"], r["lon"], k["lat"].to_numpy(), k["lon"].to_numpy())
                j = int(d.argmin())
                regions.append({"body": body, "aspect": aspect, "rank": rank, "cell_id": r["cell_id"], "lat": r["lat"], "lon": r["lon"],
                                "score": r["score"], "n_targets": len(with_data), "nearest_known": k["name"].iloc[j],
                                "nearest_known_km": float(d[j]), "confidence": conf.level, "why": conf.why})
            top = ok.sort_values("score", ascending=False).head(n_cells)
            cells.append(top[["cell_id", "lat", "lon", "score"]].assign(body=body, aspect=aspect))
    return pd.DataFrame(regions), pd.concat(cells, ignore_index=True)


def _has_data(profile: pd.Series, aspect: str) -> bool:
    return bool(profile[DIMENSIONS[aspect]].notna().any())


def main() -> None:
    regions, cells = run()
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    regions.to_csv(RESULTS_DIR / "atlas_regiones.csv", index=False)
    cells.to_csv(RESULTS_DIR / "atlas_celdas.csv", index=False)
    pd.set_option("display.width", 250)
    for (body, aspect), g in regions.groupby(["body", "aspect"], sort=False):
        print(f"\n== {body} · {ASPECT_LABEL[aspect]} · confianza {g['confidence'].iloc[0]} · {g['n_targets'].iloc[0]} objetivos con dato")
        if g["rank"].iloc[0] > 0:
            print(g[["rank", "cell_id", "lat", "lon", "score", "nearest_known", "nearest_known_km"]].round(2).to_string(index=False))


if __name__ == "__main__":
    main()
