import numpy as np
import pandas as pd

from astroatlas.stability import run as stability_run
from astroatlas.synthetic import synthetic_earth, synthetic_target
from astroatlas.validation_ext import boot_mean, summarize_groups


def test_boot_mean_ci_contains_mean_and_handles_nan():
    m, lo, hi = boot_mean(np.array([0.4, 0.6, 0.8, np.nan]))
    assert lo <= m <= hi and np.isclose(m, 0.6)
    m1, lo1, hi1 = boot_mean(np.array([0.7]))
    assert m1 == 0.7 and np.isnan(lo1) and np.isnan(hi1)


def test_summarize_groups_splits_original_and_new():
    raw = pd.DataFrame({"body": "mars", "config": "all", "target": "t", "analog": ["a", "b", "c", "d"], "u": [0.9, 0.7, 0.4, 0.6]})
    known = pd.DataFrame({"name": list("abcd"), "group": ["original", "original", "nuevo", "nuevo"]})
    s = summarize_groups(raw, known).query("config == 'all' and body == 'mars'").set_index("grupo")
    assert s.loc["originales", "n_analogs"] == 2 and np.isclose(s.loc["originales", "u_medio"], 0.8)
    assert s.loc["nuevos", "n_analogs"] == 2 and np.isclose(s.loc["todos", "u_medio"], 0.65)


def test_stability_frequencies_are_valid(tmp_path):
    earth = synthetic_earth().assign(viable=True, vegetated=False)
    earth.to_parquet(tmp_path / "earth.parquet", index=False)
    sites = pd.read_csv("docs/catalog/target_sites.csv")
    for b in ("moon", "mars"):
        synthetic_target(b, sites).to_parquet(tmp_path / f"{b}.parquet", index=False)
    r = stability_run("mars", n_rep=4, features_dir=tmp_path)
    assert r["freq_top5"].between(0, 1).all() and r["mean_rank_pct"].between(0, 1).all()
    assert (r["freq_top5"] > 0).any()          # algunas celdas siempre llegan al 5 % superior


def test_inertia_percentile_window_and_proxy():
    from astroatlas import config
    from astroatlas.inertia import earth_proxy, extra_dimension, percentile, window_median

    ref = np.sort(np.array([10.0, 20, 30, 40]))
    p = percentile(np.array([5.0, 25.0, 100.0, np.nan]), ref)
    assert p[0] == 0.0 and p[1] == 0.5 and p[2] == 1.0 and np.isnan(p[3])
    px = earth_proxy(np.array([2.0, 0.0, -1.0, np.nan]))
    assert px[0] == 0.5 and np.isnan(px[1:]).all()
    ti = np.full((3600, 7200), np.nan, dtype="float32")
    ti[1800:1802, 3600:3602] = 300.0
    assert window_median(ti, 0.0, 0.0) == 300.0               # longitude 0 and 360 are the same point
    assert window_median(ti, 0.0, 360.0) == 300.0
    assert np.isnan(window_median(ti, 45.0, 90.0))


def test_extra_dimension_restores_global_state():
    from astroatlas import ablation, config
    from astroatlas.inertia import FEATURE, extra_dimension

    dims, feats, weights, abl = list(config.DIMENSIONS), list(config.FEATURES), dict(config.DEFAULT_WEIGHTS), list(ablation.DIMS)
    with extra_dimension():
        assert "inertia" in config.DIMENSIONS and FEATURE in config.FEATURES and "inertia" in ablation.DIMS
    assert list(config.DIMENSIONS) == dims and list(config.FEATURES) == feats
    assert config.DEFAULT_WEIGHTS == weights and ablation.DIMS == abl


def test_emissivity_contrast_and_gates():
    from astroatlas.emissivity import contrast_index, gates, litho_sites

    assert np.isclose(contrast_index(0.90, 0.96, 0.98), -0.07)
    l = litho_sites()
    assert l["basalt"].sum() == 10 and (l["basalt"] == 0).sum() == 10 and l["name"].is_unique
    l["c"] = np.where(l["basalt"] == 1, 0.0, -0.1)            # perfect separation
    small = pd.DataFrame({"name": list("abc"), "c": [-0.01, -0.2, -0.05]})
    g = gates(l, np.array([0.0, 0.0, np.nan]), small)
    assert g["auc"] == 1.0 and g["puerta2"] and g["small_above_median"] == 2 and g["puerta3"]
    assert g["puerta1"] is False


def test_multiscale_hurst_recovers_power_law():
    from astroatlas.multiscale import FLOOR_M, add_multiscale, hurst

    L = np.array([1.0, 2.0, 5.0])
    rough = np.vstack([3.0 * L ** 0.7, 0.5 * L ** 0.3])
    assert np.allclose(hurst(rough), [0.7, 0.3])
    assert np.isfinite(hurst(np.zeros((1, 3)))).all()                  # zero roughness: bounded below, no infinities
    df = pd.DataFrame({"topo__rough_1km_m": [3.0], "topo__rough_2km_m": [4.9], "topo__rough_5km_m": [9.0], "topo__slope_mean_deg": [1.0]})
    out = add_multiscale(df)
    assert {"ms_hurst", "ms_lnr1", "ms_lnslope"} <= set(out.columns) and np.isclose(out["ms_lnslope"].iloc[0], np.log(1.1)) and FLOOR_M > 0


def test_variability_offsets_and_pole_reflection():
    from astroatlas.variability import calibrated_model, offset_point, window_offsets

    lat, lon = offset_point(0.0, 10.0, 0.0, 25.0, 3396.0)               # 25 km east on the equator of Mars
    assert abs(lat) < 1e-9 and np.isclose(lon - 10.0, 25.0 / (3396.0 * np.pi / 180.0))
    lat, lon = offset_point(89.9, 0.0, 25.0, 0.0, 1737.4)               # to the north it passes the pole: it is mirrored
    assert 89.0 < lat < 90.0 and np.isclose(abs(lon), 180.0)
    assert len(window_offsets(10.0)) == 9 and len(window_offsets(-89.9)) == 3
    from astroatlas.similarity import TopoModel
    m = TopoModel(["a", "b"], pd.Series([0.0, 0.0], index=["a", "b"]), pd.Series([1.0, 1.0], index=["a", "b"]), np.eye(2), np.ones(2), np.array([0.5, 1.0]))
    c = calibrated_model(m, [3.0, 0.0])
    assert np.allclose(c.scale, [np.sqrt(10.0), 1.0])
    d = pd.DataFrame({"a": [2.0], "b": [2.0]})
    assert np.allclose(c.transform(d).to_numpy(), [[2.0 / np.sqrt(10.0), 2.0]])   # the difference is divided by sqrt(1 + s^2)


def test_variability_target_spread_and_fallback():
    from astroatlas.similarity import TopoModel
    from astroatlas.variability import target_spread

    m = TopoModel(["a", "b"], pd.Series([0.0, 0.0], index=["a", "b"]), pd.Series([1.0, 1.0], index=["a", "b"]), np.eye(2), np.ones(2), np.array([0.5, 1.0]))
    g1 = pd.DataFrame({"site": "A", "lat": 10.0, "valid_frac": 1.0, "a": np.arange(9.0), "b": np.zeros(9)})
    g2 = pd.DataFrame({"site": "B", "lat": 10.0, "valid_frac": [1.0] * 3 + [0.0] * 6, "a": np.arange(9.0), "b": np.arange(9.0)})
    w = pd.concat([g1, g2], ignore_index=True)
    s = target_spread(w, m)
    assert s.loc["A", "calibrado"] and np.isclose(s.loc["A", "s1"], np.arange(9.0).std(ddof=1)) and s.loc["A", "s2"] == 0.0
    assert not s.loc["B", "calibrado"] and s.loc["B", "s1"] == 0.0     # only 3 valid windows out of 9: not calibrated


def test_grupos_rules_and_exact_test():
    from astroatlas.groups import COLD_LAT, COLD_TMAX_K, cold_analogs, exact_sign_flip_p, split_targets

    assert exact_sign_flip_p(np.array([0.1, 0.2, 0.3, 0.4, 0.5])) == 1 / 32          # the 5 positives: minimum p
    assert exact_sign_flip_p(np.array([-0.1, -0.2, -0.3])) == 1.0
    sites = pd.DataFrame({"name": ["cold", "justo", "calido", "moon_only"], "thermal__t_max_k": [280.0, COLD_TMAX_K, 320.0, 270.0]})
    known = pd.DataFrame({"name": ["cold", "justo", "calido", "moon_only"], "analog_of": ["mars", "mars", "moon+mars", "moon"]})
    assert cold_analogs(sites, known) == ["cold"]                                   # 295 K is not cold (strict <); the Moon is ignored
    prof = pd.DataFrame(index=["polar", "borde", "tropical"])
    lat = pd.Series({"polar": 68.0, "borde": COLD_LAT, "tropical": 5.0})
    cold, warm = split_targets(prof, lat)
    assert cold == ["polar", "borde"] and warm == ["tropical"]


def test_modelos_percentiles_and_max_over():
    from astroatlas.models import max_over, percentile_below, rank_pct

    v = np.array([1.0, 2.0, 2.0, 4.0, np.nan])
    assert percentile_below(v, 2.0) == (1 + 0.5 * 2) / 4 and np.isnan(percentile_below(v, np.nan))
    r = rank_pct(v)
    assert np.isclose(r[0], 0.125) and np.isclose(r[1], r[2]) and np.isnan(r[4]) and r[3] > r[1]
    S = np.array([[0.2, 0.9], [np.nan, np.nan], [0.5, 0.1]])
    out = max_over(S, [0, 1])
    assert out[0] == 0.9 and np.isnan(out[1]) and out[2] == 0.5
    assert np.isnan(max_over(S, [])).all()


def test_polar_ice_season_rule_lookup_and_index():
    from astroatlas.polar_ice import H_ICE, hydrogen_index, lookup, selected

    assert selected(10.0, 0, 15) and selected(-39.0, 300, 315)                      # |lat| < 40: all intervals
    assert selected(68.0, 105, 120) and selected(68.0, 150, 165) and not selected(68.0, 90, 105) and not selected(68.0, 165, 180)
    assert selected(-60.0, 285, 300) and not selected(-60.0, 105, 120)              # the south uses its own summer
    cells = pd.DataFrame({"lat": [87.5, 2.5, -2.5, 2.5], "lon": [2.5, 7.5, 7.5, 2.5], "cepi": [2.0, 8.0, 8.0, 4.0], "n_obs": [1, 1, 1, 1]})
    out = hydrogen_index(cells)
    ref = out.attrs["cepi_ref"]
    assert np.isclose(ref, 8.0)                                                      # median of the cells with |lat| < 30
    c = lookup(out, 3.0, 8.0)
    assert c["lat"] == 2.5 and c["lon"] == 7.5 and np.isclose(c["H"], -np.log(8.0 / ref))
    assert abs(H_ICE - np.log(1.5)) < 1e-12 and lookup(out, 88.0, 361.0)["lat"] == 87.5   # 361° E = 1° E: misma celda


def test_permafrost_annual_mean_alignment_and_class():
    import pytest

    from astroatlas.permafrost import align, annual_mean_k, to_class

    day = np.full((12, 2), 280.0)
    night = np.full((12, 2), 260.0)
    day[:7, 1] = np.nan                                    # only 5 valid months: no mean
    m = annual_mean_k(day, night)
    assert np.isclose(m[0], 270.0) and np.isnan(m[1])
    assert to_class(pd.Series([270.9, 271.0, np.nan])).tolist()[:2] == [1.0, 0.0]
    cache = np.array([300.0, 310.0, 320.0, 330.0])          # the current table lost the 2nd cell
    assert align(cache, np.array([300.0, 320.0, 330.0])) == [0, 2, 3]
    with pytest.raises(RuntimeError):
        align(cache, np.array([300.0, 999.0]))
