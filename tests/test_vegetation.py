import numpy as np
import pandas as pd

from analogos.data.earth_vegetation import add_vegetated, annual_ndvi
from analogos.pipeline import attach_viability
from analogos.validate import novel_candidates


def test_annual_ndvi_mean_max_ignoring_nan():
    m = np.array([[0.1, np.nan], [0.3, np.nan], [0.2, np.nan]])
    r = annual_ndvi(m)
    assert np.isclose(r["veg_ndvi_mean"][0], 0.2) and np.isclose(r["veg_ndvi_max"][0], 0.3)
    assert np.isnan(r["veg_ndvi_mean"][1]) and np.isnan(r["veg_ndvi_max"][1])


def test_vegetated_threshold_and_nan_not_vegetated():
    d = add_vegetated(pd.DataFrame({"veg_ndvi_max": [0.19, 0.2, 0.7, np.nan]}))
    assert d["vegetated"].tolist() == [False, True, True, False]
    assert d["vegetated"].dtype == bool


def test_add_vegetated_drops_old_barren_column():
    d = add_vegetated(pd.DataFrame({"veg_ndvi_max": [0.1], "barren": [True]}))
    assert "barren" not in d.columns


def test_novel_candidates_unvegetated_only():
    ranked = pd.DataFrame({"cell_id": list("abc"), "lat": [0.0, 10, 20], "lon": [0.0, 0, 0], "score": [0.9, 0.8, 0.7],
                           "rank": [1, 2, 3], "vegetated": [True, False, np.nan]})
    known = pd.DataFrame({"name": ["k"], "lat": [-80.0], "lon": [100.0]})
    assert novel_candidates(ranked, known, n=10)["cell_id"].tolist() == ["a", "b", "c"]
    assert novel_candidates(ranked, known, n=10, unvegetated_only=True)["cell_id"].tolist() == ["b", "c"]  # NaN no se descarta


def test_attach_viability_carries_vegetation_columns():
    earth = pd.DataFrame({"cell_id": ["a"], "viable": [True], "veg_ndvi_max": [0.3], "vegetated": [True]})
    out = attach_viability(pd.DataFrame({"cell_id": ["a"], "score": [1.0]}), earth)
    assert {"viable", "veg_ndvi_max", "vegetated"} <= set(out.columns)


def test_nearest_index_circular_longitude():
    from analogos.data.earth_dust_wind import nearest_index

    lons = np.array([-180.0, -179.375, 179.375])
    assert nearest_index(lons, np.array([179.9]), period=360.0)[0] == 0   # 179.9 está más cerca de -180 que de 179.375 circularmente
    assert nearest_index(np.array([0.0, 10.0]), np.array([4.0, 6.0])).tolist() == [0, 1]
