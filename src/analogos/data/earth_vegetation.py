"""Marca de VEGETACIÓN de la Tierra (solo diagnóstico, no es una feature del modelo) con NDVI mensual de MODIS.

Producto: MOD13C2 v061 (MODIS/Terra Vegetation Indices Monthly L3 Global 0.05° CMG, LP DAAC). ~170 MB por mes; por mes:
bajar -> reducir a un valor por celda -> borrar (ver earth_water.py).

Motivo: el modelo no tiene dimensión de biología/cobertura. Sin ella, selvas y bosques húmedos pueden salir como candidatos
"parecidos a Marte" solo porque no tienen nieve (la variable de hielo vale ~0 igual que en Marte). Se añade una MARCA, igual
que `viable`: no cambia el score ni la validación.

  - `veg_ndvi_mean`  = NDVI medio anual de la ventana de 50 km.
  - `veg_ndvi_max`   = NDVI máximo entre los meses.
  - `vegetated`      = veg_ndvi_max >= 0.2 (hay vegetación en algún mes: matorral o más; por debajo de 0.1 es roca, arena o hielo).
                       Sin dato de NDVI (hielo polar, noche polar) NO se marca como vegetada: ahí no se afirma nada.

    python -m analogos.data.earth_vegetation --year 2019
"""
import argparse
import warnings

import numpy as np
import pandas as pd

from ..config import FEATURES_WRITE_DIR
from .earth_water import cell_windows, monthly_reduced, snow_grid, window_means

NDVI_SHORT, NDVI_VAR = "MOD13C2", "CMG 0.05 Deg Monthly NDVI"
VEGETATED_NDVI_MAX = 0.2
COLUMNS = ["veg_ndvi_mean", "veg_ndvi_max", "vegetated"]


def read_ndvi_hdf(path) -> np.ndarray:
    """NDVI (-0.2 a 1) con NaN en el relleno. Cierra el archivo (en Windows si no, no se puede borrar)."""
    from pyhdf.SD import SD, SDC

    sd = SD(str(path), SDC.READ)
    try:
        ds = sd.select(NDVI_VAR)
        at = ds.attributes()
        dn = ds.get().astype("float64")
        lo, hi = at.get("valid_range", [-2000, 10000])
        return np.where((dn >= lo) & (dn <= hi), dn / float(at.get("scale_factor", 10000.0)), np.nan)
    finally:
        sd.end()


def annual_ndvi(monthly: np.ndarray) -> dict:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        return {"veg_ndvi_mean": np.nanmean(monthly, axis=0), "veg_ndvi_max": np.nanmax(monthly, axis=0)}


def add_vegetated(df: pd.DataFrame) -> pd.DataFrame:
    """`vegetated` = NDVI máximo anual >= 0.2. NDVI sin dato cuenta como NO vegetada (no se afirma nada)."""
    out = df.copy()
    out["vegetated"] = (out["veg_ndvi_max"] >= VEGETATED_NDVI_MAX).fillna(False).astype(bool)
    return out.drop(columns=[c for c in ("barren",) if c in out.columns])


def run_ndvi(cells: pd.DataFrame, year: int) -> dict:
    lats, lons = snow_grid()  # misma rejilla CMG de 0.05° (3600 x 7200)
    windows = cell_windows(cells, lats, lons)
    return annual_ndvi(monthly_reduced(NDVI_SHORT, year, cells, lambda p: window_means(read_ndvi_hdf(p), windows), "ndvi"))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--year", type=int, default=2019)
    a = ap.parse_args()
    names = ("earth.parquet", "earth_sites.parquet", "earth_usgs.parquet")
    paths = [FEATURES_WRITE_DIR / n for n in names if (FEATURES_WRITE_DIR / n).exists()]
    tables = [pd.read_parquet(p) for p in paths]
    both = pd.concat([t[["lat", "lon"]] for t in tables], ignore_index=True)
    print(f"{len(both)} celdas ({', '.join(p.name for p in paths)}); año {a.year}")
    nd = run_ndvi(both, a.year)
    start = 0
    for p, t in zip(paths, tables):
        for k, v in nd.items():
            t[k] = v[start:start + len(t)]
        start += len(t)
        t = add_vegetated(t)
        t.to_parquet(p, index=False)
        print(f"{p.name}: con vegetación (NDVI máx >= {VEGETATED_NDVI_MAX}): {int(t['vegetated'].sum())} de {len(t)}")


if __name__ == "__main__":
    main()
