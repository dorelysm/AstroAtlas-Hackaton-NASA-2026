"""Earth VEGETATION flag (diagnostic only, not a model feature) from monthly MODIS NDVI.

Product: MOD13C2 v061 (MODIS/Terra Vegetation Indices Monthly L3 Global 0.05° CMG, LP DAAC). ~170 MB per month; per month:
download -> reduce to one value per cell -> delete (see earth_water.py).

Reason: the model has no biology/land-cover dimension. Without it, rainforests and humid forests can come out as candidates
"similar to Mars" just because they have no snow (the ice variable is ~0, same as on Mars). A FLAG is added, like
`viable`: it changes neither the score nor the validation.

  - `veg_ndvi_mean`  = mean annual NDVI of the 50 km window.
  - `veg_ndvi_max`   = maximum NDVI across the months.
  - `vegetated`      = veg_ndvi_max >= 0.2 (there is vegetation in some month: shrub or more; below 0.1 it is rock, sand or ice).
                       Without NDVI data (polar ice, polar night) it is NOT flagged as vegetated: nothing is asserted there.

    python -m astroatlas.data.earth_vegetation --year 2019
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
    """NDVI (-0.2 to 1) with NaN in the fill. Closes the file (on Windows otherwise it cannot be deleted)."""
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
    """`vegetated` = maximum annual NDVI >= 0.2. NDVI without data counts as NOT vegetated (nothing is asserted)."""
    out = df.copy()
    out["vegetated"] = (out["veg_ndvi_max"] >= VEGETATED_NDVI_MAX).fillna(False).astype(bool)
    return out.drop(columns=[c for c in ("barren",) if c in out.columns])


def run_ndvi(cells: pd.DataFrame, year: int) -> dict:
    lats, lons = snow_grid()  # same 0.05° CMG grid (3600 x 7200)
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
    print(f"{len(both)} celdas ({', '.join(p.name for p in paths)}); year {a.year}")
    nd = run_ndvi(both, a.year)
    start = 0
    for p, t in zip(paths, tables):
        for k, v in nd.items():
            t[k] = v[start:start + len(t)]
        start += len(t)
        t = add_vegetated(t)
        t.to_parquet(p, index=False)
        print(f"{p.name}: with vegetation (max NDVI >= {VEGETATED_NDVI_MAX}): {int(t['vegetated'].sum())} of {len(t)}")


if __name__ == "__main__":
    main()
