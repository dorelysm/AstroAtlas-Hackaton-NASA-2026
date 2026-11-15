"""Estabilidad de las predicciones: ¿qué celdas siguen entre las mejores cuando se perturban las decisiones arbitrarias del modelo?

En cada réplica se perturban (1) los pesos por dimensión (Dirichlet uniforme), (2) la muestra de la Tierra con la que se estandariza
y se ajusta la PCA de la topografía (bootstrap de celdas) y (3) la varianza que debe explicar la PCA (80 a 95 %). Se recalcula el
puntaje medio de cada celda sobre todos los objetivos del cuerpo y se anota si queda en el 5 % mejor de las celdas viables y sin vegetación.
Resultado: `freq_top5` = fracción de réplicas en las que la celda está entre las mejores. Cerca de 1 = robusta; cerca de 0 = depende de una elección.

No usa los análogos conocidos: solo mide cuánto dependen las celdas candidatas de decisiones que no están respaldadas por datos.

    python -m analogos.stability
"""
import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from .config import DIMENSIONS, FEATURES_DIR, RESULTS_DIR
from .features import load_features
from .similarity import fit_topo_model, score_cells, site_profiles


def run(body: str, n_rep: int = 200, seed: int = 0, features_dir: Path = FEATURES_DIR, top_frac: float = 0.05) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    earth = load_features("earth", features_dir)
    ok = earth["viable"].fillna(True).astype(bool) & ~earth["vegetated"].fillna(False).astype(bool) if "viable" in earth else \
        pd.Series(True, index=earth.index)
    profiles = site_profiles(load_features(body, features_dir))
    dims = list(DIMENSIONS)
    n_top = max(1, int(round(top_frac * int(ok.sum()))))
    hits, rank_sum = np.zeros(len(earth)), np.zeros(len(earth))
    for _ in range(n_rep):
        w = dict(zip(dims, rng.dirichlet(np.ones(len(dims)))))
        boot = earth.iloc[rng.integers(0, len(earth), len(earth))]
        topo = fit_topo_model(boot, variance=float(rng.uniform(0.80, 0.95)))
        scores = np.column_stack([score_cells(earth, p, w, topo, ref=boot)["score"].to_numpy() for _, p in profiles.iterrows()])
        mean = pd.Series(np.nanmean(scores, axis=1), index=earth.index).where(ok)
        rank = mean.rank(ascending=False, method="min")
        hits += (rank <= n_top).to_numpy()
        rank_sum += (rank / ok.sum()).fillna(1.0).to_numpy()
    out = earth[["cell_id", "lat", "lon"]].copy()
    out["freq_top5"] = hits / n_rep
    out["mean_rank_pct"] = rank_sum / n_rep
    return out.assign(body=body, viable_unvegetated=ok.to_numpy())


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=200)
    ap.add_argument("--out", type=Path, default=RESULTS_DIR)
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    pd.set_option("display.width", 200)
    res = []
    for body in ("mars", "moon"):
        r = run(body, a.reps)
        res.append(r)
        top = r[r["viable_unvegetated"]].sort_values("freq_top5", ascending=False).head(8)
        print(f"\n== {body}: celdas más estables (de {int(r['viable_unvegetated'].sum())} viables y sin vegetación)")
        print(top[["cell_id", "lat", "lon", "freq_top5", "mean_rank_pct"]].round(2).to_string(index=False))
        cand = r[r["cell_id"].isin(["earth_24_43", "earth_23_39"])]
        print(cand[["cell_id", "lat", "lon", "freq_top5", "mean_rank_pct"]].round(2).to_string(index=False))
    pd.concat(res).to_csv(a.out / "stability.csv", index=False)


if __name__ == "__main__":
    main()
