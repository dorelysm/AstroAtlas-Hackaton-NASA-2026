"""Polvo y viento de la Tierra (SOLO CONTEXTO DESCRIPTIVO; no es una feature del modelo) con MERRA-2 mensual de la NASA.

Productos (GES DISC; exigen la licencia GESDISC aceptada en Earthdata):
  - M2TMNXAER v5.12.4: polvo (DUSMASS = concentración en superficie, DUCMASS = columna).
  - M2TMNXSLV v5.12.4: viento a 10 m (U10M, V10M).
~80 MB por mes y producto; por mes: bajar -> reducir -> borrar (ver earth_water.py).

Columnas (diagnóstico, en earth*.parquet):
  - `dust_surface_ugm3`   = concentración de polvo en superficie media anual (µg/m3).
  - `dust_column_mgm2`    = columna de polvo media anual (mg/m2).
  - `wind10m_ms`          = media anual de la velocidad del viento mensual medio a 10 m (m/s; subestima ráfagas y la media de la rapidez).

POR QUÉ SOLO CONTEXTO: no hay contraparte comparable en Luna (sin atmósfera) ni, con los datos usados, en Marte (haría falta la
opacidad de polvo de MCS/TES y el viento de modelos), así que no se puede puntuar similitud. Sirve para describir en las fichas
si un candidato es polvoriento o ventoso. La rejilla (0.5° x 0.625°) es más gruesa que la ventana de 50 km: se toma la celda
de MERRA-2 que contiene el centro de la celda, no una media de ventana.

    python -m analogos.data.earth_dust_wind --year 2019
"""
import argparse
import warnings

import numpy as np
import pandas as pd

from ..config import FEATURES_WRITE_DIR
from .earth_water import monthly_reduced

VERSION = "5.12.4"
COLUMNS = ["dust_surface_ugm3", "dust_column_mgm2", "wind10m_ms"]


def nearest_index(centers: np.ndarray, values: np.ndarray, period: float | None = None) -> np.ndarray:
    """Índice de la rejilla más cercano a cada valor; con `period` (longitud, 360) la distancia es circular."""
    d = np.abs(centers[None, :] - values[:, None])
    if period:
        d = np.minimum(d, period - d)
    return d.argmin(axis=1)


def sample(arr: np.ndarray, lats, lons, cells: pd.DataFrame) -> np.ndarray:
    ii = nearest_index(np.asarray(lats, float), cells["lat"].to_numpy(float))
    jj = nearest_index(np.asarray(lons, float), cells["lon"].to_numpy(float), period=360.0)
    return arr[ii, jj]


def _read(path, names: list[str]):
    import netCDF4

    with netCDF4.Dataset(path) as ds:
        lats, lons = np.asarray(ds["lat"][:], float), np.asarray(ds["lon"][:], float)
        arrs = [np.ma.filled(ds[n][0].astype("float64"), np.nan) for n in names]
    return lats, lons, arrs


def run(cells: pd.DataFrame, year: int) -> dict[str, np.ndarray]:
    n = len(cells)

    def dust_fn(path):
        lats, lons, (surf, col) = _read(path, ["DUSMASS", "DUCMASS"])
        return np.concatenate([sample(surf * 1e9, lats, lons, cells), sample(col * 1e6, lats, lons, cells)])  # kg/m3->ug/m3; kg/m2->mg/m2

    def wind_fn(path):
        lats, lons, (u, v) = _read(path, ["U10M", "V10M"])
        return sample(np.hypot(u, v), lats, lons, cells)

    dust = monthly_reduced("M2TMNXAER", year, cells, dust_fn, "m2dust", version=VERSION)
    wind = monthly_reduced("M2TMNXSLV", year, cells, wind_fn, "m2wind", version=VERSION)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        return {"dust_surface_ugm3": np.nanmean(dust[:, :n], axis=0), "dust_column_mgm2": np.nanmean(dust[:, n:], axis=0),
                "wind10m_ms": np.nanmean(wind, axis=0)}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--year", type=int, default=2019)
    a = ap.parse_args()
    names = ("earth.parquet", "earth_sites.parquet", "earth_usgs.parquet")
    paths = [FEATURES_WRITE_DIR / nm for nm in names if (FEATURES_WRITE_DIR / nm).exists()]
    tables = [pd.read_parquet(p) for p in paths]
    both = pd.concat([t[["lat", "lon"]] for t in tables], ignore_index=True)
    print(f"{len(both)} celdas ({', '.join(p.name for p in paths)}); año {a.year}", flush=True)
    res = run(both, a.year)
    start = 0
    for p, t in zip(paths, tables):
        for k, v in res.items():
            t[k] = v[start:start + len(t)]
        start += len(t)
        t.to_parquet(p, index=False)
        print(f"{p.name}: " + ", ".join(f"{k} media {t[k].mean():.2f}" for k in res), flush=True)


if __name__ == "__main__":
    main()
