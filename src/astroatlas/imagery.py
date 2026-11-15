"""Orbital views of a place on the Moon, Mars or Earth, at the same scale, to compare them at a glance.

All of them come from open NASA services (no key needed):
- Earth: NASA GIBS (Global Imagery Browse Services), MODIS Terra true colour (one day) or Blue Marble Next Generation (cloud-free).
- Mars: NASA Trek, Viking MDIM 2.1 colour mosaic (232 m per pixel).
- Moon: NASA Trek, LRO WAC mosaic (≈ 100 m per pixel).
The window is a square of `km` kilometres per side centred on the place. If a service does not respond, the functions return None and the app
shows a fallback text: the app never depends on these images being available.
"""
import io
import math
from concurrent.futures import ThreadPoolExecutor
import urllib.error
import urllib.parse
import urllib.request

from PIL import Image

USER_AGENT = "analogos-astroatlas"
TIMEOUT_S = 20
TILE_PX = 256
WINDOW_KM = 150.0             # side of the window: it shows more terrain than the model's 50 km and is easier to recognise
KM_PER_DEGREE = {"mars": 2 * math.pi * 3389.5 / 360, "moon": 2 * math.pi * 1737.4 / 360, "earth": 2 * math.pi * 6371.0 / 360}
# Trek tile grid (WMTS "default028mm"): at level z there are 2^(z+1) columns x 2^z rows of 256 px, with the top
# left corner at -180° / 90°; each tile spans 180/2^z degrees. Maximum published levels: Mars 7, Moon 8.
_DEG_PER_PX_LEVEL0 = 180.0 / TILE_PX
ZOOM_MAX = {"mars": 7, "moon": 8}
MAX_TILES = 16
TREK = {
    "mars": ("https://trek.nasa.gov/tiles/Mars/EQ/Mars_Viking_MDIM21_ClrMosaic_global_232m/1.0.0/default/default028mm/{z}/{row}/{col}.jpg",
             {"es": "NASA/JPL/USGS, mosaico Viking MDIM 2.1 (232 m/píxel), vía NASA Trek",
              "en": "NASA/JPL/USGS, Viking MDIM 2.1 mosaic (232 m/pixel), via NASA Trek"}),
    "moon": ("https://trek.nasa.gov/tiles/Moon/EQ/LRO_WAC_Mosaic_Global_303ppd_v02/1.0.0/default/default028mm/{z}/{row}/{col}.jpg",
             {"es": "NASA/GSFC/ASU, mosaico LRO WAC (≈ 100 m/píxel), vía NASA Trek",
              "en": "NASA/GSFC/ASU, LRO WAC mosaic (≈ 100 m/pixel), via NASA Trek"}),
}
GIBS_WMS = "https://gibs.earthdata.nasa.gov/wms/epsg4326/best/wms.cgi"
EARTH_LAYERS = {
    "modis": ("MODIS_Terra_CorrectedReflectance_TrueColor", "2023-07-15",
              {"es": "NASA GIBS, MODIS Terra en color verdadero (250 m/píxel, un día de 2023)",
               "en": "NASA GIBS, MODIS Terra true color (250 m/pixel, a single day in 2023)"}),
    "bluemarble": ("BlueMarble_NextGeneration", "2004-07-01",
                   {"es": "NASA Earth Observatory, Blue Marble Next Generation (500 m/píxel, sin nubes), vía NASA GIBS",
                    "en": "NASA Earth Observatory, Blue Marble Next Generation (500 m/pixel, cloud-free), via NASA GIBS"}),
}
LAT_MAX_VIEW = 84.0           # closer to the pole the rectangular Trek projection distorts too much: it is not shown


def window(lat: float, lon: float, km: float, body: str) -> tuple[float, float, float, float]:
    """(lat0, lat1, lon0, lon1) in degrees of a square of `km` km per side centred on the place (longitude widens with latitude)."""
    kpg = KM_PER_DEGREE[body]
    dlat = km / kpg / 2
    dlon = min(km / (kpg * max(math.cos(math.radians(lat)), 0.02)) / 2, 90.0)
    return lat - dlat, lat + dlat, lon - dlon, lon + dlon


def lon_180(lon: float) -> float:
    """Longitude in -180..180 (Moon and Mars sites are stored as 0..360 east)."""
    return ((lon + 180.0) % 360.0) - 180.0


def view_available(body: str, lat: float) -> bool:
    return abs(lat) <= LAT_MAX_VIEW


def _download(url: str) -> bytes | None:
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": USER_AGENT}), timeout=TIMEOUT_S) as r:
            return r.read()
    except (urllib.error.URLError, TimeoutError, OSError):
        return None


def zoom_for(body: str, width_deg: float, size: int = 512) -> int:
    """Lowest tile level with at least ~85 % of the requested pixels across (so few tiles are downloaded)."""
    for z in range(ZOOM_MAX[body] + 1):
        if width_deg / (_DEG_PER_PX_LEVEL0 / 2 ** z) >= 0.85 * size:
            return z
    return ZOOM_MAX[body]


def tiles_needed(lat0: float, lat1: float, lon0: float, lon1: float, z: int) -> tuple[range, range, float]:
    """(rows, columns, degrees per pixel) of the Trek tiles that cover the window."""
    gpp = _DEG_PER_PX_LEVEL0 / 2 ** z
    span = TILE_PX * gpp
    rows = range(int((90.0 - lat1) // span), int((90.0 - lat0) // span) + 1)
    cols = range(int((lon0 + 180.0) // span), int((lon1 + 180.0) // span) + 1)
    return rows, cols, gpp


def tile_url(body: str, z: int, row: int, col: int) -> str:
    return TREK[body][0].format(z=z, row=row, col=col)


def body_view(body: str, lat: float, lon: float, km: float = WINDOW_KM, size: int = 512) -> bytes | None:
    """Square PNG (size x size) of the window around a Moon or Mars site, or None if there is no view or the download fails."""
    if body not in TREK or not view_available(body, lat):
        return None
    lon = lon_180(lon)
    lat0, lat1, lon0, lon1 = window(lat, lon, km, body)
    z = zoom_for(body, lon1 - lon0, size)
    rows, cols, gpp = tiles_needed(lat0, lat1, lon0, lon1, z)
    if len(rows) * len(cols) > MAX_TILES or cols.start < 0 or rows.start < 0:
        return None
    canvas = Image.new("RGB", (len(cols) * TILE_PX, len(rows) * TILE_PX))
    positions = [(i, j, row, col) for i, row in enumerate(rows) for j, col in enumerate(cols)]
    with ThreadPoolExecutor(max_workers=6) as pool:  # the tiles are downloaded at the same time: from ~5 s to ~1 s
        downloads = list(pool.map(lambda x: _download(tile_url(body, z, x[2], x[3])), positions))
    for (i, j, _, _), data in zip(positions, downloads):
        if data is None:
            return None
        try:
            canvas.paste(Image.open(io.BytesIO(data)).convert("RGB"), (j * TILE_PX, i * TILE_PX))
        except Exception:  # noqa: BLE001  (a corrupt tile = no image)
            return None
    # top-left corner of the canvas in degrees and window crop (in grid pixels)
    top, left = 90.0 - rows.start * TILE_PX * gpp, -180.0 + cols.start * TILE_PX * gpp
    box = ((lon0 - left) / gpp, (top - lat1) / gpp, (lon1 - left) / gpp, (top - lat0) / gpp)
    out = canvas.crop(tuple(int(round(v)) for v in box)).resize((size, size), Image.LANCZOS)
    buf = io.BytesIO()
    out.save(buf, "PNG")
    return buf.getvalue()


def earth_url(lat: float, lon: float, km: float = WINDOW_KM, layer: str = "modis", size: int = 512) -> str:
    """NASA GIBS (WMS) address that returns a square JPEG of the window around an Earth place."""
    nombre, fecha, _ = EARTH_LAYERS[layer]
    lat0, lat1, lon0, lon1 = window(lat, lon_180(lon), km, "earth")
    q = {"SERVICE": "WMS", "REQUEST": "GetMap", "VERSION": "1.1.1", "SRS": "EPSG:4326", "FORMAT": "image/jpeg", "STYLES": "",
         "LAYERS": nombre, "TIME": fecha, "WIDTH": size, "HEIGHT": size, "BBOX": f"{lon0:.4f},{lat0:.4f},{lon1:.4f},{lat1:.4f}"}
    return GIBS_WMS + "?" + urllib.parse.urlencode(q)


def earth_view(lat: float, lon: float, km: float = WINDOW_KM, layer: str = "modis", size: int = 512) -> bytes | None:
    """JPEG of the window around an Earth place (NASA GIBS), or None if the download fails."""
    if abs(lat) > 89.0:
        return None
    data = _download(earth_url(lat, lon, km, layer, size))
    if data is None:
        return None
    try:
        Image.open(io.BytesIO(data)).verify()  # GIBS returns XML with the error instead of an image if anything fails
    except Exception:  # noqa: BLE001
        return None
    return data


def credit(body: str, layer: str = "modis", lang: str = "en") -> str:
    """Credit of a body's image (to show below it), in Spanish or English."""
    source = EARTH_LAYERS[layer][2] if body == "earth" else TREK[body][1]
    return source.get(lang, source["en"])
