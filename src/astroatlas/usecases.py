"""Profiles per use case: instead of a single ranking, which places on Earth are useful for each TYPE of use.

Each use case fixes (1) the targets it is compared with, (2) the weights per dimension and (3) a text saying what can and cannot
be claimed. A cell's score is the mean, over the case's targets, of its similarity to the profile of each one.

SCALE LIMIT (important): the model variables are from the common 500 m grid and 50 km windows. The published
engineering thresholds (landing slope, rock abundance, rover tilt) are defined at scales of metres
and 2-5 km, so they CANNOT be applied as absolute thresholds to this data. That is why no thresholds are used here: the comparison is
with the terrain of sites where a landing or a drive has already happened, which is a relative measure. The literature thresholds are
in docs/results/use-cases.md only as context.

    python -m astroatlas.usecases
"""
from dataclasses import dataclass, field

import pandas as pd

from .config import FEATURES_DIR, RESULTS_DIR
from .features import load_features
from .similarity import fit_topo_model, rank_cells, site_profiles
from .validate import haversine_km, load_known


@dataclass
class UseCase:
    key: str
    title: str
    body: str
    targets: list[str]
    weights: dict[str, float]
    note: str
    caveats: list[str] = field(default_factory=list)


_W0 = {"topo": 0.0, "thermal": 0.0, "ice": 0.0, "geo": 0.0}

USE_CASES: list[UseCase] = [
    UseCase("movilidad_marte", "Probar movilidad y aterrizaje (Marte)", "mars",
            ["Jezero", "Oxia Planum", "Viking 1", "Viking 2", "Mars Pathfinder", "Spirit (MER-A)", "Opportunity (MER-B)",
             "Curiosity (MSL Gale)", "InSight", "Eberswalde (candidato MSL)", "Holden (candidato MSL)", "Mawrth Vallis (candidato MSL)"],
            _W0 | {"topo": 1.0},
            "Terreno parecido al de los sitios donde ya se aterrizó o se condujo en Marte (solo topografía a 500 m).",
            ["No son umbrales de aterrizaje: a 500 m no se ven rocas ni pendientes de metros.",
             "La topografía a esta escala no distingue bien un cráter de una llanura estable (ver preregistrations/plains.md)."]),
    UseCase("movilidad_luna", "Probar movilidad y aterrizaje (Luna)", "moon",
            ["Apollo 11 LM", "Apollo 12 LM", "Apollo 14 LM", "Apollo 15 LM", "Apollo 16 LM", "Apollo 17 LM", "Surveyor 1", "Surveyor 5",
             "Surveyor 6", "Surveyor 7", "Luna 16", "Luna 17", "Luna 20", "Luna 21", "Luna 23", "Chang'e 3", "Chang'e 4", "Chang'e 6"],
            _W0 | {"topo": 1.0},
            "Terreno parecido al de los sitios de aterrizaje lunares (solo topografía a 500 m).",
            ["Las celdas que salen primero suelen ser superficies muy llanas (hielo antártico) que no se parecen a la Luna en nada más."]),
    UseCase("frio_luna_polar", "Operaciones en frío en los polos lunares", "moon", ["Shackleton rim", "Malapert massif"],
            _W0 | {"topo": 0.5, "thermal": 1.0, "ice": 0.5},
            "Parecido en temperatura máxima mensual y rango térmico, con algo de topografía y nieve.",
            ["La térmica de la Tierra son medias mensuales (MODIS), no el pico real: nunca llega a lo frío de una zona sombreada (< 100 K).",
             "La 'nieve' terrestre no equivale al hielo de agua lunar: peso reducido."]),
    UseCase("hielo_marte_polar", "Hielo y permafrost en el norte de Marte", "mars", ["Arcadia Planitia", "Phoenix"],
            _W0 | {"topo": 0.5, "ice": 1.0},
            "Parecido en el hielo medido (nieve en la Tierra, agua en el suelo según Odyssey GRS en Marte) y algo de topografía.",
            ["Es el caso más débil: la nieve de la Tierra falla justo donde debía acertar (Valles Secos). Marte no tiene térmica en el modelo."]),
    UseCase("basalto_marte", "Terreno basáltico (Marte)", "mars", ["Jezero", "Oxia Planum", "Viking 1", "Viking 2", "Mars Pathfinder",
                                                               "Spirit (MER-A)", "Opportunity (MER-B)", "Curiosity (MSL Gale)", "InSight"],
            _W0 | {"geo": 1.0, "topo": 0.5},
            "Campos basálticos con topografía moderadamente parecida. Es donde coinciden las candidatas de las fichas.",
            ["La geología de Marte (hierro de Odyssey GRS) satura en casi todo el planeta: discrimina poco.",
             "La fracción de basalto de la Tierra (roca en superficie, GLiM) no mide lo mismo que el proxy de hierro de Marte."]),
    UseCase("volcanico_luna", "Terreno volcánico y tubos de lava (Luna)", "moon",
            ["Mare Tranquillitatis pit", "Apollo 12 LM", "Apollo 15 LM", "Apollo 17 LM", "Surveyor 1", "Luna 16", "Luna 17", "Chang'e 3"],
            _W0 | {"geo": 1.0, "topo": 0.5},
            "Basalto de mar lunar (proxy de FeO) con topografía parecida; relevante para pits y tubos de lava.",
            ["Solo 1 de los 21 objetivos lunares tiene un pit cerca (docs/context/caves-and-lava-tubes.md): el modelo no ve los tubos, solo el terreno basáltico.",
             "El proxy lunar (FeO) y la fracción de basalto de la Tierra no miden lo mismo."]),
]


def score_use_case(uc: UseCase, earth: pd.DataFrame, target_profiles: pd.DataFrame, topo_model) -> pd.DataFrame:
    prof = target_profiles.loc[[t for t in uc.targets if t in target_profiles.index]]
    if prof.empty:
        raise ValueError(f"{uc.key}: ningún objetivo existe")
    cols = {site: rank_cells(earth, p, uc.weights, topo_model).set_index("cell_id")["score"] for site, p in prof.iterrows()}
    m = pd.DataFrame(cols)
    out = earth[["cell_id", "lat", "lon"]].set_index("cell_id").join(pd.DataFrame({
        "score": m.mean(axis=1), "n_targets": m.notna().sum(axis=1)}))
    return out.reset_index().dropna(subset=["score"])


def pick_regions(scored: pd.DataFrame, n: int = 3, min_sep_km: float = 500.0) -> pd.DataFrame:
    """The n best cells separated by at least min_sep_km (so three neighbouring cells do not come out)."""
    chosen = []
    for _, r in scored.sort_values("score", ascending=False).iterrows():
        if all(haversine_km(r["lat"], r["lon"], c["lat"], c["lon"]) >= min_sep_km for c in chosen):
            chosen.append(r)
        if len(chosen) == n:
            break
    return pd.DataFrame(chosen)


def run(features_dir=FEATURES_DIR, n: int = 3) -> pd.DataFrame:
    earth = load_features("earth", features_dir)
    topo = fit_topo_model(earth)
    known = load_known()
    profiles = {b: site_profiles(load_features(b, features_dir)) for b in ("moon", "mars")}
    rows = []
    for uc in USE_CASES:
        s = score_use_case(uc, earth, profiles[uc.body], topo)
        s = s.merge(earth[[c for c in ("cell_id", "viable", "vegetated", "dist_settlement_km", "veg_ndvi_max") if c in earth.columns]],
                    on="cell_id", how="left")
        s_ok = s[s["viable"].fillna(True).astype(bool) & ~s["vegetated"].fillna(False).astype(bool)]
        top = pick_regions(s_ok, n)
        k = known[known["analog_of"].fillna("").str.contains(uc.body)]
        for rank, (_, r) in enumerate(top.iterrows(), 1):
            d = haversine_km(r["lat"], r["lon"], k["lat"].to_numpy(), k["lon"].to_numpy())
            j = int(d.argmin())
            rows.append({"use_case": uc.key, "title": uc.title, "rank": rank, "cell_id": r["cell_id"], "lat": r["lat"], "lon": r["lon"],
                         "score": r["score"], "n_targets": int(r["n_targets"]), "nearest_known": k["name"].iloc[j],
                         "nearest_known_km": float(d[j]), "dist_settlement_km": r.get("dist_settlement_km"),
                         "ndvi_max": r.get("veg_ndvi_max")})
    return pd.DataFrame(rows)


def main() -> None:
    res = run()
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    res.to_csv(RESULTS_DIR / "usecases.csv", index=False)
    pd.set_option("display.width", 250)
    for key, g in res.groupby("use_case", sort=False):
        print(f"\n== {g['title'].iloc[0]}")
        print(g[["rank", "cell_id", "lat", "lon", "score", "n_targets", "nearest_known", "nearest_known_km"]].round(2).to_string(index=False))


if __name__ == "__main__":
    main()
