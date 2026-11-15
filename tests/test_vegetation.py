import numpy as np
import pandas as pd

from astroatlas.data.earth_vegetation import add_vegetated, annual_ndvi
from astroatlas.pipeline import attach_viability
from astroatlas.validate import novel_candidates


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
    assert novel_candidates(ranked, known, n=10, unvegetated_only=True)["cell_id"].tolist() == ["b", "c"]  # NaN is not discarded


def test_attach_viability_carries_vegetation_columns():
    earth = pd.DataFrame({"cell_id": ["a"], "viable": [True], "veg_ndvi_max": [0.3], "vegetated": [True]})
    out = attach_viability(pd.DataFrame({"cell_id": ["a"], "score": [1.0]}), earth)
    assert {"viable", "veg_ndvi_max", "vegetated"} <= set(out.columns)


def test_nearest_index_circular_longitude():
    from astroatlas.data.earth_dust_wind import nearest_index

    lons = np.array([-180.0, -179.375, 179.375])
    assert nearest_index(lons, np.array([179.9]), period=360.0)[0] == 0   # 179.9 is closer to -180 than to 179.375 circularly
    assert nearest_index(np.array([0.0, 10.0]), np.array([4.0, 6.0])).tolist() == [0, 1]


def test_add_pit_context_counts_and_nearest():
    from astroatlas.data.caves import add_pit_context

    pits = pd.DataFrame({"name": ["A", "B"], "lat": [0.0, 10.0], "lon": [0.0, 359.9]})
    df = pd.DataFrame({"lat": [0.1, 10.0, -50.0], "lon": [0.0, 0.1, 100.0]})
    out = add_pit_context(df, pits)
    assert out["pits_within_50km"].tolist() == [1, 1, 0]            # the 2nd crosses the 0/360 meridian: B is ~22 km away
    assert out["nearest_pit_name"].tolist()[:2] == ["A", "B"]
    assert out["nearest_pit_km"].iloc[2] > 1000
    assert add_pit_context(out, pits)["pits_within_50km"].tolist() == [1, 1, 0]   # idempotente


def test_load_mars_caves_ignores_misordered_header(tmp_path):
    from astroatlas.data.caves import MARS_COLUMNS, add_pit_context, load_mars_caves

    f = tmp_path / "c.csv"
    f.write_text("longitude:string,latitude:string,Label:string\nAPC001,240.4585,-0.94678,APC,1,25,32,\"APC, tiny\"\n"
                 "CC0002,10.0,5.0,sky,2,,,x\n", encoding="utf-8")
    c = load_mars_caves(f)
    assert c["name"].tolist() == ["APC001", "CC0002"] and abs(c["lon"][0] - 240.4585) < 1e-9 and abs(c["lat"][0] + 0.94678) < 1e-9
    out = add_pit_context(pd.DataFrame({"lat": [-0.9], "lon": [240.4]}), c, columns=MARS_COLUMNS)
    assert out["caves_within_50km"].iloc[0] == 1 and out["nearest_cave_name"].iloc[0] == "APC001"


def test_region_grid_cell_centers_and_ids():
    from astroatlas.zoom import region_grid

    g = region_grid((29.0, 30.0), (34.0, 35.0), 0.25, "t")
    assert len(g) == 16 and g["cell_id"].is_unique and g["cell_id"].iloc[0] == "zoom_t_0_0"
    assert np.isclose(g["lat"].min(), 29.125) and np.isclose(g["lon"].max(), 34.875) and (g["body"] == "earth").all()
