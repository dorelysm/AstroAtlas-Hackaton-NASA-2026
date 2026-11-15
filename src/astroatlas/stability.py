"""Stability of the predictions: which cells stay among the best when the model's arbitrary decisions are perturbed?

In each replicate the following are perturbed: (1) the weights per dimension (uniform Dirichlet), (2) the Earth sample used to standardise
and fit the topography PCA (cell bootstrap) and (3) the variance the PCA must explain (80 to 95 %). The mean score of each cell over all the
body's targets is recomputed and it is recorded whether it stays in the best 5 % of viable, non-vegetated cells.
Result: `freq_top5` = fraction of replicates in which the cell is among the best. Near 1 = robust; near 0 = depends on one choice.

It does not use the known analogs: it only measures how much the candidate cells depend on decisions that are not backed by data.

    python -m astroatlas.stability
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
        print(f"\n== {body}: most stable cells (of {int(r['viable_unvegetated'].sum())} viable and non-vegetated)")
        print(top[["cell_id", "lat", "lon", "freq_top5", "mean_rank_pct"]].round(2).to_string(index=False))
        cand = r[r["cell_id"].isin(["earth_24_43", "earth_23_39"])]
        print(cand[["cell_id", "lat", "lon", "freq_top5", "mean_rank_pct"]].round(2).to_string(index=False))
    pd.concat(res).to_csv(a.out / "stability.csv", index=False)


if __name__ == "__main__":
    main()
