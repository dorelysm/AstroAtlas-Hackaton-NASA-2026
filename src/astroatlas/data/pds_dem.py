"""Moon and Mars DEMs read directly from the NASA PDS (Geosciences Node), without rasterio.

- Moon: LRO LOLA LDEM_256 (256 px/°, ~118 m), 4 simple cylindrical tiles, int16 LSB, height = DN * 0.5 m
  above the 1737.4 km sphere.
  https://pds-geosciences.wustl.edu/lro/lro-l-lola-3-rdr-v1/lrolol_1xxx/data/lola_gdr/cylindrical/img/
- Mars: MGS MOLA MEGDR 128 px/° (~463 m), 16 tiles of 44° x 90°, int16 MSB, height in m above the
  areoid (covers 88° S to 88° N).
  https://pds-geosciences.wustl.edu/mgs/mgs-m-mola-5-megdr-l3-v1/mgsl_300x/meg128/

It is the same data as the USGS mosaics used before, but served by NASA.
Each read downloads by HTTP Range only the rows the window needs (full tile rows)
and stores them in data/raw/pds_dem/ so the download is not repeated.
Same interface as RasterDem (res_m, radius_m, elevation) so `site_topography` can use it.
"""
import hashlib
import math
import time
import urllib.request
from dataclasses import dataclass

import numpy as np
from scipy.ndimage import map_coordinates

from ..config import RAW_DIR

CACHE_DIR = RAW_DIR / "pds_dem"
LOLA_BASE = "https://pds-geosciences.wustl.edu/lro/lro-l-lola-3-rdr-v1/lrolol_1xxx/data/lola_gdr/cylindrical/img/"
MOLA_BASE = "https://pds-geosciences.wustl.edu/mgs/mgs-m-mola-5-megdr-l3-v1/mgsl_300x/meg128/"


@dataclass(frozen=True)
class Tile:
    url: str
    lat_max: float
    lat_min: float
    lon_min: float  # 0..360 este
    lon_max: float


def _lola_tiles() -> list[Tile]:
    out = []
    for lat_tag, (lat_max, lat_min) in {"00n_90n": (90, 0), "90s_00s": (0, -90)}.items():
        for lon_tag, (l0, l1) in {"000_180": (0, 180), "180_360": (180, 360)}.items():
            out.append(Tile(f"{LOLA_BASE}ldem_256_{lat_tag}_{lon_tag}.img", lat_max, lat_min, l0, l1))
    return out


def _mola_tiles() -> list[Tile]:
    out = []
    for lat_tag, lat_max in {"88n": 88, "44n": 44, "00n": 0, "44s": -44}.items():
        for l0 in (0, 90, 180, 270):
            out.append(Tile(f"{MOLA_BASE}megt{lat_tag}{l0:03d}hb.img", lat_max, lat_max - 44, l0, l0 + 90))
    return out


class PdsTiledDem:
    """Global DEM in simple cylindrical PDS tiles. `elevation` returns metres (NaN outside)."""

    def __init__(self, tiles, ppd: int, dtype: str, scale: float, radius_m: float, lat_limit: float = 90.0):
        self.tiles, self.ppd, self.dtype, self.scale = tiles, ppd, np.dtype(dtype), scale
        self.radius_m = radius_m
        self.res_m = radius_m * math.pi / 180 / ppd
        self.lat_limit = lat_limit
        self.width = 360 * ppd

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def _rows(self, tile: Tile, r0: int, r1: int) -> np.ndarray:
        """Rows [r0, r1) of a tile (local indices), with on-disk cache."""
        ncols = int(round((tile.lon_max - tile.lon_min) * self.ppd))
        row_bytes = ncols * self.dtype.itemsize
        key = hashlib.md5(f"{tile.url}:{r0}:{r1}".encode()).hexdigest()[:16]
        path = CACHE_DIR / f"{tile.url.rsplit('/', 1)[1]}_{r0}_{r1}_{key}.npy"
        if path.exists():
            return np.load(path)
        req = urllib.request.Request(tile.url, headers={"Range": f"bytes={r0 * row_bytes}-{r1 * row_bytes - 1}"})
        for attempt in range(5):  # the network cuts long connections from time to time
            try:
                with urllib.request.urlopen(req, timeout=300) as resp:
                    buf = resp.read()
                break
            except OSError:
                if attempt == 4:
                    raise
                time.sleep(2 * (attempt + 1))
        if len(buf) != (r1 - r0) * row_bytes:
            raise RuntimeError(f"{tile.url}: expected {(r1 - r0) * row_bytes} bytes y llegaron {len(buf)}")
        arr = np.frombuffer(buf, dtype=self.dtype).reshape(r1 - r0, ncols)
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        np.save(path, arr)
        return arr

    def _band(self, g0: int, g1: int, lon_needed=None) -> np.ndarray:
        """Global rows [g0, g1) across the full 360° width (row 0 = latitude +90).

        `lon_needed` (array of longitudes 0..360): only the tiles that contain them are downloaded;
        the other columns stay NaN.
        """
        out = np.full((g1 - g0, self.width), np.nan)
        for t in self.tiles:
            if lon_needed is not None and not np.any((lon_needed >= t.lon_min - 0.01) & (lon_needed <= t.lon_max + 0.01)):
                continue
            t0 = int(round((90 - t.lat_max) * self.ppd))
            t1 = int(round((90 - t.lat_min) * self.ppd))
            a, b = max(g0, t0), min(g1, t1)
            if a >= b:
                continue
            c0 = int(round(t.lon_min * self.ppd))
            rows = self._rows(t, a - t0, b - t0).astype("float64") * self.scale
            out[a - g0:b - g0, c0:c0 + rows.shape[1]] = rows
        return out

    def elevation(self, lat_deg: np.ndarray, lon_deg: np.ndarray) -> np.ndarray:
        lat = np.asarray(lat_deg, dtype="float64")
        lon = np.asarray(lon_deg, dtype="float64") % 360
        rows = (90 - lat) * self.ppd - 0.5
        cols = lon * self.ppd - 0.5
        g0 = max(int(np.floor(rows.min())) - 1, 0)
        g1 = min(int(np.ceil(rows.max())) + 2, 180 * self.ppd)
        band = self._band(g0, g1, lon)
        # extra column to interpolate across 0°/360°
        band = np.concatenate([band[:, -1:], band, band[:, :1]], axis=1)
        out = map_coordinates(band, [rows - g0, cols + 1], order=1, mode="nearest")
        out[np.abs(lat) > self.lat_limit] = np.nan
        return out


def lola_dem() -> PdsTiledDem:
    return PdsTiledDem(_lola_tiles(), ppd=256, dtype="<i2", scale=0.5, radius_m=1737400.0)


def mola_dem() -> PdsTiledDem:
    return PdsTiledDem(_mola_tiles(), ppd=128, dtype=">i2", scale=1.0, radius_m=3396000.0, lat_limit=88.0)
