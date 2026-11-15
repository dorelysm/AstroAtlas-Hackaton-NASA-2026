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
