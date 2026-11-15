"""Tests sin red de earth_thermal.py (con un HDF4 pequeño escrito en el momento)."""
import numpy as np
import pandas as pd
import pytest

pytest.importorskip("pyhdf")
from pyhdf.SD import SD, SDC  # noqa: E402

from analogos.data import earth_thermal as et  # noqa: E402
from analogos.data.earth_water import cell_windows  # noqa: E402


def _write_hdf(path, day_dn, night_dn):
    sd = SD(str(path), SDC.WRITE | SDC.CREATE)
    for name, dn in ((et.DAY_VAR, day_dn), (et.NIGHT_VAR, night_dn)):
        ds = sd.create(name, SDC.UINT16, dn.shape)
        ds.scale_factor = 0.02
        ds.valid_range = [7500, 65535]
        ds[:] = dn.astype("uint16")
        ds.endaccess()
    sd.end()


def test_read_lst_hdf_scales_and_masks_fill(tmp_path):
    day = np.full((6, 8), 16000)            # 16000 * 0.02 = 320 K
    night = np.full((6, 8), 14000)          # 280 K
    day[0, 0], night[1, 1] = 0, 5000        # relleno (0) y por debajo del rango válido (< 7500)
    p = tmp_path / "lst.hdf"
    _write_hdf(p, day, night)
    d, n = et.read_lst_hdf(p)
    assert d[2, 2] == pytest.approx(320.0) and n[2, 2] == pytest.approx(280.0)
    assert np.isnan(d[0, 0]) and np.isnan(n[1, 1])
    p.unlink()  # el archivo debe quedar cerrado: en Windows falla si no


def test_lst_cell_values_and_annual_thermal():
    lats, lons = 90 - 0.05 * (np.arange(3600) + 0.5), -180 + 0.05 * (np.arange(7200) + 0.5)
    cells = pd.DataFrame({"lat": [36.25, -77.5], "lon": [-116.8, 162.0]})
    w = cell_windows(cells, lats, lons)
    months = []
    for day_k, night_k in [(300.0, 280.0), (326.0, 309.0), (310.0, 290.0)]:
        day = np.full((3600, 7200), np.nan)
        night = np.full((3600, 7200), np.nan)
        for (la, lo) in [(36.25, -116.8)]:  # solo la primera celda tiene dato; la segunda queda en NaN
            r, c = int((90 - la) / 0.05), int((lo + 180) / 0.05)
            day[r - 30:r + 30, c - 30:c + 30], night[r - 30:r + 30, c - 30:c + 30] = day_k, night_k
        months.append(et.lst_cell_values(day, night, w))
    th = et.annual_thermal(np.vstack(months))
    assert th["t_max_k"][0] == pytest.approx(326.0)                           # máximo de las medias diurnas mensuales
    assert th["t_range_k"][0] == pytest.approx(np.mean([20.0, 17.0, 20.0]))   # media de (día - noche)
    assert th["night_min_k"][0] == pytest.approx(280.0) and th["months_valid"][0] == 3
    assert np.isnan(th["t_max_k"][1]) and th["months_valid"][1] == 0          # sin dato: NaN, no 0


def test_apply_to_earth_keeps_air_temperature_once():
    earth = pd.DataFrame({"thermal__t_max_k": [300.0, 280.0], "thermal__t_range_k": [30.0, 20.0]})
    th = {"t_max_k": np.array([326.0, np.nan]), "t_range_k": np.array([17.0, np.nan]),
          "night_min_k": np.array([280.0, np.nan]), "months_valid": np.array([12, 0])}
    once = et.apply_to_earth(earth, th)
    assert list(once["thermal_air_t_max_k"]) == [300.0, 280.0]  # el aire de POWER no se pierde
    assert once["thermal__t_max_k"].iloc[0] == 326.0 and np.isnan(once["thermal__t_max_k"].iloc[1])
    twice = et.apply_to_earth(once, {**th, "t_max_k": np.array([1.0, 2.0])})
    assert list(twice["thermal_air_t_max_k"]) == [300.0, 280.0]  # la segunda corrida no lo sobrescribe
