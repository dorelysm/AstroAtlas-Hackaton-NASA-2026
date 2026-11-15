"""Vistas desde órbita de un lugar de la Luna, de Marte o de la Tierra, a la misma escala, para compararlos a simple vista.

Todas vienen de servicios abiertos de la NASA (no hace falta clave):
- Tierra: NASA GIBS (Global Imagery Browse Services), MODIS Terra en color verdadero (un día) o Blue Marble Next Generation (sin nubes).
- Marte: NASA Trek, mosaico en color de Viking MDIM 2.1 (232 m por píxel).
- Luna: NASA Trek, mosaico de LRO WAC (≈ 100 m por píxel).
La ventana es un cuadrado de `km` kilómetros de lado centrado en el lugar. Si un servicio no responde, las funciones devuelven None y la app
muestra un texto de reserva: la app nunca depende de que estas imágenes estén disponibles.
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
KM_VENTANA = 150.0             # lado de la ventana: ve más terreno que los 50 km del modelo y se reconoce mejor
KM_POR_GRADO = {"mars": 2 * math.pi * 3389.5 / 360, "moon": 2 * math.pi * 1737.4 / 360, "earth": 2 * math.pi * 6371.0 / 360}
# Rejilla de teselas de Trek (WMTS «default028mm»): en el nivel z hay 2^(z+1) columnas x 2^z filas de 256 px, con esquina superior
# izquierda en -180° / 90°; cada tesela abarca 180/2^z grados. Niveles máximos publicados: Marte 7, Luna 8.
_GRADOS_POR_PX_NIVEL0 = 180.0 / TILE_PX
ZOOM_MAX = {"mars": 7, "moon": 8}
MAX_TESELAS = 16
TREK = {
    "mars": ("https://trek.nasa.gov/tiles/Mars/EQ/Mars_Viking_MDIM21_ClrMosaic_global_232m/1.0.0/default/default028mm/{z}/{row}/{col}.jpg",
             {"es": "NASA/JPL/USGS, mosaico Viking MDIM 2.1 (232 m/píxel), vía NASA Trek",
              "en": "NASA/JPL/USGS, Viking MDIM 2.1 mosaic (232 m/pixel), via NASA Trek"}),
    "moon": ("https://trek.nasa.gov/tiles/Moon/EQ/LRO_WAC_Mosaic_Global_303ppd_v02/1.0.0/default/default028mm/{z}/{row}/{col}.jpg",
             {"es": "NASA/GSFC/ASU, mosaico LRO WAC (≈ 100 m/píxel), vía NASA Trek",
              "en": "NASA/GSFC/ASU, LRO WAC mosaic (≈ 100 m/pixel), via NASA Trek"}),
}
GIBS_WMS = "https://gibs.earthdata.nasa.gov/wms/epsg4326/best/wms.cgi"
CAPAS_TIERRA = {
    "modis": ("MODIS_Terra_CorrectedReflectance_TrueColor", "2023-07-15",
              {"es": "NASA GIBS, MODIS Terra en color verdadero (250 m/píxel, un día de 2023)",
               "en": "NASA GIBS, MODIS Terra true color (250 m/pixel, a single day in 2023)"}),
    "bluemarble": ("BlueMarble_NextGeneration", "2004-07-01",
                   {"es": "NASA Earth Observatory, Blue Marble Next Generation (500 m/píxel, sin nubes), vía NASA GIBS",
                    "en": "NASA Earth Observatory, Blue Marble Next Generation (500 m/pixel, cloud-free), via NASA GIBS"}),
}
LAT_MAX_VISTA = 84.0           # más cerca del polo la proyección rectangular de Trek deforma demasiado: no se muestra


def ventana(lat: float, lon: float, km: float, cuerpo: str) -> tuple[float, float, float, float]:
    """(lat0, lat1, lon0, lon1) en grados de un cuadrado de `km` km de lado centrado en el lugar (la longitud se ensancha con la latitud)."""
    kpg = KM_POR_GRADO[cuerpo]
    dlat = km / kpg / 2
    dlon = min(km / (kpg * max(math.cos(math.radians(lat)), 0.02)) / 2, 90.0)
    return lat - dlat, lat + dlat, lon - dlon, lon + dlon


def lon_180(lon: float) -> float:
    """Longitud en -180..180 (los sitios de la Luna y de Marte se guardan en 0..360 este)."""
    return ((lon + 180.0) % 360.0) - 180.0


def vista_disponible(cuerpo: str, lat: float) -> bool:
    return abs(lat) <= LAT_MAX_VISTA


def _descargar(url: str) -> bytes | None:
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": USER_AGENT}), timeout=TIMEOUT_S) as r:
            return r.read()
    except (urllib.error.URLError, TimeoutError, OSError):
        return None


def zoom_para(cuerpo: str, ancho_grados: float, tam: int = 512) -> int:
    """Nivel más bajo de teselas con al menos ~85 % de los píxeles pedidos a lo ancho (así se descargan pocas teselas)."""
    for z in range(ZOOM_MAX[cuerpo] + 1):
        if ancho_grados / (_GRADOS_POR_PX_NIVEL0 / 2 ** z) >= 0.85 * tam:
            return z
    return ZOOM_MAX[cuerpo]


def teselas_necesarias(lat0: float, lat1: float, lon0: float, lon1: float, z: int) -> tuple[range, range, float]:
    """(filas, columnas, grados por píxel) de las teselas de Trek que cubren la ventana."""
    gpp = _GRADOS_POR_PX_NIVEL0 / 2 ** z
    span = TILE_PX * gpp
    filas = range(int((90.0 - lat1) // span), int((90.0 - lat0) // span) + 1)
    cols = range(int((lon0 + 180.0) // span), int((lon1 + 180.0) // span) + 1)
    return filas, cols, gpp


def url_tesela(cuerpo: str, z: int, fila: int, col: int) -> str:
    return TREK[cuerpo][0].format(z=z, row=fila, col=col)


def vista_cuerpo(cuerpo: str, lat: float, lon: float, km: float = KM_VENTANA, tam: int = 512) -> bytes | None:
    """PNG cuadrado (tam x tam) de la ventana alrededor de un sitio de la Luna o de Marte, o None si no hay vista o falla la descarga."""
    if cuerpo not in TREK or not vista_disponible(cuerpo, lat):
        return None
    lon = lon_180(lon)
    lat0, lat1, lon0, lon1 = ventana(lat, lon, km, cuerpo)
    z = zoom_para(cuerpo, lon1 - lon0, tam)
    filas, cols, gpp = teselas_necesarias(lat0, lat1, lon0, lon1, z)
    if len(filas) * len(cols) > MAX_TESELAS or cols.start < 0 or filas.start < 0:
        return None
    lienzo = Image.new("RGB", (len(cols) * TILE_PX, len(filas) * TILE_PX))
    posiciones = [(i, j, fila, col) for i, fila in enumerate(filas) for j, col in enumerate(cols)]
    with ThreadPoolExecutor(max_workers=6) as pool:  # las teselas se descargan a la vez: de ~5 s a ~1 s
        descargas = list(pool.map(lambda x: _descargar(url_tesela(cuerpo, z, x[2], x[3])), posiciones))
    for (i, j, _, _), datos in zip(posiciones, descargas):
        if datos is None:
            return None
        try:
            lienzo.paste(Image.open(io.BytesIO(datos)).convert("RGB"), (j * TILE_PX, i * TILE_PX))
        except Exception:  # noqa: BLE001  (una tesela dañada = sin imagen)
            return None
    # esquina superior izquierda del lienzo en grados y recorte de la ventana (en píxeles de la rejilla)
    top, left = 90.0 - filas.start * TILE_PX * gpp, -180.0 + cols.start * TILE_PX * gpp
    caja = ((lon0 - left) / gpp, (top - lat1) / gpp, (lon1 - left) / gpp, (top - lat0) / gpp)
    salida = lienzo.crop(tuple(int(round(v)) for v in caja)).resize((tam, tam), Image.LANCZOS)
    buf = io.BytesIO()
    salida.save(buf, "PNG")
    return buf.getvalue()


def url_tierra(lat: float, lon: float, km: float = KM_VENTANA, capa: str = "modis", tam: int = 512) -> str:
    """Dirección de NASA GIBS (WMS) que devuelve un JPEG cuadrado de la ventana alrededor de un lugar de la Tierra."""
    nombre, fecha, _ = CAPAS_TIERRA[capa]
    lat0, lat1, lon0, lon1 = ventana(lat, lon_180(lon), km, "earth")
    q = {"SERVICE": "WMS", "REQUEST": "GetMap", "VERSION": "1.1.1", "SRS": "EPSG:4326", "FORMAT": "image/jpeg", "STYLES": "",
         "LAYERS": nombre, "TIME": fecha, "WIDTH": tam, "HEIGHT": tam, "BBOX": f"{lon0:.4f},{lat0:.4f},{lon1:.4f},{lat1:.4f}"}
    return GIBS_WMS + "?" + urllib.parse.urlencode(q)


def vista_tierra(lat: float, lon: float, km: float = KM_VENTANA, capa: str = "modis", tam: int = 512) -> bytes | None:
    """JPEG de la ventana alrededor de un lugar de la Tierra (NASA GIBS), o None si falla la descarga."""
    if abs(lat) > 89.0:
        return None
    datos = _descargar(url_tierra(lat, lon, km, capa, tam))
    if datos is None:
        return None
    try:
        Image.open(io.BytesIO(datos)).verify()  # GIBS devuelve XML con el error en vez de una imagen si algo falla
    except Exception:  # noqa: BLE001
        return None
    return datos


def credito(cuerpo: str, capa: str = "modis", lang: str = "es") -> str:
    """Crédito de la imagen de un cuerpo (para mostrarlo debajo), en español o inglés."""
    fuente = CAPAS_TIERRA[capa][2] if cuerpo == "earth" else TREK[cuerpo][1]
    return fuente.get(lang, fuente["es"])
