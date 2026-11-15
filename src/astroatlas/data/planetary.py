"""Thermal, ice and geo dimensions of the Moon and Mars, ONLY with NASA PDS data (Geosciences Node).

Each function takes (lat, lon 0..360 E) and returns the contract columns + diagnostics.
Window: cells whose centre is within <= `HALF_KM` of the site (the same 50 x 50 km window as the topography);
if the product is coarser than that, the nearest cell.

| Variable            | Moon                                             | Mars                                   |
|---------------------|--------------------------------------------------|----------------------------------------|
| thermal__t_max_k    | LRO Diviner GCP, tbol (Williams et al. 2017)     | NO DATA: no map in the PDS             |
| thermal__t_range_k  | same, max - min of the diurnal curve             | NO DATA                                |
| ice__water_frac     | Diviner PRP (Paige et al. 2010): fraction of     | Mars Odyssey GRS H2O (% by mass / 100) |
|                     | area with stable ice at <= 1 m (only > 80° S)    | no data above ~45°                     |
| geo__basalt_frac    | Lunar Prospector GRS FeO -> linear proxy         | Mars Odyssey GRS Fe -> same proxy      |

Basalt proxy (ours, not from the PDS): (FeO % - 5) / 15, clipped to 0-1
(lunar highlands ~5 % FeO, basaltic maria ~20 %).
Downloads: data/raw/pds/ (Diviner PRP south ~600 MB and GCP 80-90° S ~156 MB only if there are polar sites).
Sources and confidence levels: docs/reference/data-sources.md.
"""
import io
import math
import shutil
import time
import urllib.request

import numpy as np
import pandas as pd

from ..config import RAW_DIR

PDS = "https://pds-geosciences.wustl.edu"
DIVINER = f"{PDS}/lro/urn-nasa-pds-lro_diviner_derived1"
GCP_URL = f"{DIVINER}/data_derived_gcp/"
PRP_URL = f"{DIVINER}/data_derived_prp/dlre_prp_south.tab"
LPGRS_URL = f"{PDS}/lunar/lp-l-grs-5-elem-abundance-v1/lp_9001/data/lpgrs_high1_elem_abundance_2deg.tab"
ODY_URL = f"{PDS}/ody/ody-m-grs-5-elements-v1/odgm_xxxx/data/smoothed/"
CACHE = RAW_DIR / "pds"
R_MOON_KM, R_MARS_KM = 1737.4, 3389.5
HALF_KM = 25.0
FEO_HIGHLANDS, FEO_MARE = 5.0, 20.0
NO_ICE_DATA_NOTE = "outside the Diviner PRP coverage (> 80° S): no data (NaN)"
NO_MARS_ICE_NOTE = ("no data in this Odyssey GRS cell (the product does not cover beyond ±57.5° "
                    "and has gaps between 45° and 60°)")

# ---------------------------------------------------------------- utilities


def _lon180(lon):
    return (np.asarray(lon, dtype="float64") + 180) % 360 - 180


def _gc_km(lat1, lon1, lat2, lon2, r_km):
    p1, p2 = np.radians(lat1), np.radians(lat2)
    dl = np.radians(np.asarray(lon2) - lon1)
    a = np.sin((p2 - p1) / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(dl / 2) ** 2
    return 2 * r_km * np.arcsin(np.sqrt(np.clip(a, 0, 1)))


def _get(url: str, rng: tuple[int, int] | None = None) -> bytes:
    headers = {"Range": f"bytes={rng[0]}-{rng[1]}"} if rng else {}
    for attempt in range(5):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=600) as r:
                return r.read()
        except OSError:
            if attempt == 4:
                raise
            time.sleep(2 * (attempt + 1))


def _download(url: str):
    """Downloads the whole file once to data/raw/pds/ and returns the local path."""
    path = CACHE / url.rsplit("/", 1)[1]
    if not path.exists():
        CACHE.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(path.suffix + ".part")
        print(f"descargando {url} ...", flush=True)
        for attempt in range(5):
            try:
                with urllib.request.urlopen(url, timeout=600) as r, open(tmp, "wb") as fh:
                    shutil.copyfileobj(r, fh, 1 << 20)
                break
            except OSError:
                if attempt == 4:
                    raise
                time.sleep(5 * (attempt + 1))
        tmp.rename(path)
    return path


def _basalt(feo_pct: float) -> float:
    if not np.isfinite(feo_pct):
        return np.nan
    return float(np.clip((feo_pct - FEO_HIGHLANDS) / (FEO_MARE - FEO_HIGHLANDS), 0, 1))

# ---------------------------------------------------------------- Luna


GCP_COLS = ["clon", "clat", "ltim", "t3", "t4", "t5", "t6", "t7", "t8", "t9", "tbol"]
GCP_ROW = 113  # bytes per row; order: longitude (720) > latitude (20 per strip) > local time (96)


def _gcp_file(lat: float) -> tuple[str, int]:
    lo = min(math.floor(lat / 10) * 10, 80)
    name = f"{abs(lo):02d}s{abs(lo + 10):02d}s" if lo < 0 else f"{lo:02d}n{lo + 10:02d}n"
    return f"global_cumul_avg_cyl_{name}_002.tab", lo


def moon_thermal(lat: float, lon: float) -> dict:
    """Maximum and diurnal range of the bolometric temperature (area-weighted mean of the 0.5° cells)."""
    fname, lo = _gcp_file(lat)
    lats = lo + 0.25 + 0.5 * np.arange(20)
    lons = -179.75 + 0.5 * np.arange(720)
    LA, LO = np.meshgrid(lats, lons, indexing="ij")
    d = _gc_km(lat, float(_lon180(lon)), LA, LO, R_MOON_KM)
    sel = d <= HALF_KM if d.min() <= HALF_KM else d == d.min()
    cells = list(zip(*np.nonzero(sel)))
    local = CACHE / fname
    if len(cells) > 60 and not local.exists():  # many cells (poles): it pays to download the whole strip
        local = _download(GCP_URL + fname)
    frames = []
    for i, j in cells:
        start = GCP_ROW * (1 + (j * 20 + i) * 96)
        if local.exists():
            with open(local, "rb") as fh:
                fh.seek(start)
                buf = fh.read(96 * GCP_ROW)
        else:
            buf = _get(GCP_URL + fname, (start, start + 96 * GCP_ROW - 1))
        frames.append(pd.read_csv(io.BytesIO(buf), names=GCP_COLS, skipinitialspace=True))
    df = pd.concat(frames, ignore_index=True)
    df = df[df.tbol > 0]  # -9999 = no observation
    per = df.groupby(["clon", "clat"]).tbol.agg(["max", "min", "count"])
    per = per[per["count"] >= 48]  # al menos media curva diurna
    if per.empty:
        return {"thermal__t_max_k": np.nan, "thermal__t_range_k": np.nan}
    w = np.cos(np.radians(per.index.get_level_values("clat")))
    return {
        "thermal__t_max_k": float(np.average(per["max"], weights=w)),
        "thermal__t_range_k": float(np.average(per["max"] - per["min"], weights=w)),
        "thermal_t_min_k": float(np.average(per["min"], weights=w)),
    }


_prp = None


def moon_ice(lat: float, lon: float) -> dict:
    """Fraction of the area with stable water ice at <= 1 m (Paige et al. 2010 model).

    The product only covers > 80° S. Outside that zone there is NO data (NaN): it used to be set to 0 as an
    assumption, but an assumption is not data and it weighed heavily in the similarity. The north pole is not
    covered by this file either.
    """
    global _prp
    if lat >= -80:
        return {"ice__water_frac": np.nan, "ice_note": NO_ICE_DATA_NOTE}
    if _prp is None:
        cols = ["x1", "y1", "z1", "x2", "y2", "z2", "x3", "y3", "z3", "clon", "clat", "calt",
                "temp_avg", "temp_max", "ice_depth"]
        _prp = pd.read_csv(_download(PRP_URL), names=cols, skiprows=1, skipinitialspace=True,
                           usecols=["clon", "clat", "temp_max", "ice_depth"])
    d = _gc_km(lat, float(_lon180(lon)), _prp.clat.to_numpy(), _prp.clon.to_numpy(), R_MOON_KM)
    w = _prp[d <= HALF_KM]
    ice = w.ice_depth
    return {"ice__water_frac": float(((ice >= 0) & (ice <= 1.0)).mean()),
            "ice_frac_at_surface": float((ice == 0).mean()),
            "ice_note": "Diviner PRP south, area with stable ice at <= 1 m"}


_lpgrs = None


def moon_geo(lat: float, lon: float) -> dict:
    global _lpgrs
    if _lpgrs is None:
        t = pd.read_csv(_download(LPGRS_URL), sep=r"\s+", header=None, usecols=range(16))
        t.columns = ["pix", "lat0", "lat1", "lon0", "lon1", "am", "nden", "mgo", "al2o3", "sio2", "cao",
                     "tio2", "feo", "k", "th", "u"]
        _lpgrs = t
    t, lo = _lpgrs, float(_lon180(lon))
    row = t[(t.lat0 <= lat) & (lat < t.lat1) & (t.lon0 <= lo) & (lo < t.lon1)]
    if row.empty:
        row = t[(t.lat0 <= lat) & (lat <= t.lat1)]
    feo = float(row.iloc[0].feo) * 100
    return {"geo__basalt_frac": _basalt(feo), "geo_feo_wt_pct": feo, "geo_tio2_wt_pct": float(row.iloc[0].tio2) * 100}

# ---------------------------------------------------------------- Marte


_ody: dict[str, pd.DataFrame] = {}


def _ody_cell(name: str, lat: float, lon: float) -> pd.Series:
    if name not in _ody:
        t = pd.read_fwf(_download(ODY_URL + name), colspecs=[(0, 5), (15, 20), (28, 36), (45, 53)],
                        names=["lat", "lon", "val", "sigma"], header=None)
        _ody[name] = t.replace(9999.999, np.nan)
    t = _ody[name]
    d = _gc_km(lat, float(_lon180(lon)), t.lat.to_numpy(), _lon180(t.lon.to_numpy()), R_MARS_KM)
    return t.iloc[int(np.argmin(d))]


def mars_ice(lat: float, lon: float) -> dict:
    r = _ody_cell("h2o_sr_5x5.tab", lat, lon)
    return {"ice__water_frac": r.val / 100 if pd.notna(r.val) else np.nan,
            "ice_h2o_wt_pct": r.val, "ice_h2o_sigma_wt_pct": r.sigma,
            "ice_note": "Mars Odyssey GRS H2O_SR_5X5 (celda 5°)" if pd.notna(r.val) else NO_MARS_ICE_NOTE}


def mars_geo(lat: float, lon: float) -> dict:
    r = _ody_cell("fe_sr_5x5.tab", lat, lon)
    feo = r.val * 1.2865 if pd.notna(r.val) else np.nan  # Fe -> FeO
    return {"geo__basalt_frac": _basalt(feo), "geo_feo_wt_pct": feo}


def mars_thermal(lat: float, lon: float) -> dict:
    return {"thermal__t_max_k": np.nan, "thermal__t_range_k": np.nan}  # no map in the PDS: NaN, not imputed

# ---------------------------------------------------------------- tabla


def add_properties(df: pd.DataFrame, body: str) -> pd.DataFrame:
    """Adds thermal__*, ice__*, geo__* and diagnostics to the site table (columns lat, lon)."""
    fns = (moon_thermal, moon_ice, moon_geo) if body == "moon" else (mars_thermal, mars_ice, mars_geo)
    rows = []
    for r in df.itertuples():
        rec = {}
        for fn in fns:
            rec |= fn(r.lat, r.lon)
        rows.append(rec)
    extra = pd.DataFrame(rows, index=df.index)
    return df.drop(columns=[c for c in extra if c in df]).join(extra)
