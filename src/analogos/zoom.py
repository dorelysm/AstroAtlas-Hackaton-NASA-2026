"""Zoom a mayor resolución sobre una región candidata (el reto pide mirar a la escala de un campo volcánico, no de un desierto).

La malla global es de 5°; aquí se recalcula la topografía en una malla fina (por defecto 0.25° ~ 28 km) dentro de una caja, con las
MISMAS variables, ventana de 50 km y base de 500 m que la malla global, y se puntúa contra los objetivos de Marte (o la Luna).

LÍMITES: solo topografía. Térmica, hielo y geología no se recalculan: la geología (GLiM) es de 0.5° y no aporta a esta escala, y las
otras necesitarían descargar de nuevo los productos MODIS para las celdas nuevas. Por tanto el puntaje de este zoom es topográfico.

    python -m analogos.zoom --name harrat --lat 29 36 --lon 34 42
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
    """Puntaje topográfico de cada celda del zoom frente a cada objetivo del cuerpo; devuelve `score_mean` y `n_top10`.
    El modelo de PCA se ajusta con la malla GLOBAL (igual que en el resto del proyecto), no con el zoom."""
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
    print(f"{len(cells)} celdas de {a.step}° en {a.lat} x {a.lon}", flush=True)
    z = build_features(cells=cells, power=False, workers=8)  # descarta agua y celdas sin DEM
    z.to_parquet(FEATURES_WRITE_DIR / f"zoom_{a.name}.parquet", index=False)
    s = score_zoom(z, a.body)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    s.to_csv(RESULTS_DIR / f"zoom_{a.name}_{a.body}.csv", index=False)
    top = s.sort_values("score_mean", ascending=False).head(8)
    print(top[["cell_id", "lat", "lon", "score_mean", "score_max", "n_top10pct"]].round(2).to_string(index=False))
    print(f"\nscore_mean: media {s['score_mean'].mean():.2f}, máx {s['score_mean'].max():.2f}, mín {s['score_mean'].min():.2f}")


if __name__ == "__main__":
    main()
