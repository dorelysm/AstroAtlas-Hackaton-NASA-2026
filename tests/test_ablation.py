import numpy as np
import pandas as pd
import pytest

from astroatlas import ablation as ab
from astroatlas.config import DIMENSIONS
from astroatlas.synthetic import synthetic_earth, synthetic_target
from astroatlas.validate import load_known


def test_weights_helpers_and_config_names():
    only, without = ab.weights_only("ice"), ab.weights_without("ice")
    assert only["ice"] == 1.0 and sum(only.values()) == 1.0
    assert without["ice"] == 0.0 and sum(without.values()) == len(DIMENSIONS) - 1
    cfgs = ab.configs()
    assert len(cfgs) == 1 + 2 * len(DIMENSIONS) and "all" in cfgs and "only geo" in cfgs and "without topo" in cfgs


def test_summarize_means_deltas_and_site_bootstrap():
    rows = []
    for t in ("T1", "T2"):  # two targets that share the SAME 3 analogs
        for a, (u_all, u_topo) in {"A": (0.9, 0.5), "B": (0.7, 0.5), "C": (0.5, 0.5)}.items():
            rows += [{"body": "moon", "target": t, "config": "all", "analog": a, "u": u_all, "auc_cells": 0.5},
                     {"body": "moon", "target": t, "config": "only topo", "analog": a, "u": u_topo, "auc_cells": 0.5}]
    s = ab.summarize(pd.DataFrame(rows), n_boot=300).set_index("config")
    assert s.loc["all", "u_mean"] == pytest.approx(0.7) and s.loc["only topo", "u_mean"] == pytest.approx(0.5)
    assert s.loc["only topo", "delta_vs_all"] == pytest.approx(-0.2)
    assert s.loc["all", "n_analogs"] == 3 and s.loc["all", "n_targets"] == 2
    assert s.loc["all", "ci_lo"] <= 0.7 <= s.loc["all", "ci_hi"]
    assert s.loc["only topo", "ci_lo"] == pytest.approx(0.5) == s.loc["only topo", "ci_hi"]  # constant: no uncertainty


def test_summarize_handles_dimension_without_data():
    # a configuration without rows for a body (e.g. Mars thermal) must not break the summary
    rows = [{"body": "mars", "target": "J", "config": "all", "analog": a, "u": 0.6, "auc_cells": 0.5} for a in "AB"]
    rows += [{"body": "mars", "target": "J", "config": "without geo", "analog": a, "u": 0.4, "auc_cells": 0.5} for a in "AB"]
    s = ab.summarize(pd.DataFrame(rows), n_boot=50).set_index("config")
    assert s.loc["without geo", "delta_vs_all"] == pytest.approx(-0.2)


def test_run_on_synthetic_features(tmp_path):
    known = load_known()
    earth = synthetic_earth(step_deg=10.0)
    earth.to_parquet(tmp_path / "earth.parquet", index=False)
    sites = pd.read_csv("docs/catalog/target_sites.csv")
    for body in ("moon", "mars"):
        synthetic_target(body, sites, cells_per_site=3).to_parquet(tmp_path / f"{body}.parquet", index=False)
    # "computed" analogs: rows of the synthetic Earth with the name of each known analog
    pick = earth.sample(len(known), random_state=1).reset_index(drop=True)
    pick["name"] = known["name"].to_numpy()
    pick["lat"], pick["lon"] = known["lat"].to_numpy(), known["lon"].to_numpy()
    pick.to_parquet(tmp_path / "earth_sites.parquet", index=False)

    df = ab.run(tmp_path)
    assert {"body", "target", "config", "analog", "u"} <= set(df.columns)
    assert set(df["body"]) == {"moon", "mars"} and df["u"].between(0, 1).all()
    assert set(df["config"]) == set(ab.configs())
    summ = ab.summarize(df, n_boot=50)
    assert (summ.loc[summ.config == "all", "u_mean"].between(0, 1)).all()
