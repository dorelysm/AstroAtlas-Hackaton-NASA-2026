"""Higher-resolution zoom over a candidate region (the challenge asks to look at the scale of a volcanic field, not of a desert).

The global grid is 5°; here the topography is recomputed on a fine grid (by default 0.25° ~ 28 km) inside a box, with the
SAME variables, 50 km window and 500 m baseline as the global grid, and scored against the Mars (or Moon) targets.

LIMITS: topography only. Thermal, ice and geology are not recomputed: the geology (GLiM) is 0.5° and adds nothing at this scale, and the
others would need re-downloading the MODIS products for the new cells. The score of this zoom is therefore topographic.

    python -m astroatlas.zoom --name harrat --lat 29 36 --lon 34 42
"""
import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from .config import FEATURES_DIR, FEATURES_WRITE_DIR, RESULTS_DIR
from .data.earth import build_features
from .features import load_features
from .similarity import fit_topo_model, rank_cells, site_profiles


def region_grid(lat: tuple[float, float], lon: tuple[float, float], step: float, name: str) -> pd.DataFrame:
    lats = np.arange(lat[0] + step / 2, lat[1], step)
    lons = np.arange(lon[0] + step / 2, lon[1], step)
    la, lo = np.meshgrid(lats, lons, indexing="ij")
    ids = [f"zoom_{name}_{i}_{j}" for i in range(len(lats)) for j in range(len(lons))]
    return pd.DataFrame({"cell_id": ids, "body": "earth", "lat": la.ravel(), "lon": lo.ravel()})


def score_zoom(zoom: pd.DataFrame, body: str = "mars", features_dir: Path = FEATURES_DIR) -> pd.DataFrame:
    """Topographic score of each zoom cell against each target of the body; returns `score_mean` and `n_top10`.
    The PCA model is fitted with the GLOBAL grid (like in the rest of the project), not with the zoom."""
    earth = load_features("earth", features_dir)
    topo = fit_topo_model(earth)
    w = {"topo": 1.0, "thermal": 0.0, "ice": 0.0, "geo": 0.0}
    cols = {}
    for site, profile in site_profiles(load_features(body, features_dir)).iterrows():
        r = rank_cells(zoom, profile, w, topo).set_index("cell_id")["score"]
        cols[site] = r
    m = pd.DataFrame(cols)
    out = zoom.set_index("cell_id").join(pd.DataFrame({"score_mean": m.mean(axis=1), "score_max": m.max(axis=1),
                                                       "n_top10pct": (m.rank(pct=True, ascending=False) <= 0.10).sum(axis=1)}))
    return out.reset_index()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", required=True)
    ap.add_argument("--lat", type=float, nargs=2, required=True)
    ap.add_argument("--lon", type=float, nargs=2, required=True)
    ap.add_argument("--step", type=float, default=0.25)
    ap.add_argument("--body", default="mars")
    a = ap.parse_args()
    cells = region_grid(tuple(a.lat), tuple(a.lon), a.step, a.name)
    print(f"{len(cells)} cells of {a.step}° at {a.lat} x {a.lon}", flush=True)
    z = build_features(cells=cells, power=False, workers=8)  # drops water and cells without DEM
    z.to_parquet(FEATURES_WRITE_DIR / f"zoom_{a.name}.parquet", index=False)
    s = score_zoom(z, a.body)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    s.to_csv(RESULTS_DIR / f"zoom_{a.name}_{a.body}.csv", index=False)
    top = s.sort_values("score_mean", ascending=False).head(8)
    print(top[["cell_id", "lat", "lon", "score_mean", "score_max", "n_top10pct"]].round(2).to_string(index=False))
    print(f"\nscore_mean: media {s['score_mean'].mean():.2f}, max {s['score_mean'].max():.2f}, min {s['score_mean'].min():.2f}")


if __name__ == "__main__":
    main()
