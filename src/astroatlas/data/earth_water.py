"""Earth ice and water (`ice` dimension) from monthly NASA products, without keeping the rasters.

Flow per month: download one file -> reduce it to one value per grid cell -> delete the file.
Only a small vector per month remains on disk (data/raw/earthdata/reduced/), so repeating the run
downloads nothing again and the disk peak is one file.

  - MOD10CM (MODIS/Terra, NSIDC): monthly snow cover, 0.05°, ~1.2 MB/month. Feeds
    `ice__water_frac` (mean fraction of the year with snow). Verified with real data.
  - GLDAS_NOAH025_M v2.1 (GES DISC): soil moisture and snow water equivalent, 0.25°, ~24 MB/month.
    Diagnostic only (`ice_soil_moisture_m3m3`, `ice_swe_kg_m2`). Requires accepting the licence of
    "NASA GESDISC DATA ARCHIVE" in the Earthdata profile. NOT YET TESTED with real data.

    python -m astroatlas.data.earth_water --year 2019            # snow (12 months, ~15 MB)
    python -m astroatlas.data.earth_water --year 2019 --gldas    # + GLDAS (~280 MB, after approving the licence)

Semantics (see docs/reference/data-sources.md): snow is NOT subsurface ice. The Moon measures "fraction of area with stable
ice at <= 1 m" and Mars "% of water by mass"; they are not the same quantity.
"""
import argparse
import hashlib
import re
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

from ..config import FEATURES_WRITE_DIR, RAW_DIR
from ..validate import haversine_km
from . import edl

SNOW_SHORT, GLDAS_SHORT, GLDAS_VERSION = "MOD10CM", "GLDAS_NOAH025_M", "2.1"
WORKDIR = RAW_DIR / "earthdata"
REDUCED = WORKDIR / "reduced"
HALF_KM = 25.0
KM_PER_DEG = 111.195
SNOW_VAR = "Snow_Cover_Monthly_CMG"  # 0-100 valid; 211, 250, 254, 255 = polar night / ocean / no data
GLDAS_VARS = {"SoilMoi0_10cm_inst": ("ice_soil_moisture_m3m3", 1 / 100.0),  # kg/m2 in 10 cm -> m3/m3
              "SWE_inst": ("ice_swe_kg_m2", 1.0)}


# --------------------------------------------------------------------------- geometry (no network)
def window_indices(lats: np.ndarray, lons: np.ndarray, lat0: float, lon0: float, half_km: float = HALF_KM):
    """Indices (rows, columns) of the pixels of a regular grid within <= half_km of (lat0, lon0).

    If no pixel centre falls within the radius (grid coarser than the window), returns the nearest one.
    """
    lats, lons = np.asarray(lats, float), np.asarray(lons, float)
    step_lat, step_lon = abs(lats[1] - lats[0]), abs(lons[1] - lons[0])
    rows = np.nonzero(np.abs(lats - lat0) <= half_km / KM_PER_DEG + step_lat)[0]
    dlon = half_km / (KM_PER_DEG * max(np.cos(np.radians(lat0)), 1e-6)) + step_lon
    diff = (lons - lon0 + 180) % 360 - 180
    cols = np.nonzero(np.abs(diff) <= dlon)[0] if dlon < 180 else np.arange(len(lons))
    if rows.size == 0:
        rows = np.array([int(np.argmin(np.abs(lats - lat0)))])
    if cols.size == 0:
        cols = np.array([int(np.argmin(np.abs(diff)))])
    la, lo = np.meshgrid(lats[rows], lons[cols], indexing="ij")
    keep = haversine_km(lat0, lon0, la, lo) <= half_km
    if not keep.any():
        d = haversine_km(lat0, lon0, la, lo)
        i, j = np.unravel_index(np.argmin(d), d.shape)
        return rows[[i]], cols[[j]]
    ii, jj = np.nonzero(keep)
    return rows[ii], cols[jj]


def cell_windows(cells: pd.DataFrame, lats, lons, half_km: float = HALF_KM) -> list:
    return [window_indices(lats, lons, r.lat, r.lon, half_km) for r in cells.itertuples()]


def window_means(arr: np.ndarray, windows: list, valid: np.ndarray | None = None) -> np.ndarray:
    """Per-cell mean of the valid pixels of its window (NaN if none is valid)."""
    valid = np.isfinite(arr) if valid is None else valid
    out = np.full(len(windows), np.nan)
    for k, (ii, jj) in enumerate(windows):
        v = arr[ii, jj][valid[ii, jj]]
        if v.size:
            out[k] = float(v.mean())
    return out


# --------------------------------------------------------------------------- nieve (MOD10CM)
def snow_grid():
    return 90 - 0.05 * (np.arange(3600) + 0.5), -180 + 0.05 * (np.arange(7200) + 0.5)


def snow_cell_values(arr: np.ndarray, windows: list) -> np.ndarray:
    """Snow fraction (0-1) per cell from the monthly raster (codes > 100 = no data)."""
    a = np.asarray(arr, dtype="float64")
    return window_means(a, windows, valid=(a >= 0) & (a <= 100)) / 100.0


def read_snow_hdf(path: Path) -> np.ndarray:
    from pyhdf.SD import SD, SDC  # HDF4: rasterio's GDAL does not open it

    sd = SD(str(path), SDC.READ)
    try:
        return sd.select(SNOW_VAR).get()
    finally:
        sd.end()  # on Windows an open HDF4 file cannot be deleted


def annual_summary(monthly: np.ndarray) -> dict:
    """monthly = (months, cells) -> annual mean, monthly maximum and number of months with data."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        return {"mean": np.nanmean(monthly, axis=0), "max": np.nanmax(monthly, axis=0),
                "n_valid": np.isfinite(monthly).sum(axis=0)}


# --------------------------------------------------------------------------- descarga -> reducir -> borrar
def _key(cells: pd.DataFrame, half_km: float) -> str:
    raw = np.round(cells[["lat", "lon"]].to_numpy(), 6).tobytes() + str(half_km).encode()
    return hashlib.md5(raw).hexdigest()[:10]


def monthly_reduced(short_name: str, year: int, cells: pd.DataFrame, reduce_fn, tag: str,
                    version: str | None = None, half_km: float = HALF_KM) -> np.ndarray:
    """(months, cells) with `reduce_fn(path) -> vector per cell`. Each month: download, reduce, delete, and save the vector."""
    earthaccess = edl.login()
    kw = {"version": version} if version else {}
    granules = earthaccess.search_data(short_name=short_name, temporal=(f"{year}-01-01", f"{year}-12-31"),
                                       count=12, **kw)
    REDUCED.mkdir(parents=True, exist_ok=True)
    key, out, downloaded = _key(cells, half_km), [], 0.0
    for g in granules:
        title = g["meta"]["native-id"] if isinstance(g, dict) and "meta" in g else str(g)
        title = re.sub(r"[^A-Za-z0-9_.-]", "_", title)  # GLDAS has ':' in the name: invalid on Windows
        cache = REDUCED / f"{tag}_{title}_{key}.npy"
        if cache.exists():
            out.append(np.load(cache))
            continue
        path = Path(str(earthaccess.download([g], str(WORKDIR))[0]))
        downloaded += path.stat().st_size / 1e6
        try:
            vec = reduce_fn(path)
        finally:
            path.unlink(missing_ok=True)  # the raster is not kept
        np.save(cache, vec)
        out.append(vec)
        print(f"  {title}: reducido ({path.name} borrado)", flush=True)
    print(f"{tag}: {len(out)} months; downloaded in this run: {downloaded:.1f} MB")
    return np.vstack(out)


def run_snow(cells: pd.DataFrame, year: int) -> dict:
    lats, lons = snow_grid()
    windows = cell_windows(cells, lats, lons)
    monthly = monthly_reduced(SNOW_SHORT, year, cells, lambda p: snow_cell_values(read_snow_hdf(p), windows),
                              "snow")
    return annual_summary(monthly)


def run_gldas(cells: pd.DataFrame, year: int) -> dict[str, np.ndarray]:
    """Mean annual soil moisture and SWE. NOT YET TESTED with real data (needs approving the GESDISC licence)."""
    import netCDF4

    state = {}

    def reduce_fn(path: Path) -> np.ndarray:
        with netCDF4.Dataset(path) as ds:
            lats, lons = np.asarray(ds["lat"][:], float), np.asarray(ds["lon"][:], float)
            if "w" not in state:
                state["w"] = cell_windows(cells, lats, lons)
            vecs = []
            for var, (_, scale) in GLDAS_VARS.items():
                a = np.ma.filled(ds[var][0].astype("float64"), np.nan) * scale
                vecs.append(window_means(a, state["w"]))
            return np.concatenate(vecs)

    monthly = monthly_reduced(GLDAS_SHORT, year, cells, reduce_fn, "gldas", version=GLDAS_VERSION)
    n = len(cells)
    out = {}
    for k, (_, (col, _)) in enumerate(GLDAS_VARS.items()):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            out[col] = np.nanmean(monthly[:, k * n:(k + 1) * n], axis=0)
    return out


# --------------------------------------------------------------------------- aplicar a earth.parquet
def apply_to_earth(earth: pd.DataFrame, snow: dict, gldas: dict | None = None) -> pd.DataFrame:
    """Replaces `ice__water_frac` with the mean annual snow. Keeps the previous proxy in `ice_precip_proxy`."""
    e = earth.copy()
    if "ice_precip_proxy" not in e and "ice__water_frac" in e:  # first time: save the POWER proxy
        e["ice_precip_proxy"] = e["ice__water_frac"]
    e["ice__water_frac"] = snow["mean"]
    e["ice_snow_cover_max"] = snow["max"]
    e["ice_snow_months_valid"] = snow["n_valid"]
    for col, vec in (gldas or {}).items():
        e[col] = vec
    return e


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--year", type=int, default=2019)
    ap.add_argument("--gldas", action="store_true", help="add soil moisture and SWE (GLDAS)")
    a = ap.parse_args()
    paths = [p for p in (FEATURES_WRITE_DIR / "earth.parquet", FEATURES_WRITE_DIR / "earth_sites.parquet") if p.exists()]
    tables = [pd.read_parquet(p) for p in paths]
    both = pd.concat([t[["lat", "lon"]] for t in tables], ignore_index=True)  # a single reduction for everything
    print(f"{len(both)} celdas ({', '.join(p.name for p in paths)}); year {a.year}")
    snow = run_snow(both, a.year)
    gldas = run_gldas(both, a.year) if a.gldas else None
    start = 0
    for p, t in zip(paths, tables):
        sl = slice(start, start + len(t))
        start += len(t)
        part = lambda d: {k: v[sl] for k, v in d.items()}  # noqa: E731
        apply_to_earth(t, part(snow), part(gldas) if gldas else None).to_parquet(p, index=False)
        print(f"{p.name} actualizado")


if __name__ == "__main__":
    main()
