"""Tests sin red de edl.py y earth_water.py."""
import numpy as np
import pandas as pd
import pytest

from analogos.data import earth_water as ew
from analogos.data import edl

LATS = 90 - 0.05 * (np.arange(3600) + 0.5)
LONS = -180 + 0.05 * (np.arange(7200) + 0.5)


# --- edl.load_env ---
def test_load_env_does_not_override_and_ignores_comments(tmp_path, monkeypatch):
    env = tmp_path / ".env"
    env.write_text("# comentario\nEARTHDATA_USERNAME=alguien\nEARTHDATA_PASSWORD=\"clave con espacios\"\n"
                   "VACIA=\nSIN_IGUAL\nYA_DEFINIDA=nueva\n", encoding="utf-8")
    monkeypatch.delenv("EARTHDATA_USERNAME", raising=False)
    monkeypatch.delenv("EARTHDATA_PASSWORD", raising=False)
    monkeypatch.delenv("VACIA", raising=False)
    monkeypatch.setenv("YA_DEFINIDA", "original")
    loaded = edl.load_env(env)
    assert set(loaded) == {"EARTHDATA_USERNAME", "EARTHDATA_PASSWORD"}  # no devuelve valores, solo claves
    import os
    assert os.environ["EARTHDATA_PASSWORD"] == "clave con espacios"
    assert os.environ["YA_DEFINIDA"] == "original" and "VACIA" not in os.environ


def test_load_env_missing_file_is_fine(tmp_path):
    assert edl.load_env(tmp_path / "no_existe.env") == []


def test_login_without_credentials_fails_clearly(monkeypatch):
    monkeypatch.delenv("EARTHDATA_USERNAME", raising=False)
    monkeypatch.delenv("EARTHDATA_PASSWORD", raising=False)
    monkeypatch.setattr(edl, "load_env", lambda *a, **k: [])
    pytest.importorskip("earthaccess")
    with pytest.raises(RuntimeError, match="EARTHDATA_USERNAME"):
        edl.login()


# --- ventanas ---
def test_window_indices_radius_and_size():
    ii, jj = ew.window_indices(LATS, LONS, 10.0, 20.0, 25.0)
    assert 60 < len(ii) < 110  # ~ pi * (25 km / 5.56 km)^2 = 63
    d = ew.haversine_km(10.0, 20.0, LATS[ii], LONS[jj])
    assert d.max() <= 25.0 and d.min() < 4.5  # el punto cae en la esquina de 4 píxeles de 5.6 km


def test_window_indices_wraps_the_antimeridian_and_poles():
    ii, jj = ew.window_indices(LATS, LONS, 0.0, 179.99, 25.0)
    assert LONS[jj].min() < -179 and LONS[jj].max() > 179  # cruza ±180
    ii, jj = ew.window_indices(LATS, LONS, -89.9, 0.0, 25.0)  # cerca del polo: todas las longitudes
    assert len(set(jj)) > 1000 and np.isfinite(LATS[ii]).all()


def test_window_falls_back_to_nearest_pixel_on_coarse_grid():
    lats, lons = np.arange(-59.875, 90, 0.25), np.arange(-179.875, 180, 0.25)
    ii, jj = ew.window_indices(lats, lons, 10.0, 20.0, 5.0)  # 5 km < 0.25° (28 km)
    assert len(ii) == 1


# --- nieve ---
def test_snow_cell_values_ignore_nodata_codes():
    a = np.full((3600, 7200), 255.0)  # sin dato en todas partes
    cells = pd.DataFrame({"lat": [72.0, 25.0, 46.5], "lon": [-40.0, 15.0, 9.8]})
    w = ew.cell_windows(cells, LATS, LONS)
    r0 = int((90 - 72.0) / 0.05)
    c0 = int((-40.0 + 180) / 0.05)
    a[r0 - 20:r0 + 20, c0 - 20:c0 + 20] = 100.0  # Groenlandia: toda nieve
    r1, c1 = int((90 - 25.0) / 0.05), int((15.0 + 180) / 0.05)
    a[r1 - 20:r1 + 20, c1 - 20:c1 + 20] = 0.0  # Sahara: sin nieve
    # la tercera celda queda con 255 / 211 / 250 -> NaN, no 2.55
    a[int((90 - 46.5) / 0.05) - 5:int((90 - 46.5) / 0.05) + 5, int((9.8 + 180) / 0.05) - 5:int((9.8 + 180) / 0.05) + 5] = 211.0
    out = ew.snow_cell_values(a, w)
    assert out[0] == pytest.approx(1.0) and out[1] == pytest.approx(0.0) and np.isnan(out[2])


def test_snow_mixed_pixels_average():
    a = np.full((3600, 7200), np.nan)
    r, c = int((90 - 60.0) / 0.05), int((10.0 + 180) / 0.05)
    a[r - 30:r + 30, c - 60:c + 60] = 0.0
    a[r - 30:r + 30, c:c + 60] = 100.0  # mitad nieve, mitad sin nieve, con relleno 255 fuera
    a[np.isnan(a)] = 255.0
    w = ew.cell_windows(pd.DataFrame({"lat": [60.0], "lon": [10.0]}), LATS, LONS)
    assert ew.snow_cell_values(a, w)[0] == pytest.approx(0.5, abs=0.05)


def test_annual_summary_with_polar_night_gaps():
    m = np.array([[np.nan, 0.0, 1.0], [np.nan, 0.0, 1.0], [0.4, 0.0, np.nan]])
    s = ew.annual_summary(m)
    assert s["mean"][0] == pytest.approx(0.4) and s["max"][2] == 1.0
    assert list(s["n_valid"]) == [1, 3, 2]
    allnan = ew.annual_summary(np.full((3, 1), np.nan))
    assert np.isnan(allnan["mean"][0]) and allnan["n_valid"][0] == 0


# --- aplicar a la tabla ---
def test_apply_to_earth_keeps_old_proxy_once_and_is_idempotent():
    earth = pd.DataFrame({"cell_id": ["a", "b"], "ice__water_frac": [0.6, 0.1], "lat": [1.0, 2.0]})
    snow = {"mean": np.array([0.9, np.nan]), "max": np.array([1.0, np.nan]), "n_valid": np.array([12, 0])}
    once = ew.apply_to_earth(earth, snow, {"ice_soil_moisture_m3m3": np.array([0.2, 0.3])})
    assert list(once["ice_precip_proxy"]) == [0.6, 0.1]  # el proxy de POWER no se pierde
    assert once["ice__water_frac"].iloc[0] == 0.9 and np.isnan(once["ice__water_frac"].iloc[1])
    twice = ew.apply_to_earth(once, {"mean": np.array([0.5, 0.5]), "max": np.array([0.5, 0.5]),
                                     "n_valid": np.array([12, 12])})
    assert list(twice["ice_precip_proxy"]) == [0.6, 0.1]  # la segunda corrida no guarda el valor de nieve como "proxy"
    assert list(twice["ice__water_frac"]) == [0.5, 0.5]


def test_reduced_cache_key_depends_on_cells():
    a = pd.DataFrame({"lat": [1.0], "lon": [2.0]})
    b = pd.DataFrame({"lat": [1.0], "lon": [2.1]})
    assert ew._key(a, 25.0) == ew._key(a.copy(), 25.0) and ew._key(a, 25.0) != ew._key(b, 25.0)
    assert ew._key(a, 25.0) != ew._key(a, 30.0)
