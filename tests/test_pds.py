"""Network-free tests of pds_dem.py, planetary.py and the merge with dem.py (retries)."""
import numpy as np
import pandas as pd
import pytest

from astroatlas.config import FEATURES
from astroatlas.data import dem as dem_mod
from astroatlas.data import planetary
from astroatlas.data.dem import build_target_features, site_topography
from astroatlas.data.pds_dem import PdsTiledDem, Tile, lola_dem, mola_dem

PPD = 4
R = 100_000.0


class FakeTiledDem(PdsTiledDem):
    """90°-wide tiles with a plane rising towards the north (z = 100 * lat)."""

    def __init__(self, lat_limit=90.0):
        tiles = [Tile(f"fake/t{la}_{lo}.img", la, la - 90, lo, lo + 180)
                 for la in (90, 0) for lo in (0, 180)]
        super().__init__(tiles, ppd=PPD, dtype="<i2", scale=1.0, radius_m=R, lat_limit=lat_limit)

    def _rows(self, tile, r0, r1):
        ncols = int(round((tile.lon_max - tile.lon_min) * self.ppd))
        lats = tile.lat_max - (np.arange(r0, r1) + 0.5) / self.ppd
        return np.tile((100 * lats)[:, None], (1, ncols)).astype("int16")


def test_factories_have_expected_resolution():
    assert lola_dem().res_m == pytest.approx(118.45, abs=0.05)
    assert mola_dem().res_m == pytest.approx(463.06, abs=0.05)
    assert mola_dem().lat_limit == 88.0


def test_pds_dem_elevation_plane_and_longitude_wrap():
    dem = FakeTiledDem()
    lat = np.array([10.0, -33.3, 47.1, 10.0, 10.0])
    lon = np.array([45.0, 200.0, 359.9, 0.1, 180.0])  # includes the 0/360 crossing and the edge between tiles
    assert dem.elevation(lat, lon) == pytest.approx(100 * lat, abs=30)  # ~1 px (0.25°) of tolerance
    assert dem.elevation(np.array([10.0]), np.array([-1.0])) == pytest.approx(
        dem.elevation(np.array([10.0]), np.array([359.0])))  # lon negativa == lon + 360


def test_pds_dem_latitude_limit_is_nan():
    z = FakeTiledDem(lat_limit=88.0).elevation(np.array([89.0, 80.0]), np.array([10.0, 10.0]))
    assert np.isnan(z[0]) and np.isfinite(z[1])


def test_site_topography_on_pds_dem_object():
    f = site_topography(FakeTiledDem(), 20.0, 359.0, half_km=3, baseline_m=1000)
    # slope = 100 m per degree of latitude = 100 / (R·pi/180 m) = 0.0573 -> 3.28°
    assert f["topo__slope_mean_deg"] == pytest.approx(np.degrees(np.arctan(100 / (R * np.pi / 180))), abs=0.1)


# --- merge with dem.py: retries ---
SITES = pd.DataFrame({"site": ["A", "B"], "body": ["moon", "moon"], "lat": [10.0, 20.0],
                      "lon": [30.0, 40.0], "kind": ["landing", "landing"]})


class FlakyDem(FakeTiledDem):
    def __init__(self, fail_first=1, always_fail_for=None):
        super().__init__()
        self.calls, self.fail_first, self.always = 0, fail_first, always_fail_for

    def elevation(self, lat, lon):
        self.calls += 1
        if self.always is not None and abs(np.mean(lat) - self.always) < 1:
            raise OSError("permanent outage")
        if self.calls <= self.fail_first:
            raise OSError("ConnectionReset")
        return super().elevation(lat, lon)


def test_retry_recovers_from_transient_network_error(monkeypatch):
    monkeypatch.setattr(dem_mod.time, "sleep", lambda s: None)
    out = build_target_features("moon", FlakyDem(fail_first=2), SITES, half_km=3, baseline_m=1000)
    assert list(out["site"]) == ["A", "B"] and out["topo__slope_mean_deg"].notna().all()
    assert set(FEATURES) <= set(out.columns) and (out["kind"] == "landing").all()


def test_site_that_keeps_failing_is_skipped_with_warning(monkeypatch, capsys):
    monkeypatch.setattr(dem_mod.time, "sleep", lambda s: None)
    out = build_target_features("moon", FlakyDem(fail_first=0, always_fail_for=20.0), SITES, half_km=3,
                                baseline_m=1000)
    assert list(out["site"]) == ["A"]  # B is skipped, A survives
    assert "WARNING" in capsys.readouterr().out


# --- planetary.py (funciones puras) ---
def test_basalt_proxy():
    assert planetary._basalt(5.0) == 0.0 and planetary._basalt(20.0) == 1.0
    assert planetary._basalt(12.5) == pytest.approx(0.5)
    assert planetary._basalt(30.0) == 1.0 and np.isnan(planetary._basalt(np.nan))


def test_great_circle_and_lon180():
    assert planetary._gc_km(0, 0, 0, 90, 1737.4) == pytest.approx(1737.4 * np.pi / 2, rel=1e-6)
    assert planetary._lon180(np.array([190.0, 350.0, 10.0])) == pytest.approx([-170.0, -10.0, 10.0])


@pytest.mark.parametrize("lat,expected", [(-85.98, "global_cumul_avg_cyl_90s80s_002.tab"),
                                          (-3.0, "global_cumul_avg_cyl_10s00s_002.tab"),
                                          (0.67, "global_cumul_avg_cyl_00n10n_002.tab"),
                                          (26.1, "global_cumul_avg_cyl_20n30n_002.tab")])
def test_diviner_file_naming(lat, expected):
    assert planetary._gcp_file(lat)[0] == expected


# --- ice: NaN outside the coverage, never an assumed 0 ---
@pytest.mark.parametrize("lat", [-79.9, -80.0, -45.0, 0.0, 26.1, 85.0])
def test_moon_ice_outside_diviner_prp_is_nan_not_zero(lat):
    r = planetary.moon_ice(lat, 10.0)  # it downloads nothing: it exits before reading the file
    assert np.isnan(r["ice__water_frac"]) and "no data" in r["ice_note"]


def test_mars_ice_cell_without_data_is_nan_with_explanation():
    planetary._ody["h2o_sr_5x5.tab"] = pd.DataFrame({
        "lat": [47.5, 17.5], "lon": [-162.5, 77.5], "val": [np.nan, 3.5], "sigma": [np.nan, 0.4]})
    try:
        arcadia = planetary.mars_ice(47.25, 196.0)  # 196° E = -164° -> cell without data
        jezero = planetary.mars_ice(18.38, 77.58)
    finally:
        planetary._ody.pop("h2o_sr_5x5.tab")
    assert np.isnan(arcadia["ice__water_frac"]) and "±57.5" in arcadia["ice_note"]
    assert jezero["ice__water_frac"] == pytest.approx(0.035)
