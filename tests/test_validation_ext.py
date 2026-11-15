import numpy as np
import pandas as pd

from analogos.stability import run as stability_run
from analogos.synthetic import synthetic_earth, synthetic_target
from analogos.validation_ext import boot_mean, summarize_groups


def test_boot_mean_ci_contains_mean_and_handles_nan():
    m, lo, hi = boot_mean(np.array([0.4, 0.6, 0.8, np.nan]))
    assert lo <= m <= hi and np.isclose(m, 0.6)
    m1, lo1, hi1 = boot_mean(np.array([0.7]))
    assert m1 == 0.7 and np.isnan(lo1) and np.isnan(hi1)


def test_summarize_groups_splits_original_and_new():
    raw = pd.DataFrame({"body": "mars", "config": "todas", "target": "t", "analog": ["a", "b", "c", "d"], "u": [0.9, 0.7, 0.4, 0.6]})
    known = pd.DataFrame({"name": list("abcd"), "group": ["original", "original", "nuevo", "nuevo"]})
    s = summarize_groups(raw, known).query("config == 'todas' and body == 'mars'").set_index("grupo")
    assert s.loc["originales", "n_analogos"] == 2 and np.isclose(s.loc["originales", "u_medio"], 0.8)
    assert s.loc["nuevos", "n_analogos"] == 2 and np.isclose(s.loc["todos", "u_medio"], 0.65)


def test_stability_frequencies_are_valid(tmp_path):
    earth = synthetic_earth().assign(viable=True, vegetated=False)
    earth.to_parquet(tmp_path / "earth.parquet", index=False)
    sites = pd.read_csv("docs/sitios_objetivo.csv")
    for b in ("moon", "mars"):
        synthetic_target(b, sites).to_parquet(tmp_path / f"{b}.parquet", index=False)
    r = stability_run("mars", n_rep=4, features_dir=tmp_path)
    assert r["freq_top5"].between(0, 1).all() and r["mean_rank_pct"].between(0, 1).all()
    assert (r["freq_top5"] > 0).any()          # algunas celdas siempre llegan al 5 % superior


def test_inertia_percentile_window_and_proxy():
    from analogos import config
    from analogos.inertia import earth_proxy, extra_dimension, percentile, window_median

    ref = np.sort(np.array([10.0, 20, 30, 40]))
    p = percentile(np.array([5.0, 25.0, 100.0, np.nan]), ref)
    assert p[0] == 0.0 and p[1] == 0.5 and p[2] == 1.0 and np.isnan(p[3])
    px = earth_proxy(np.array([2.0, 0.0, -1.0, np.nan]))
    assert px[0] == 0.5 and np.isnan(px[1:]).all()
    ti = np.full((3600, 7200), np.nan, dtype="float32")
    ti[1800:1802, 3600:3602] = 300.0
    assert window_median(ti, 0.0, 0.0) == 300.0               # longitud 0 y 360 son el mismo punto
    assert window_median(ti, 0.0, 360.0) == 300.0
    assert np.isnan(window_median(ti, 45.0, 90.0))


def test_extra_dimension_restores_global_state():
    from analogos import ablation, config
    from analogos.inertia import FEATURE, extra_dimension

    dims, feats, weights, abl = list(config.DIMENSIONS), list(config.FEATURES), dict(config.DEFAULT_WEIGHTS), list(ablation.DIMS)
    with extra_dimension():
        assert "inertia" in config.DIMENSIONS and FEATURE in config.FEATURES and "inertia" in ablation.DIMS
    assert list(config.DIMENSIONS) == dims and list(config.FEATURES) == feats
    assert config.DEFAULT_WEIGHTS == weights and ablation.DIMS == abl


def test_emissivity_contrast_and_gates():
    from analogos.emissivity import contrast_index, gates, litho_sites

    assert np.isclose(contrast_index(0.90, 0.96, 0.98), -0.07)
    l = litho_sites()
    assert l["basalt"].sum() == 10 and (l["basalt"] == 0).sum() == 10 and l["name"].is_unique
    l["c"] = np.where(l["basalt"] == 1, 0.0, -0.1)            # separación perfecta
    small = pd.DataFrame({"name": list("abc"), "c": [-0.01, -0.2, -0.05]})
    g = gates(l, np.array([0.0, 0.0, np.nan]), small)
    assert g["auc"] == 1.0 and g["puerta2"] and g["pequenos_sobre_mediana"] == 2 and g["puerta3"]
    assert g["puerta1"] is False


def test_multiscale_hurst_recovers_power_law():
    from analogos.multiscale import FLOOR_M, add_multiscale, hurst

    L = np.array([1.0, 2.0, 5.0])
    rough = np.vstack([3.0 * L ** 0.7, 0.5 * L ** 0.3])
    assert np.allclose(hurst(rough), [0.7, 0.3])
    assert np.isfinite(hurst(np.zeros((1, 3)))).all()                  # rugosidad cero: acotada por debajo, sin infinitos
    df = pd.DataFrame({"topo__rough_1km_m": [3.0], "topo__rough_2km_m": [4.9], "topo__rough_5km_m": [9.0], "topo__slope_mean_deg": [1.0]})
    out = add_multiscale(df)
    assert {"ms_hurst", "ms_lnr1", "ms_lnslope"} <= set(out.columns) and np.isclose(out["ms_lnslope"].iloc[0], np.log(1.1)) and FLOOR_M > 0


def test_variability_offsets_and_pole_reflection():
    from analogos.variability import calibrated_model, offset_point, window_offsets

    lat, lon = offset_point(0.0, 10.0, 0.0, 25.0, 3396.0)               # 25 km al este en el ecuador de Marte
    assert abs(lat) < 1e-9 and np.isclose(lon - 10.0, 25.0 / (3396.0 * np.pi / 180.0))
    lat, lon = offset_point(89.9, 0.0, 25.0, 0.0, 1737.4)               # al norte pasa el polo: se refleja
    assert 89.0 < lat < 90.0 and np.isclose(abs(lon), 180.0)
    assert len(window_offsets(10.0)) == 9 and len(window_offsets(-89.9)) == 3
    from analogos.similarity import TopoModel
    m = TopoModel(["a", "b"], pd.Series([0.0, 0.0], index=["a", "b"]), pd.Series([1.0, 1.0], index=["a", "b"]), np.eye(2), np.ones(2), np.array([0.5, 1.0]))
    c = calibrated_model(m, [3.0, 0.0])
    assert np.allclose(c.scale, [np.sqrt(10.0), 1.0])
    d = pd.DataFrame({"a": [2.0], "b": [2.0]})
    assert np.allclose(c.transform(d).to_numpy(), [[2.0 / np.sqrt(10.0), 2.0]])   # la diferencia se divide por sqrt(1 + s^2)


def test_variability_target_spread_and_fallback():
    from analogos.similarity import TopoModel
    from analogos.variability import target_spread

    m = TopoModel(["a", "b"], pd.Series([0.0, 0.0], index=["a", "b"]), pd.Series([1.0, 1.0], index=["a", "b"]), np.eye(2), np.ones(2), np.array([0.5, 1.0]))
    g1 = pd.DataFrame({"site": "A", "lat": 10.0, "valid_frac": 1.0, "a": np.arange(9.0), "b": np.zeros(9)})
    g2 = pd.DataFrame({"site": "B", "lat": 10.0, "valid_frac": [1.0] * 3 + [0.0] * 6, "a": np.arange(9.0), "b": np.arange(9.0)})
    w = pd.concat([g1, g2], ignore_index=True)
    s = target_spread(w, m)
    assert s.loc["A", "calibrado"] and np.isclose(s.loc["A", "s1"], np.arange(9.0).std(ddof=1)) and s.loc["A", "s2"] == 0.0
    assert not s.loc["B", "calibrado"] and s.loc["B", "s1"] == 0.0     # solo 3 ventanas válidas de 9: sin calibrar


def test_grupos_rules_and_exact_test():
    from analogos.grupos import COLD_LAT, COLD_TMAX_K, cold_analogs, exact_sign_flip_p, split_targets

    assert exact_sign_flip_p(np.array([0.1, 0.2, 0.3, 0.4, 0.5])) == 1 / 32          # los 5 positivos: p mínima
    assert exact_sign_flip_p(np.array([-0.1, -0.2, -0.3])) == 1.0
    sites = pd.DataFrame({"name": ["frio", "justo", "calido", "solo_luna"], "thermal__t_max_k": [280.0, COLD_TMAX_K, 320.0, 270.0]})
    known = pd.DataFrame({"name": ["frio", "justo", "calido", "solo_luna"], "analog_of": ["mars", "mars", "moon+mars", "moon"]})
    assert cold_analogs(sites, known) == ["frio"]                                   # 295 K no es frío (< estricto); la Luna se ignora
    prof = pd.DataFrame(index=["polar", "borde", "tropical"])
    lat = pd.Series({"polar": 68.0, "borde": COLD_LAT, "tropical": 5.0})
    cold, warm = split_targets(prof, lat)
    assert cold == ["polar", "borde"] and warm == ["tropical"]


def test_modelos_percentiles_and_max_over():
    from analogos.modelos import max_over, percentile_below, rank_pct

    v = np.array([1.0, 2.0, 2.0, 4.0, np.nan])
    assert percentile_below(v, 2.0) == (1 + 0.5 * 2) / 4 and np.isnan(percentile_below(v, np.nan))
    r = rank_pct(v)
    assert np.isclose(r[0], 0.125) and np.isclose(r[1], r[2]) and np.isnan(r[4]) and r[3] > r[1]
    S = np.array([[0.2, 0.9], [np.nan, np.nan], [0.5, 0.1]])
    out = max_over(S, [0, 1])
    assert out[0] == 0.9 and np.isnan(out[1]) and out[2] == 0.5
    assert np.isnan(max_over(S, [])).all()
