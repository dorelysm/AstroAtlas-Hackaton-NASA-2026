"""Reading of global DEMs (simple cylindrical GeoTIFF, local or remote) and topography extraction.

Requires rasterio (`pip install -e ".[data]"`). Remote GeoTIFFs are read by window with
/vsicurl/ (HTTP range), without downloading the whole file. The USGS DEMs are organised by
rows, so every row of the window costs a full-width read.
"""
import math
import time

import numpy as np
import pandas as pd
from scipy.ndimage import map_coordinates

from ..config import FEATURES
from ..topography import local_grid, window_features

try:
    import rasterio
    from rasterio.windows import Window
except ImportError:  # pragma: no cover
    rasterio = None

GDAL_OPTS = {"GDAL_HTTP_MAX_RETRY": "4", "GDAL_HTTP_RETRY_DELAY": "2",
             "GDAL_DISABLE_READDIR_ON_OPEN": "EMPTY_DIR", "CPL_VSIL_CURL_ALLOWED_EXTENSIONS": ".tif"}


class RasterDem:
    """DEM in simple cylindrical projection (x = R·lon, y = R·lat), longitudes -180..180 east-positive."""

    def __init__(self, path_or_url: str):
        if rasterio is None:
            raise ImportError('Falta rasterio: pip install -e ".[data]"')
        self.path = ("/vsicurl/" + path_or_url) if path_or_url.startswith("http") else path_or_url
        self._env = self.ds = None

    def __enter__(self):
        self._env = rasterio.Env(**GDAL_OPTS)
        self._env.__enter__()
        self.ds = rasterio.open(self.path)
        b = self.ds.bounds
        self.res_m = float(self.ds.res[0])
        self.radius_m = (b.right - b.left) / (2 * math.pi)
        self.scale = float(self.ds.scales[0])
        self.nodata = self.ds.nodata
        return self

    def __exit__(self, *exc):
        self.ds.close()
        self._env.__exit__(*exc)

    def elevation(self, lat_deg: np.ndarray, lon_deg: np.ndarray) -> np.ndarray:
        """Elevation in metres (bilinear interpolation). Reads only the window needed."""
        b, ds = self.ds.bounds, self.ds
        lon = ((np.asarray(lon_deg) + 180) % 360) - 180
        x, y = self.radius_m * np.radians(lon), self.radius_m * np.radians(np.asarray(lat_deg))
        cols, rows = (x - b.left) / self.res_m - 0.5, (b.top - y) / self.res_m - 0.5
        r0, r1 = max(int(np.floor(rows.min())) - 1, 0), min(int(np.ceil(rows.max())) + 2, ds.height)
        c0, c1 = max(int(np.floor(cols.min())) - 1, 0), min(int(np.ceil(cols.max())) + 2, ds.width)
        if (c1 - c0) > ds.width / 2:  # crosses the antimeridian or the pole: full width
            c0, c1 = 0, ds.width
        arr = ds.read(1, window=Window(c0, r0, c1 - c0, r1 - r0)).astype("float64")
        if self.nodata is not None:
            arr[arr == self.nodata] = np.nan
        arr *= self.scale
        out = map_coordinates(arr, [rows - r0, cols - c0], order=1, mode="nearest", cval=np.nan)
        outside = (cols < c0) | (cols > c1 - 1) | (rows < r0) | (rows > r1 - 1)
        out[outside] = np.nan
        return out


def site_topography(dem, lat: float, lon_east: float, half_km: float = 25.0, baseline_m: float = 500.0) -> dict:
    """topo__* features of a window around (lat, lon). `dem` needs .res_m, .radius_m and .elevation().

    Sampling is baseline/k with k = round(baseline/native_res): so the effective baseline is EXACTLY
    `baseline_m` on the three bodies (it used to be 474 m on the Moon and 463 m on Mars).
    """
    k = max(1, round(baseline_m / dem.res_m))
    spacing = baseline_m / k
    lat_g, lon_g = local_grid(lat, lon_east, half_km * 1000, spacing, dem.radius_m)
    return window_features(dem.elevation(lat_g, lon_g), spacing, baseline_m, lat=lat)


def _enter(dem_src):
    """URL/path of a GeoTIFF -> opened RasterDem; an already-created DEM object is used as is."""
    return (RasterDem(dem_src) if isinstance(dem_src, str) else dem_src).__enter__()


def build_target_features(body: str, dem_src, sites: pd.DataFrame, half_km: float = 25.0,
                          baseline_m: float = 500.0, retries: int = 3) -> pd.DataFrame:
    """One row per site (contract: cell_id, body, site, lat, lon 0..360 + FEATURES).

    `dem_src`: URL/path of a GeoTIFF (RasterDem) or an already-created object with `.res_m`, `.radius_m`,
    `.elevation()` and `__enter__/__exit__` (e.g. `pds_dem.lola_dem()`). If a site fails because of the network
    (RasterioIOError and the urllib errors inherit from OSError) the DEM is reopened and the call retried; a
    site that keeps failing is skipped with a WARNING, without bringing down the rest.
    """
    rows, failed = [], []
    dem = _enter(dem_src)
    try:
        for s in sites[sites["body"] == body].itertuples():
            f = None
            for attempt in range(retries):
                try:
                    f = site_topography(dem, s.lat, s.lon, half_km, baseline_m)
                    break
                except OSError as e:  # network cut, truncated read, DNS
                    print(f"  retry {attempt + 1}/{retries} at {s.site}: {str(e)[:80]}")
                    dem.__exit__(None, None, None)
                    time.sleep(5 * (attempt + 1))
                    dem = _enter(dem_src)  # reopen (the rows already read from pds_dem are cached)
            if f is None:
                failed.append(s.site)
                continue
            rows.append({"cell_id": f"{body}_{s.site}_0", "body": body, "site": s.site,
                         "lat": s.lat, "lon": s.lon % 360, "kind": getattr(s, "kind", None), **f})
    finally:
        dem.__exit__(None, None, None)
    if failed:
        print(f"WARNING: sites without topography after {retries} attempts: {failed}")
    df = pd.DataFrame(rows)
    for col in FEATURES:  # dimensions not yet extracted stay as NaN
        if col not in df:
            df[col] = np.nan
    return df
