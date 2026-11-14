"""Lectura de DEM globales (GeoTIFF cilíndrico simple, local o remoto) y extracción de topografía.

Requiere rasterio (`pip install -e ".[data]"`). Los GeoTIFF remotos se leen por ventanas con
/vsicurl/ (HTTP range), sin bajar el archivo entero. Los DEM del USGS están organizados por
filas, así que cada fila de la ventana cuesta una lectura de un ancho completo.
"""
import math

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
    """DEM en proyección cilíndrica simple (x = R·lon, y = R·lat), longitudes -180..180 este-positivas."""

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
        """Elevación en metros (interpolación bilineal). Lee solo la ventana necesaria."""
        b, ds = self.ds.bounds, self.ds
        lon = ((np.asarray(lon_deg) + 180) % 360) - 180
        x, y = self.radius_m * np.radians(lon), self.radius_m * np.radians(np.asarray(lat_deg))
        cols, rows = (x - b.left) / self.res_m - 0.5, (b.top - y) / self.res_m - 0.5
        r0, r1 = max(int(np.floor(rows.min())) - 1, 0), min(int(np.ceil(rows.max())) + 2, ds.height)
        c0, c1 = max(int(np.floor(cols.min())) - 1, 0), min(int(np.ceil(cols.max())) + 2, ds.width)
        if (c1 - c0) > ds.width / 2:  # cruza el antimeridiano o el polo: ancho completo
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
    """Features topo__* de una ventana alrededor de (lat, lon). `dem` necesita .res_m, .radius_m y .elevation().

    El muestreo es baseline/k con k = round(baseline/res_nativa): así la base efectiva es EXACTAMENTE
    `baseline_m` en los tres cuerpos (antes salía 474 m en la Luna, 463 m en Marte).
    """
    k = max(1, round(baseline_m / dem.res_m))
    spacing = baseline_m / k
    lat_g, lon_g = local_grid(lat, lon_east, half_km * 1000, spacing, dem.radius_m)
    return window_features(dem.elevation(lat_g, lon_g), spacing, baseline_m, lat=lat)


def build_target_features(body: str, dem_url: str, sites: pd.DataFrame, half_km: float = 25.0,
                          baseline_m: float = 500.0) -> pd.DataFrame:
    """Una fila por sitio (contrato: cell_id, body, site, lat, lon 0..360 + FEATURES)."""
    rows = []
    with RasterDem(dem_url) as dem:
        for s in sites[sites["body"] == body].itertuples():
            f = site_topography(dem, s.lat, s.lon, half_km, baseline_m)
            rows.append({"cell_id": f"{body}_{s.site}_0", "body": body, "site": s.site,
                         "lat": s.lat, "lon": s.lon % 360, "kind": getattr(s, "kind", None), **f})
    df = pd.DataFrame(rows)
    for col in FEATURES:  # dimensiones aún sin extraer quedan como NaN
        if col not in df:
            df[col] = np.nan
    return df
