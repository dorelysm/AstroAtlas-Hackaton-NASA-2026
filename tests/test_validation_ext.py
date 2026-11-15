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
