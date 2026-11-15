"""DEM global de la Tierra: Copernicus GLO-90 (ESA) en AWS Open Data, sin login.

- Teselas COG de 1° x 1°, float32, EPSG:4326, cobertura global incluidos los polos. Los océanos no
  tienen tesela (404): se devuelven como NaN.
- Cada tesela se lee DECIMADA a ~360 m (usa las overviews del COG, ~0.3 MB en vez de ~5 MB) y se
  guarda en data/raw/copernicus90/. Con una base de 500 m no hace falta más resolución.
- Misma interfaz que RasterDem (res_m, radius_m, elevation) para usar `site_topography`.

Fuente: https://registry.opendata.aws/copernicus-dem/  (bucket copernicus-dem-90m, eu-central-1).
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
TARGET_M = 360.0  # resolución a la que se lee cada tesela (múltiplo de 90 m)
MAX_TILES = 16  # ventanas que cruzan más teselas (cerca de los polos) se devuelven como NaN
M_PER_DEG = 111_320.0
GDAL_OPTS = {"GDAL_DISABLE_READDIR_ON_OPEN": "EMPTY_DIR", "CPL_VSIL_CURL_ALLOWED_EXTENSIONS": ".tif",
             "GDAL_HTTP_MAX_RETRY": "4", "GDAL_HTTP_RETRY_DELAY": "2"}


def tile_name(lat_floor: int, lon_floor: int) -> str:
    ns, ew = ("N" if lat_floor >= 0 else "S"), ("E" if lon_floor >= 0 else "W")
    return f"Copernicus_DSM_COG_30_{ns}{abs(lat_floor):02d}_00_{ew}{abs(lon_floor):03d}_00_DEM"


def tile_url(name: str) -> str:
    return f"{BASE_URL}/{name}/{name}.tif"


def _retry(fn, tries: int = 4):
    """Reintenta con espera creciente ante cortes de red (ConnectionReset, DNS, lecturas truncadas)."""
    for attempt in range(tries):
        try:
            return fn()
        except urllib.error.HTTPError as e:
            if e.code < 500 or attempt == tries - 1:  # 403/404 los decide quien llama; 5xx se reintenta
                raise
        except (urllib.error.URLError, OSError, TimeoutError):
            if attempt == tries - 1:
                raise
        time.sleep(3 * (attempt + 1))


def _exists(url: str) -> bool:
    """HEAD: False solo si es 404/403 (océano). Los cortes de red se reintentan y luego se propagan."""
    def head():
        urllib.request.urlopen(urllib.request.Request(url, method="HEAD"), timeout=30).close()
        return True

    try:
        return _retry(head)
    except urllib.error.HTTPError as e:
        if e.code in (403, 404):  # el bucket responde 403 para claves inexistentes
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
        # RasterioIOError hereda de OSError: _retry la reintenta
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

    # --- API común con RasterDem ---
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
