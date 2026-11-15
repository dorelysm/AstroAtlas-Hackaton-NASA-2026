import numpy as np
import pandas as pd
import pytest

from analogos import ablation as ab
from analogos.config import DIMENSIONS
from analogos.synthetic import synthetic_earth, synthetic_target
from analogos.validate import load_known


def test_weights_helpers_and_config_names():
    only, without = ab.weights_only("ice"), ab.weights_without("ice")
    assert only["ice"] == 1.0 and sum(only.values()) == 1.0
    assert without["ice"] == 0.0 and sum(without.values()) == len(DIMENSIONS) - 1
    cfgs = ab.configs()
    assert len(cfgs) == 1 + 2 * len(DIMENSIONS) and "todas" in cfgs and "solo geo" in cfgs and "sin topo" in cfgs


def test_summarize_means_deltas_and_site_bootstrap():
    rows = []
    for t in ("T1", "T2"):  # dos objetivos que comparten los MISMOS 3 análogos
        for a, (u_all, u_topo) in {"A": (0.9, 0.5), "B": (0.7, 0.5), "C": (0.5, 0.5)}.items():
            rows += [{"body": "moon", "target": t, "config": "todas", "analog": a, "u": u_all, "auc_cells": 0.5},
                     {"body": "moon", "target": t, "config": "solo topo", "analog": a, "u": u_topo, "auc_cells": 0.5}]
    s = ab.summarize(pd.DataFrame(rows), n_boot=300).set_index("config")
    assert s.loc["todas", "u_mean"] == pytest.approx(0.7) and s.loc["solo topo", "u_mean"] == pytest.approx(0.5)
    assert s.loc["solo topo", "delta_vs_todas"] == pytest.approx(-0.2)
    assert s.loc["todas", "n_analogs"] == 3 and s.loc["todas", "n_targets"] == 2
    assert s.loc["todas", "ci_lo"] <= 0.7 <= s.loc["todas", "ci_hi"]
    assert s.loc["solo topo", "ci_lo"] == pytest.approx(0.5) == s.loc["solo topo", "ci_hi"]  # constante: sin incertidumbre


def test_summarize_handles_dimension_without_data():
    # una configuración sin filas para un cuerpo (p. ej. térmica de Marte) no debe romper el resumen
    rows = [{"body": "mars", "target": "J", "config": "todas", "analog": a, "u": 0.6, "auc_cells": 0.5} for a in "AB"]
    rows += [{"body": "mars", "target": "J", "config": "sin geo", "analog": a, "u": 0.4, "auc_cells": 0.5} for a in "AB"]
    s = ab.summarize(pd.DataFrame(rows), n_boot=50).set_index("config")
    assert s.loc["sin geo", "delta_vs_todas"] == pytest.approx(-0.2)


def test_run_on_synthetic_features(tmp_path):
    known = load_known()
    earth = synthetic_earth(step_deg=10.0)
    earth.to_parquet(tmp_path / "earth.parquet", index=False)
    sites = pd.read_csv("docs/sitios_objetivo.csv")
    for body in ("moon", "mars"):
        synthetic_target(body, sites, cells_per_site=3).to_parquet(tmp_path / f"{body}.parquet", index=False)
    # análogos "calculados": filas de la Tierra sintética con el nombre de cada análogo conocido
    pick = earth.sample(len(known), random_state=1).reset_index(drop=True)
    pick["name"] = known["name"].to_numpy()
    pick["lat"], pick["lon"] = known["lat"].to_numpy(), known["lon"].to_numpy()
    pick.to_parquet(tmp_path / "earth_sites.parquet", index=False)

    df = ab.run(tmp_path)
    assert {"body", "target", "config", "analog", "u"} <= set(df.columns)
    assert set(df["body"]) == {"moon", "mars"} and df["u"].between(0, 1).all()
    assert set(df["config"]) == set(ab.configs())
    summ = ab.summarize(df, n_boot=50)
    assert (summ.loc[summ.config == "todas", "u_mean"].between(0, 1)).all()
