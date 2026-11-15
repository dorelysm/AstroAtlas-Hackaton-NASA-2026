"""Network-free tests of earth_geology.py."""
import zipfile

import numpy as np
import pandas as pd
import pytest

from astroatlas.data import earth_geology as eg

NAMES = {1: "su", 2: "vb", 3: "ss", 4: "pb", 5: "wb", 6: "ig", 7: "nd"}
LATS = 90 - 0.5 * (np.arange(360) + 0.5)
LONS = -180 + 0.5 * (np.arange(720) + 0.5)


def _grid(fill=1):
    return np.full((360, 720), fill, dtype=int)


def _cell(lat, lon):
    return int((90 - lat) / 0.5), int((lon + 180) / 0.5)


def test_basalt_fraction_counts_only_rock_cells():
    g = _grid(1)  # all sediments
    r, c = _cell(10.0, 20.0)
    g[:, :c] = 2                   # basalt west of the central cell; sediments to the east
    wet = g.copy()
    wet[r, c] = 5                  # one of the 4 cells of the window (2 x 2) is water: it does NOT count as rock
    cells = pd.DataFrame({"lat": [10.0], "lon": [20.0]})
    dry = eg.geology_features(cells, g, NAMES, LATS, LONS, half_km=75)
    wetf = eg.geology_features(cells, wet, NAMES, LATS, LONS, half_km=75)
    assert 0.15 < dry["geo__basalt_frac"].iloc[0] < 0.55          # part of the window is basalt
    assert wetf["geo_glim_rock_cells"].iloc[0] < dry["geo_glim_rock_cells"].iloc[0]  # the water leaves the denominator
    assert wetf["geo__basalt_frac"].iloc[0] > dry["geo__basalt_frac"].iloc[0]       # and that is why the fraction goes up


def test_pure_basalt_pure_sediment_and_mafic_plutonic():
    g = _grid(1)
    g[:, :100] = 2          # lon -180..-130: basalto
    g[:, 100:200] = 4       # lon -130..-80: gabbro (mafic, but not basalt)
    cells = pd.DataFrame({"lat": [0.0, 0.0, 0.0], "lon": [-170.0, -100.0, 50.0]})
    f = eg.geology_features(cells, g, NAMES, LATS, LONS)
    assert list(f["geo__basalt_frac"]) == [1.0, 0.0, 0.0]
    assert list(f["geo_glim_mafic_frac"]) == [1.0, 1.0, 0.0]  # gabbro counts as mafic
    assert list(f["geo_glim_class"]) == ["vb", "pb", "su"]


def test_ice_water_and_nodata_give_nan_not_zero():
    g = _grid(6)             # ice everywhere
    g[:, 300:] = eg.NODATA   # ocean / no data
    cells = pd.DataFrame({"lat": [72.0, 0.0], "lon": [-100.0, 100.0]})
    f = eg.geology_features(cells, g, NAMES, LATS, LONS)
    assert f["geo__basalt_frac"].isna().all() and (f["geo_glim_rock_cells"] == 0).all()
    assert f["geo_glim_class"].isna().all()


def test_apply_to_earth_is_idempotent():
    earth = pd.DataFrame({"cell_id": ["a", "b"], "geo__basalt_frac": [np.nan, np.nan]})
    geo = pd.DataFrame({"geo__basalt_frac": [1.0, 0.0], "geo_glim_class": ["vb", "su"]})
    once = eg.apply_to_earth(earth, geo)
    assert list(once["geo__basalt_frac"]) == [1.0, 0.0]
    assert eg.apply_to_earth(once, geo).equals(once)


def test_load_glim_parses_header_and_orientation(tmp_path):
    (tmp_path / eg.CLASSES_NAME).write_text('"OBJECTID";"Value_";"Count_";"xx"\n1;1;10.0;"su"\n2;2;5.0;"vb"\n')
    rows = ["ncols 4", "nrows 2", "xllcorner -180", "yllcorner -90", "cellsize 90", "NODATA_value -9999",
            "2 1 1 1", "-9999 1 1 2"]
    (tmp_path / eg.GRID_NAME).write_text("\n".join(rows) + "\n")
    grid, names, lats, lons = eg.load_glim(tmp_path)
    assert grid.shape == (2, 4) and names == {1: "su", 2: "vb"}
    assert list(lats) == [45.0, -45.0] and list(lons) == [-135.0, -45.0, 45.0, 135.0]  # fila 0 = norte
    assert grid[0, 0] == 2 and grid[1, 0] == eg.NODATA


def test_safe_extract_blocks_zip_slip(tmp_path):
    bad = tmp_path / "bad.zip"
    with zipfile.ZipFile(bad, "w") as z:
        z.writestr("../escapado.txt", "must not leave the folder")
    with pytest.raises(ValueError, match="suspicious"):
        eg.safe_extract(bad, tmp_path / "out")
    assert not (tmp_path / "escapado.txt").exists()
    ok = tmp_path / "ok.zip"
    with zipfile.ZipFile(ok, "w") as z:
        z.writestr("data.txt", "hola")
    eg.safe_extract(ok, tmp_path / "out2")
    assert (tmp_path / "out2" / "data.txt").read_text() == "hola"
