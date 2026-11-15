"""Earth data.

  - Topography (`topo__*`): Copernicus GLO-90 (ESA, AWS Open Data, no login), see copernicus.py.
  - Thermal and ice: POWER (AIR temperature and precipitation, PROXY; see docs/reference/nasa-apis.md).
  - CMR: granule search (MODIS LST, NASADEM...) for when there is an Earthdata login.
`geo__*` (NaN) and a SURFACE temperature (MODIS LST) are missing.

    python -m astroatlas.data.earth                  # 5° grid, dry land only
    python -m astroatlas.data.earth --step 10 --no-power
"""
import argparse
import math
import urllib.parse
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import pandas as pd

from ..config import FEATURES, FEATURES_WRITE_DIR, KNOWN_CSV
from ..grid import make_grid
from .copernicus import CopernicusDem
from .dem import site_topography
from .http import get_json

POWER_URL = "https://power.larc.nasa.gov/api/temporal/climatology/point"
POWER_PARAMS = "T2M_MAX,T2M_MIN,PRECTOTCORR"
CMR_URL = "https://cmr.earthdata.nasa.gov/search"
POWER_MISSING = -999.0
PRECIP_FULL_MM_DAY = 5.0  # at 5 mm/day or more, ice__water_frac = 1 (provisional proxy)
DIAGNOSTICS = ["elev_mean_m", "valid_frac", "baseline_m"]  # not model features


# --- POWER: climate per point ---
def power_url(lat: float, lon: float) -> str:
    q = {"parameters": POWER_PARAMS, "community": "RE", "latitude": lat, "longitude": lon, "format": "JSON"}
    return f"{POWER_URL}?{urllib.parse.urlencode(q)}"


def _val(params: dict, name: str) -> float:
    v = params.get(name, {}).get("ANN")
    return math.nan if v is None or v == POWER_MISSING else float(v)


def parse_power(payload: dict) -> dict:
    """POWER response -> contract features.

    NOTE: T2M is the AIR temperature at 2 m, not the surface temperature (Diviner/MODIS LST are).
    ANN of T2M_MAX/T2M_MIN is the extreme of the monthly means.
    """
    p = payload["properties"]["parameter"]
    tmax, tmin, precip = _val(p, "T2M_MAX"), _val(p, "T2M_MIN"), _val(p, "PRECTOTCORR")
    return {
        "thermal__t_max_k": tmax + 273.15,
        "thermal__t_range_k": tmax - tmin,
        "ice__water_frac": float(np.clip(precip / PRECIP_FULL_MM_DAY, 0, 1)) if not math.isnan(precip) else math.nan,
    }


def fetch_power_point(lat: float, lon: float) -> dict:
    return parse_power(get_json(power_url(lat, lon)))


def add_power(cells: pd.DataFrame, workers: int = 4) -> pd.DataFrame:
    def one(row):
        try:
            return fetch_power_point(row.lat, row.lon)
        except RuntimeError:  # point without data: NaN, not imputed
            return {}

    with ThreadPoolExecutor(max_workers=workers) as ex:
        results = list(ex.map(one, cells.itertuples()))
    vals = pd.DataFrame(results, index=cells.index).reindex(columns=["thermal__t_max_k", "thermal__t_range_k",
                                                                    "ice__water_frac"])
    return cells.assign(**{c: vals[c] for c in vals})


# --- Topography: Copernicus DEM ---
def build_topography(cells: pd.DataFrame, half_km: float = 25.0, baseline_m: float = 500.0,
                     workers: int = 8) -> pd.DataFrame:
    """topo__* features (+ diagnostics) for every cell. A cell that fails stays NaN and a warning is issued."""
    dem, failures = CopernicusDem(), []

    def one(row):
        try:
            return site_topography(dem, row.lat, row.lon, half_km, baseline_m)
        except Exception as e:  # noqa: BLE001  network, GDAL...: do not bring down the whole batch
            failures.append((row.cell_id, repr(e)))
            return {}

    with ThreadPoolExecutor(max_workers=workers) as ex:
        results = list(ex.map(one, cells.itertuples()))
    if failures:  # second pass, with fewer threads, only for the cells that failed (tiles already read are cached)
        print(f"{len(failures)} cells failed; retrying with 2 threads...")
        retry_ids = {cid for cid, _ in failures}
        failures.clear()
        todo = [(i, row) for i, row in enumerate(cells.itertuples()) if row.cell_id in retry_ids]
        with ThreadPoolExecutor(max_workers=2) as ex:
            for (i, _), res in zip(todo, ex.map(lambda t: one(t[1]), todo)):
                results[i] = res
    if failures:
        print(f"WARNING: {len(failures)} cells without topography because of an error, e.g. {failures[0]}")
    return pd.DataFrame(results, index=cells.index)


def is_flat_water(df: pd.DataFrame) -> pd.Series:
    """Cells whose window is WATER (sea, lakes, inland seas): Copernicus flattens bodies of water to a
    constant height, so without this filter they come out as 'perfect plains'. Criterion: local relief < 1 m at ANY
    altitude (it used to be only at ~0 m, which let lakes like Michigan or the Caspian through). With the 5° grid data,
    the flattest real flat terrain (Antarctic ice, plains, wetlands) has relief >= 4 m, so there is a margin."""
    return df["topo__relief_m"] < 1.0


is_flat_ocean = is_flat_water  # previous name, kept for compatibility


def build_features(step_deg: float = 5.0, workers: int = 8, topo: bool = True, power: bool = True,
                   min_valid: float = 0.5, cells: pd.DataFrame | None = None) -> pd.DataFrame:
    """Contract table for the Earth.

    With topo=True the cells with less than `min_valid` valid DEM are dropped (ocean, no tile).
    POWER is queried only for the cells that remain. `cells` allows passing custom points.
    """
    df = make_grid(step_deg, "earth") if cells is None else cells.copy()
    if topo:
        df = pd.concat([df, build_topography(df, workers=workers)], axis=1)
        df = df[(df["valid_frac"].fillna(0) >= min_valid) & ~is_flat_water(df)]
    if power:
        df = add_power(df, workers=min(workers, 4))  # POWER limits with 429: few connections
    for col in FEATURES:  # dimensions not yet extracted stay as NaN
        if col not in df:
            df[col] = np.nan
    return df.reset_index(drop=True)


def known_analog_cells(path=KNOWN_CSV) -> pd.DataFrame:
    k = pd.read_csv(path)
    return pd.DataFrame({"cell_id": [f"earth_known_{i}" for i in range(len(k))], "body": "earth",
                         "lat": k["lat"], "lon": k["lon"], "name": k["name"]})


def download() -> None:
    """Pending: MODIS LST with earthaccess (needs an Earthdata login)."""
    raise NotImplementedError


# --- CMR: locate datasets and granules (no login to search) ---
def cmr_collections(short_name: str, page_size: int = 5) -> list[dict]:
    q = urllib.parse.urlencode({"short_name": short_name, "page_size": page_size})
    entries = get_json(f"{CMR_URL}/collections.json?{q}")["feed"]["entry"]
    return [{"entry_id": e["entry_id"], "title": e["dataset_id"], "cloud_hosted": e.get("cloud_hosted")} for e in entries]


def cmr_granules(short_name: str, bbox: tuple[float, float, float, float], page_size: int = 5) -> list[dict]:
    """bbox = (west, south, east, north). Returns the title and download links of every granule."""
    q = urllib.parse.urlencode(
        {"short_name": short_name, "bounding_box": ",".join(map(str, bbox)), "page_size": page_size}
    )
    entries = get_json(f"{CMR_URL}/granules.json?{q}")["feed"]["entry"]
    return [
        {"title": e["title"], "links": [l["href"] for l in e.get("links", []) if "data#" in l.get("rel", "")]}
        for e in entries
    ]


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--step", type=float, default=5.0, help="grid step in degrees")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--no-topo", action="store_true")
    ap.add_argument("--no-power", action="store_true")
    ap.add_argument("--no-sites", action="store_true", help="do not compute the known analogs")
    a = ap.parse_args()
    FEATURES_WRITE_DIR.mkdir(parents=True, exist_ok=True)

    out = build_features(a.step, a.workers, topo=not a.no_topo, power=not a.no_power)
    out.to_parquet(FEATURES_WRITE_DIR / "earth.parquet", index=False)
    print(f"earth.parquet: {len(out)} celdas (malla {a.step}°)")

    if not a.no_sites:  # known analogs: ONLY to compare/validate, never mixed with the grid
        sites = build_features(cells=known_analog_cells(), workers=a.workers, topo=not a.no_topo,
                               power=not a.no_power, min_valid=0.0)
        sites.to_parquet(FEATURES_WRITE_DIR / "earth_sites.parquet", index=False)
        print(f"earth_sites.parquet: {len(sites)} known analogs")
