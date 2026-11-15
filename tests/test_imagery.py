"""Orbital views (astroatlas/imagery.py): window geometry, tiles and composition, with no network (the download is simulated)."""
import io
import math

import pytest
from PIL import Image

from astroatlas import imagery as im


def test_ventana_es_un_cuadrado_en_kilometros():
    for body, lat in (("earth", 0.0), ("earth", 60.0), ("mars", 45.0), ("moon", -30.0)):
        lat0, lat1, lon0, lon1 = im.window(lat, 10.0, 150.0, body)
        kpg = im.KM_PER_DEGREE[body]
        alto = (lat1 - lat0) * kpg
        ancho = (lon1 - lon0) * kpg * math.cos(math.radians(lat))
        assert alto == pytest.approx(150.0, rel=1e-6) and ancho == pytest.approx(150.0, rel=1e-6)
        assert (lat0 + lat1) / 2 == pytest.approx(lat) and (lon0 + lon1) / 2 == pytest.approx(10.0)


def test_longitudes_0_360_pasan_a_menos_180_180():
    assert im.lon_180(77.58) == pytest.approx(77.58)
    assert im.lon_180(336.5781) == pytest.approx(-23.4219)
    assert im.lon_180(180.0) == pytest.approx(-180.0)


def test_rejilla_de_teselas_de_trek():
    # level z: 2^(z+1) columns x 2^z rows, each tile spans 180/2^z degrees from (-180°, 90°)
    filas, cols, gpp = im.tiles_needed(-1.0, 1.0, -1.0, 1.0, 7)
    span = 180.0 / 2 ** 7
    assert gpp == pytest.approx(span / 256)
    assert 63 in filas and 64 in filas and 127 in cols and 128 in cols   # the equator and the 0 meridian are in the centre
    assert im.zoom_for("mars", 2.5) == 7 and im.zoom_for("moon", 5.0) == 6   # 150 km: level 7 on Mars and 6 on the Moon (fewer tiles)
    assert im.zoom_for("mars", 360.0) == 0 and im.zoom_for("moon", 0.001) == 8   # cap per body


def test_vista_no_disponible_cerca_del_polo_y_cuerpos_desconocidos():
    assert im.view_available("moon", -85.98) is False and im.view_available("mars", 18.4) is True
    assert im.body_view("moon", -85.98, 358.33) is None        # Malapert: no download
    assert im.body_view("venus", 0.0, 0.0) is None


def test_url_de_la_tierra_lleva_capa_fecha_y_ventana():
    u = im.earth_url(32.5, 37.5, layer="modis")
    assert "gibs.earthdata.nasa.gov" in u and "MODIS_Terra_CorrectedReflectance_TrueColor" in u and "TIME=2023-07-15" in u
    assert "BlueMarble_NextGeneration" in im.earth_url(32.5, 37.5, layer="bluemarble")
    bbox = [float(x) for x in u.split("BBOX=")[1].split("&")[0].replace("%2C", ",").split(",")]
    assert bbox[0] < 37.5 < bbox[2] and bbox[1] < 32.5 < bbox[3]


def test_creditos_en_los_dos_idiomas():
    assert "NASA Trek" in im.credit("mars", lang="es") and "NASA Trek" in im.credit("mars", lang="en")
    assert "Viking" in im.credit("mars") and "LRO WAC" in im.credit("moon", lang="en")
    assert im.credit("earth", "modis", "es") != im.credit("earth", "modis", "en")
    assert "sin nubes" in im.credit("earth", "bluemarble", "es") and "cloud-free" in im.credit("earth", "bluemarble", "en")


def _fake_tile(color):
    b = io.BytesIO()
    Image.new("RGB", (256, 256), color).save(b, "JPEG", quality=100)
    return b.getvalue()


def test_composicion_recorte_y_tamano(monkeypatch):
    """Each fake tile carries its row and column in its colour: the central pixel must be the tile that contains the centre."""
    visited = []

    def fake(url):
        z, fila, col = (int(x) for x in url.rsplit(".jpg", 1)[0].rsplit("/", 3)[1:])
        visited.append((z, fila, col))
        return _fake_tile((col % 256, fila % 256, 0))

    monkeypatch.setattr(im, "_download", fake)
    lat, lon = 18.38, 77.58
    png = im.body_view("mars", lat, lon, size=256)
    out = Image.open(io.BytesIO(png))
    assert out.size == (256, 256)
    z = im.zoom_for("mars", im.window(lat, lon, im.WINDOW_KM, "mars")[3] - im.window(lat, lon, im.WINDOW_KM, "mars")[2], 256)
    span = 180.0 / 2 ** z
    expected = (int((lon + 180) // span) % 256, int((90 - lat) // span) % 256)
    r, g, b = out.getpixel((128, 128))
    assert (abs(r - expected[0]) <= 2) and (abs(g - expected[1]) <= 2)
    assert 0 < len(visited) <= im.MAX_TILES and all(v[0] == z for v in visited)


def test_si_una_tesela_falla_no_hay_imagen(monkeypatch):
    monkeypatch.setattr(im, "_download", lambda url: None)
    assert im.body_view("mars", 18.38, 77.58) is None
    assert im.earth_view(32.5, 37.5) is None


def test_vista_tierra_rechaza_respuestas_que_no_son_imagen(monkeypatch):
    monkeypatch.setattr(im, "_download", lambda url: b"<?xml version='1.0'?><ServiceExceptionReport/>")
    assert im.earth_view(32.5, 37.5) is None   # GIBS returns XML with the error instead of an image
    assert im.earth_view(89.5, 0.0) is None    # no view right at the pole
