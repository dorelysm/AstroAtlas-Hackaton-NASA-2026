"""Temperatura de SUPERFICIE de la Tierra (dimensión `thermal`) con MODIS LST mensual de la NASA.

Producto: MOD11C3 v061 (MODIS/Terra Land Surface Temperature/Emissivity Monthly L3 Global 0.05° CMG, LP DAAC).
~70 MB por mes; 12 meses ~840 MB. Por mes: bajar -> reducir a un valor por celda -> borrar (ver earth_water.py).

  - `thermal__t_max_k`   = máximo, entre los meses del año, de la LST diurna media mensual.
  - `thermal__t_range_k` = media, entre los meses, de (LST diurna - LST nocturna).
  - La temperatura del AIRE de POWER se conserva en `thermal_air_t_max_k` / `thermal_air_t_range_k` (diagnóstico).

LIMITACIÓN IMPORTANTE: son medias MENSUALES de la LST, no el pico instantáneo. La Luna (Diviner) da la
temperatura máxima real, así que la Tierra saldrá siempre más fría y esta dimensión no es comparable
en valor absoluto con la lunar (la amplitud diurna sí es más comparable). Ver docs/FUENTES.md.

    python -m analogos.data.earth_thermal --year 2019
"""
import argparse
import warnings

import numpy as np
import pandas as pd

from ..config import FEATURES_WRITE_DIR
from .earth_water import cell_windows, monthly_reduced, snow_grid, window_means

LST_SHORT = "MOD11C3"
DAY_VAR, NIGHT_VAR = "LST_Day_CMG", "LST_Night_CMG"
DEFAULT_SCALE, DEFAULT_MIN_DN = 0.02, 7500  # K por DN; DN válidos 7500-65535 (150 K en adelante); relleno = 0


def read_lst_hdf(path) -> tuple[np.ndarray, np.ndarray]:
    """(día, noche) en K con NaN donde no hay dato. Cierra el archivo (en Windows si no, no se puede borrar)."""
    from pyhdf.SD import SD, SDC

    sd = SD(str(path), SDC.READ)
    try:
        out = []
        for name in (DAY_VAR, NIGHT_VAR):
            ds = sd.select(name)
            at = ds.attributes()
            dn = ds.get().astype("float64")
            lo = at.get("valid_range", [DEFAULT_MIN_DN])[0]
            out.append(np.where(dn >= lo, dn * float(at.get("scale_factor", DEFAULT_SCALE)), np.nan))
        return out[0], out[1]
    finally:
        sd.end()


def lst_cell_values(day: np.ndarray, night: np.ndarray, windows: list) -> np.ndarray:
    """Vector [media diurna de cada celda..., media nocturna de cada celda...] en K."""
    return np.concatenate([window_means(day, windows), window_means(night, windows)])


def annual_thermal(monthly: np.ndarray) -> dict:
    """monthly = (meses, 2n) con día y noche concatenados -> t_max, rango diurno medio y diagnósticos."""
    n = monthly.shape[1] // 2
    day, night = monthly[:, :n], monthly[:, n:]
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        return {"t_max_k": np.nanmax(day, axis=0), "t_range_k": np.nanmean(day - night, axis=0),
                "night_min_k": np.nanmin(night, axis=0), "months_valid": np.isfinite(day).sum(axis=0)}


def apply_to_earth(earth: pd.DataFrame, th: dict) -> pd.DataFrame:
    """Sustituye la temperatura del aire (POWER) por la de superficie, guardando la primera en diagnóstico."""
    e = earth.copy()
    if "thermal_air_t_max_k" not in e:  # solo la primera vez (idempotente)
        e["thermal_air_t_max_k"] = e.get("thermal__t_max_k")
        e["thermal_air_t_range_k"] = e.get("thermal__t_range_k")
    e["thermal__t_max_k"] = th["t_max_k"]
    e["thermal__t_range_k"] = th["t_range_k"]
    e["thermal_lst_night_min_k"] = th["night_min_k"]
    e["thermal_lst_months_valid"] = th["months_valid"]
    return e


def run_lst(cells: pd.DataFrame, year: int) -> dict:
    lats, lons = snow_grid()  # MOD11C3 y MOD10CM comparten la rejilla CMG de 0.05° (3600 x 7200)
    windows = cell_windows(cells, lats, lons)

    def reduce_fn(path):
        day, night = read_lst_hdf(path)
        return lst_cell_values(day, night, windows)

    return annual_thermal(monthly_reduced(LST_SHORT, year, cells, reduce_fn, "lst"))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--year", type=int, default=2019)
    a = ap.parse_args()
    paths = [p for p in (FEATURES_WRITE_DIR / "earth.parquet", FEATURES_WRITE_DIR / "earth_sites.parquet") if p.exists()]
    tables = [pd.read_parquet(p) for p in paths]
    both = pd.concat([t[["lat", "lon"]] for t in tables], ignore_index=True)
    print(f"{len(both)} celdas ({', '.join(p.name for p in paths)}); año {a.year}")
    th = run_lst(both, a.year)
    start = 0
    for p, t in zip(paths, tables):
        sl = slice(start, start + len(t))
        start += len(t)
        apply_to_earth(t, {k: v[sl] for k, v in th.items()}).to_parquet(p, index=False)
        print(f"{p.name} actualizado")


if __name__ == "__main__":
    main()
