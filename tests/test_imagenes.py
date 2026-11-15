"""Vistas desde órbita (analogos/imagenes.py): geometría de la ventana, teselas y composición, sin red (se simula la descarga)."""
import io
import math

import pytest
from PIL import Image

from analogos import imagenes as im


def test_ventana_es_un_cuadrado_en_kilometros():
    for cuerpo, lat in (("earth", 0.0), ("earth", 60.0), ("mars", 45.0), ("moon", -30.0)):
        lat0, lat1, lon0, lon1 = im.ventana(lat, 10.0, 150.0, cuerpo)
        kpg = im.KM_POR_GRADO[cuerpo]
        alto = (lat1 - lat0) * kpg
        ancho = (lon1 - lon0) * kpg * math.cos(math.radians(lat))
        assert alto == pytest.approx(150.0, rel=1e-6) and ancho == pytest.approx(150.0, rel=1e-6)
        assert (lat0 + lat1) / 2 == pytest.approx(lat) and (lon0 + lon1) / 2 == pytest.approx(10.0)


def test_longitudes_0_360_pasan_a_menos_180_180():
    assert im.lon_180(77.58) == pytest.approx(77.58)
    assert im.lon_180(336.5781) == pytest.approx(-23.4219)
    assert im.lon_180(180.0) == pytest.approx(-180.0)


def test_rejilla_de_teselas_de_trek():
    # nivel z: 2^(z+1) columnas x 2^z filas, cada tesela abarca 180/2^z grados desde (-180°, 90°)
    filas, cols, gpp = im.teselas_necesarias(-1.0, 1.0, -1.0, 1.0, 7)
    span = 180.0 / 2 ** 7
    assert gpp == pytest.approx(span / 256)
    assert 63 in filas and 64 in filas and 127 in cols and 128 in cols   # el ecuador y el meridiano 0 están en el centro
    assert im.zoom_para("mars", 2.5) == 7 and im.zoom_para("moon", 5.0) == 6   # 150 km: nivel 7 en Marte y 6 en la Luna (menos teselas)
    assert im.zoom_para("mars", 360.0) == 0 and im.zoom_para("moon", 0.001) == 8   # tope por cuerpo


def test_vista_no_disponible_cerca_del_polo_y_cuerpos_desconocidos():
    assert im.vista_disponible("moon", -85.98) is False and im.vista_disponible("mars", 18.4) is True
    assert im.vista_cuerpo("moon", -85.98, 358.33) is None        # Malapert: sin descarga
    assert im.vista_cuerpo("venus", 0.0, 0.0) is None


def test_url_de_la_tierra_lleva_capa_fecha_y_ventana():
    u = im.url_tierra(32.5, 37.5, capa="modis")
    assert "gibs.earthdata.nasa.gov" in u and "MODIS_Terra_CorrectedReflectance_TrueColor" in u and "TIME=2023-07-15" in u
    assert "BlueMarble_NextGeneration" in im.url_tierra(32.5, 37.5, capa="bluemarble")
    bbox = [float(x) for x in u.split("BBOX=")[1].split("&")[0].replace("%2C", ",").split(",")]
    assert bbox[0] < 37.5 < bbox[2] and bbox[1] < 32.5 < bbox[3]


def test_creditos_en_los_dos_idiomas():
    assert "NASA Trek" in im.credito("mars", lang="es") and "NASA Trek" in im.credito("mars", lang="en")
    assert "Viking" in im.credito("mars") and "LRO WAC" in im.credito("moon", lang="en")
    assert im.credito("earth", "modis", "es") != im.credito("earth", "modis", "en")
    assert "sin nubes" in im.credito("earth", "bluemarble", "es") and "cloud-free" in im.credito("earth", "bluemarble", "en")


def _tesela_falsa(color):
    b = io.BytesIO()
    Image.new("RGB", (256, 256), color).save(b, "JPEG", quality=100)
    return b.getvalue()


def test_composicion_recorte_y_tamano(monkeypatch):
    """Cada tesela falsa lleva su fila y columna en el color: el píxel central debe ser la tesela que contiene el centro."""
    visitadas = []

    def falsa(url):
        z, fila, col = (int(x) for x in url.rsplit(".jpg", 1)[0].rsplit("/", 3)[1:])
        visitadas.append((z, fila, col))
        return _tesela_falsa((col % 256, fila % 256, 0))

    monkeypatch.setattr(im, "_descargar", falsa)
    lat, lon = 18.38, 77.58
    png = im.vista_cuerpo("mars", lat, lon, tam=256)
    salida = Image.open(io.BytesIO(png))
    assert salida.size == (256, 256)
    z = im.zoom_para("mars", im.ventana(lat, lon, im.KM_VENTANA, "mars")[3] - im.ventana(lat, lon, im.KM_VENTANA, "mars")[2], 256)
    span = 180.0 / 2 ** z
    esperado = (int((lon + 180) // span) % 256, int((90 - lat) // span) % 256)
    r, g, b = salida.getpixel((128, 128))
    assert (abs(r - esperado[0]) <= 2) and (abs(g - esperado[1]) <= 2)
    assert 0 < len(visitadas) <= im.MAX_TESELAS and all(v[0] == z for v in visitadas)


def test_si_una_tesela_falla_no_hay_imagen(monkeypatch):
    monkeypatch.setattr(im, "_descargar", lambda url: None)
    assert im.vista_cuerpo("mars", 18.38, 77.58) is None
    assert im.vista_tierra(32.5, 37.5) is None


def test_vista_tierra_rechaza_respuestas_que_no_son_imagen(monkeypatch):
    monkeypatch.setattr(im, "_descargar", lambda url: b"<?xml version='1.0'?><ServiceExceptionReport/>")
    assert im.vista_tierra(32.5, 37.5) is None   # GIBS devuelve XML con el error en vez de una imagen
    assert im.vista_tierra(89.5, 0.0) is None    # sin vista justo en el polo
