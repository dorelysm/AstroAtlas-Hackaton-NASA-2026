"""Global Earth DEM: Copernicus GLO-90 (ESA) on AWS Open Data, no login.

- 1° x 1° COG tiles, float32, EPSG:4326, global coverage including the poles. Oceans have
  no tile (404): they are returned as NaN.
- Each tile is read DECIMATED to ~360 m (uses the COG overviews, ~0.3 MB instead of ~5 MB) and
  cached in data/raw/copernicus90/. With a 500 m baseline no more resolution is needed.
- Same interface as RasterDem (res_m, radius_m, elevation) so `site_topography` can use it.

Source: https://registry.opendata.aws/copernicus-dem/  (bucket copernicus-dem-90m, eu-central-1).
"""
import math
import threading
import time
import urllib.error
import urllib.request

import numpy as np
from scipy.ndimage import map_coordinates

from ..config import RAW_DIR

try:
    import rasterio
    from rasterio.enums import Resampling
except ImportError:  # pragma: no cover
    rasterio = None

BASE_URL = "https://copernicus-dem-90m.s3.eu-central-1.amazonaws.com"
CACHE_DIR = RAW_DIR / "copernicus90"
TARGET_M = 360.0  # resolution at which each tile is read (multiple of 90 m)
MAX_TILES = 16  # windows crossing more tiles (near the poles) are returned as NaN
M_PER_DEG = 111_320.0
GDAL_OPTS = {"GDAL_DISABLE_READDIR_ON_OPEN": "EMPTY_DIR", "CPL_VSIL_CURL_ALLOWED_EXTENSIONS": ".tif",
             "GDAL_HTTP_MAX_RETRY": "4", "GDAL_HTTP_RETRY_DELAY": "2"}


def tile_name(lat_floor: int, lon_floor: int) -> str:
    ns, ew = ("N" if lat_floor >= 0 else "S"), ("E" if lon_floor >= 0 else "W")
    return f"Copernicus_DSM_COG_30_{ns}{abs(lat_floor):02d}_00_{ew}{abs(lon_floor):03d}_00_DEM"


def tile_url(name: str) -> str:
    return f"{BASE_URL}/{name}/{name}.tif"


def _retry(fn, tries: int = 4):
    """Retries with growing back-off on network cuts (ConnectionReset, DNS, truncated reads)."""
    for attempt in range(tries):
        try:
            return fn()
        except urllib.error.HTTPError as e:
            if e.code < 500 or attempt == tries - 1:  # 403/404 are decided by the caller; 5xx is retried
                raise
        except (urllib.error.URLError, OSError, TimeoutError):
            if attempt == tries - 1:
                raise
        time.sleep(3 * (attempt + 1))


def _exists(url: str) -> bool:
    """HEAD: False only for 404/403 (ocean). Network cuts are retried and then propagated."""
    def head():
        urllib.request.urlopen(urllib.request.Request(url, method="HEAD"), timeout=30).close()
        return True

    try:
        return _retry(head)
    except urllib.error.HTTPError as e:
        if e.code in (403, 404):  # the bucket answers 403 for non-existent keys
            return False
        raise


class CopernicusDem:
    res_m = TARGET_M
    radius_m = 6_371_000.0

    def __init__(self):
        if rasterio is None:
            raise ImportError('Falta rasterio: pip install -e ".[data]"')
        self._tiles: dict = {}
        self._lock = threading.Lock()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    # --- teselas ---
    def _read_tile(self, name: str):
        url = tile_url(name)
        if not _exists(url):
            return None
        return _retry(lambda: self._read_open_tile(url))

    @staticmethod
    def _read_open_tile(url: str):
        # RasterioIOError inherits from OSError: _retry retries it
        with rasterio.Env(**GDAL_OPTS), rasterio.open("/vsicurl/" + url) as ds:
            b = ds.bounds
            lat_c = (b.top + b.bottom) / 2
            dx_m = ds.res[0] * M_PER_DEG * math.cos(math.radians(lat_c))
            dy_m = ds.res[1] * M_PER_DEG
            out_w = max(2, int(ds.width // max(1, round(TARGET_M / max(dx_m, 1e-6)))))
            out_h = max(2, int(ds.height // max(1, round(TARGET_M / dy_m))))
            arr = ds.read(1, out_shape=(out_h, out_w), resampling=Resampling.average).astype("float64")
            return arr, b.left, b.top, (b.right - b.left) / out_w, (b.top - b.bottom) / out_h

    def _load_tile(self, name: str):
        with self._lock:
            if name in self._tiles:
                return self._tiles[name]
        cache, missing = CACHE_DIR / f"{name}.npz", CACHE_DIR / f"{name}.missing"
        if missing.exists():
            tile = None
        elif cache.exists():
            z = np.load(cache)
            tile = (z["arr"], float(z["left"]), float(z["top"]), float(z["dx"]), float(z["dy"]))
        else:
            tile = self._read_tile(name)
            CACHE_DIR.mkdir(parents=True, exist_ok=True)
            if tile is None:
                missing.touch()
            else:
                np.savez_compressed(cache, arr=tile[0].astype("float32"), left=tile[1], top=tile[2],
                                    dx=tile[3], dy=tile[4])
        with self._lock:
            self._tiles[name] = tile
        return tile

    # --- API shared with RasterDem ---
    def elevation(self, lat_deg: np.ndarray, lon_deg: np.ndarray) -> np.ndarray:
        lat = np.asarray(lat_deg, dtype="float64")
        lon = ((np.asarray(lon_deg, dtype="float64") + 180) % 360) - 180
        out = np.full(lat.shape, np.nan)
        lat_f, lon_f = np.floor(lat).astype(int), np.floor(lon).astype(int)
        keys = set(zip(lat_f.ravel().tolist(), lon_f.ravel().tolist()))
        if len(keys) > MAX_TILES:
            return out
        for la, lo in keys:
            tile = self._load_tile(tile_name(la, lo))
            if tile is None:
                continue
            arr, left, top, dx, dy = tile
            m = (lat_f == la) & (lon_f == lo)
            rows, cols = (top - lat[m]) / dy - 0.5, (lon[m] - left) / dx - 0.5
            out[m] = map_coordinates(arr, [rows, cols], order=1, mode="nearest")
        return out
