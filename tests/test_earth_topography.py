"""Tests del lector Copernicus y de la topografía de la Tierra con un DEM falso (sin red)."""
import re

import numpy as np
import pytest

pytest.importorskip("rasterio")

from analogos.data import earth
from analogos.data.copernicus import MAX_TILES, CopernicusDem, tile_name, tile_url
from analogos.data.dem import site_topography
from analogos.features import validate_features

R = CopernicusDem.radius_m
SLOPE = 0.1


class FakeDem(CopernicusDem):
    """Teselas de 1° con un plano que sube hacia el norte (pendiente 0.1 = 5.71°)."""

    def __init__(self, missing=lambda la, lo: False):
        super().__init__()
        self.missing = missing

    def _load_tile(self, name):
        m = re.match(r".*_([NS])(\d+)_00_([EW])(\d+)_00_DEM", name)
        la = int(m[2]) * (1 if m[1] == "N" else -1)
        lo = int(m[4]) * (1 if m[3] == "E" else -1)
        if self.missing(la, lo):
            return None
        n = 310
        d = 1.0 / n
        lats = la + 1 - (np.arange(n) + 0.5) * d
        arr = np.tile((SLOPE * R * np.radians(lats))[:, None], (1, n))
        return arr, float(lo), float(la + 1), d, d


def test_tile_names():
    assert tile_name(-25, -70) == "Copernicus_DSM_COG_30_S25_00_W070_00_DEM"
    assert tile_name(45, 10) == "Copernicus_DSM_COG_30_N45_00_E010_00_DEM"
    assert tile_name(-90, 0) == "Copernicus_DSM_COG_30_S90_00_E000_00_DEM"
    assert tile_name(0, -1) == "Copernicus_DSM_COG_30_N00_00_W001_00_DEM"
    assert tile_url(tile_name(45, 10)).endswith("/Copernicus_DSM_COG_30_N45_00_E010_00_DEM.tif")


def test_plane_slope_across_tile_boundary():
    dem = FakeDem()
    # 40.0° N es el borde entre dos teselas: la ventana de ±25 km (~0.22°) cruza ambas
    f = site_topography(dem, 40.0, 10.5)
    assert f["topo__slope_mean_deg"] == pytest.approx(np.degrees(np.arctan(SLOPE)), abs=0.15)
    assert f["valid_frac"] == 1.0
    assert f["baseline_m"] == 500.0  # base común con Luna y Marte
    assert f["topo__aspect_equatorward"] == pytest.approx(1.0, abs=0.01)  # sube al norte: ladera mira al sur


def test_elevation_matches_plane():
    dem = FakeDem()
    lat, lon = np.array([40.3, -12.7]), np.array([10.2, 170.9])
    assert dem.elevation(lat, lon) == pytest.approx(SLOPE * R * np.radians(lat), abs=5.0)


def test_missing_tile_is_nan():
    dem = FakeDem(missing=lambda la, lo: la == 40)  # océano al norte de 40°
    z = dem.elevation(np.array([39.5, 40.5]), np.array([10.2, 10.2]))
    assert np.isfinite(z[0]) and np.isnan(z[1])
    f = site_topography(dem, 40.0, 10.5)
    assert 0.3 < f["valid_frac"] < 0.7


def test_window_over_too_many_tiles_is_nan():
    lat = np.linspace(0, MAX_TILES + 4, 50)
    assert np.isnan(FakeDem().elevation(lat, np.zeros(50))).all()


def test_build_features_drops_ocean_and_meets_contract(monkeypatch):
    # tierra solo en el hemisferio norte; el sur es océano (sin tesela)
    monkeypatch.setattr(earth, "CopernicusDem", lambda: FakeDem(missing=lambda la, lo: la < 0))
    df = earth.build_features(step_deg=30, workers=1, topo=True, power=False)
    validate_features(df, "earth")
    assert len(df) > 0 and (df["lat"] > 0).all()
    assert df["topo__slope_mean_deg"].notna().all()
    assert df["thermal__t_max_k"].isna().all()  # POWER desactivado


def test_known_analog_cells_have_contract_columns():
    cells = earth.known_analog_cells()
    assert {"cell_id", "body", "lat", "lon", "name"} <= set(cells.columns)
    assert cells["cell_id"].is_unique and len(cells) >= 10


def test_flat_water_is_detected_at_any_altitude_but_real_flat_land_is_kept():
    import pandas as pd

    df = pd.DataFrame({
        "topo__relief_m": [0.0, 0.3, 4.0, 5.0, 0.0, 4.15, 500.0],
        "elev_mean_m": [0.0, 0.5, 1.0, 55.0, 174.0, 3050.0, 0.0],
    })  # mar, mar, polder holandés, plataforma de hielo, lago (Michigan), meseta antártica, costa montañosa
    assert list(earth.is_flat_water(df)) == [True, True, False, False, True, False, False]
    assert earth.is_flat_ocean is earth.is_flat_water  # el nombre anterior sigue funcionando
