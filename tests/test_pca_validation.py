import json

import numpy as np
import pandas as pd
import pytest

from astroatlas.config import DIMENSIONS, FEATURES
from astroatlas.pipeline import run
from astroatlas.similarity import fit_topo_model, rank_cells, score_cells
from astroatlas.synthetic import synthetic_earth, synthetic_target
from astroatlas.validate import evaluate, evaluate_sites, known_for_body, load_known

TOPO = DIMENSIONS["topo"]
SITES = pd.DataFrame({"site": ["A", "B"], "body": ["moon", "moon"], "lat": [-80.0, 8.0], "lon": [10.0, 33.0]})


@pytest.fixture(scope="module")
def earth():
    return synthetic_earth(step_deg=5.0)


def test_topo_model_whitens_and_compresses_correlated_features():
    rng = np.random.default_rng(0)
    base = rng.normal(size=(400, 1))
    df = pd.DataFrame({f: base[:, 0] * (i + 1) + rng.normal(0, 0.01, 400) for i, f in enumerate(TOPO)})
    m = fit_topo_model(df)
    assert m.n_components == 1  # 16 almost identical variables = a single direction
    pcs = m.transform(df)
    assert pcs["pc1"].std() == pytest.approx(1.0, rel=0.05)  # blanqueada


def test_topo_model_respects_variance_and_max_components(earth):
    m = fit_topo_model(earth, variance=0.999, max_components=4)
    assert 1 <= m.n_components <= 4
    assert (np.diff(m.cum_variance) > 0).all()


def test_topo_transform_gives_nan_instead_of_imputing(earth):
    m = fit_topo_model(earth)
    e = earth.head(5).copy()
    e.loc[e.index[0], TOPO[0]] = np.nan
    pcs = m.transform(e)
    assert pcs.iloc[0].isna().all() and pcs.iloc[1:].notna().all().all()


def test_identical_cell_ranks_first_with_pca(earth):
    m = fit_topo_model(earth)
    ranked = rank_cells(earth, earth.iloc[100][FEATURES], topo_model=m)
    assert ranked.loc[0, "cell_id"] == earth.iloc[100]["cell_id"]
    assert ranked.loc[0, "score"] == pytest.approx(1.0)
    assert ranked["topo"].between(0, 1).all()


def test_pca_stops_redundant_topo_features_from_counting_twice():
    """15 copies of A and 1 independent variable B: without PCA a difference of 1 sd in A weighs ~4 times
    more than the same difference in B; with PCA they weigh the same."""
    from astroatlas.similarity import dimension_scores

    rng = np.random.default_rng(0)
    a, b = rng.normal(size=500), rng.normal(size=500)
    df = pd.DataFrame(0.0, index=range(500), columns=FEATURES)
    for f in TOPO[:15]:
        df[f] = a + rng.normal(0, 0.01, 500)
    df[TOPO[15]] = b
    mu, sd = df[TOPO].mean(), df[TOPO].std()

    def row(da, db):  # a row at `da` and `db` standard deviations from the mean
        r = pd.Series(0.0, index=FEATURES)
        r[TOPO[:15]] = mu[TOPO[:15]] + da * sd[TOPO[:15]]
        r[TOPO[15]] = mu[TOPO[15]] + db * sd[TOPO[15]]
        return r

    cells = pd.DataFrame([row(1, 0), row(0, 1)])
    profile = row(0, 0)
    m = fit_topo_model(df, variance=0.999)
    with_pca = dimension_scores(cells, profile, m, ref=df)["topo"]
    without = dimension_scores(cells, profile, None, ref=df)["topo"]
    assert m.n_components == 2
    assert abs(with_pca.iloc[0] - with_pca.iloc[1]) < 0.05
    assert without.iloc[1] - without.iloc[0] > 0.3  # B barely counts without PCA


def test_score_cells_uses_reference_stats(earth):
    """The analog sites are scored with the Earth's standardisation, not their own."""
    profile = earth.iloc[10][FEATURES]
    sub = earth.iloc[:10]
    a = score_cells(sub, profile, ref=earth)["score"]
    b = score_cells(sub, profile)["score"]  # standardised with only 10 rows
    assert not np.allclose(a, b)


def test_known_for_body_filters_by_analog_type():
    known = load_known()
    moon, mars = known_for_body(known, "moon"), known_for_body(known, "mars")
    assert "Mauna Kea" in set(moon["name"]) and "Mauna Kea" not in set(mars["name"])
    assert "Atacama" in set(mars["name"]) and "Atacama" not in set(moon["name"])
    assert "Craters of the Moon" in set(moon["name"]) & set(mars["name"])  # 'moon+mars'
    assert len(known_for_body(known, None)) == len(known)
    assert len(known_for_body(known.drop(columns="analog_of"), "moon")) == len(known)


def test_evaluate_with_bootstrap_ci(earth):
    ranked = rank_cells(earth, earth.iloc[100][FEATURES])
    known = load_known()
    a = evaluate(ranked, known, radius_km=600, body="mars", n_boot=200, seed=1)
    b = evaluate(ranked, known, radius_km=600, body="mars", n_boot=200, seed=1)
    assert a["auc_ci"] == b["auc_ci"]  # reproducible
    lo, hi = a["auc_ci"]
    assert 0 <= lo <= hi <= 1 and a["n_known"] == len(known_for_body(known, "mars"))
    assert "auc_ci" not in evaluate(ranked, known, radius_km=600)  # without bootstrap there is no CI


def test_evaluate_handles_no_analogs_for_body(earth):
    ranked = rank_cells(earth, earth.iloc[1][FEATURES])
    out = evaluate(ranked, load_known().head(0), body="mars")
    assert np.isnan(out["auc"]) and out["n_known"] == 0


def test_evaluate_sites_extremes():
    cells = pd.Series(np.linspace(0, 1, 101))
    hi = evaluate_sites(cells, pd.Series({"a": 1.5, "b": 2.0}))
    lo = evaluate_sites(cells, pd.Series({"a": -1.0}))
    assert hi["auc"] == 1.0 and hi["recall_at_top_pct"] == 1.0 and hi["percentile_per_known"]["a"] == 0.0
    assert lo["auc"] == 0.0 and lo["recall_at_top_pct"] == 0.0
    mid = evaluate_sites(cells, pd.Series({"x": 0.5}))
    assert mid["auc"] == pytest.approx(0.5, abs=0.01)
    assert np.isnan(evaluate_sites(cells, pd.Series(dtype=float))["auc"])  # no sites


@pytest.mark.parametrize("with_sites", [True, False])
def test_pipeline_end_to_end_tmp(tmp_path, earth, with_sites):
    fdir, rdir = tmp_path / "features", tmp_path / "results"
    fdir.mkdir()
    earth.to_parquet(fdir / "earth.parquet", index=False)
    synthetic_target("moon", SITES).to_parquet(fdir / "moon.parquet", index=False)
    mars_sites = SITES.assign(site=["C", "D"], body="mars")
    synthetic_target("mars", mars_sites).to_parquet(fdir / "mars.parquet", index=False)
    if with_sites:
        known = load_known()
        es = earth.head(len(known)).copy()
        es["name"] = known["name"].to_numpy()
        es.to_parquet(fdir / "earth_sites.parquet", index=False)

    m = run(n_boot=20, features_dir=fdir, results_dir=rdir)
    assert set(m) == {"moon/A", "moon/B", "mars/C", "mars/D"}
    assert all(("sites" in v) == with_sites for v in m.values())
    summ = json.loads((rdir / "validation_summary.json").read_text())
    assert summ["config"]["compress_topo"] and summ["all"]["n_targets"] == 4
    assert summ["config"]["topo_components"] >= 1
    assert (rdir / "scores.parquet").exists() and (rdir / "candidates.csv").exists()

    # the previous version is still available
    run(n_boot=0, compress_topo=False, by_body=False, features_dir=fdir, results_dir=tmp_path / "base")
    base = json.loads((tmp_path / "base" / "validation_summary.json").read_text())
    assert base["config"]["compress_topo"] is False and base["config"]["topo_components"] is None


def test_pca_scores_flat_terrain_rows_instead_of_dropping_them():
    """Regression: rows with slope < 0.1° used to carry NaN in the aspect and the PCA did not score them."""
    import numpy as np

    from astroatlas.config import DIMENSIONS
    from astroatlas.similarity import fit_topo_model
    from astroatlas.synthetic import synthetic_earth

    earth = synthetic_earth(step_deg=5.0)
    model = fit_topo_model(earth)
    flat = earth.iloc[:3].copy()
    for c in DIMENSIONS["topo"]:
        flat[c] = 0.0  # perfectly flat terrain, with neutral aspect 0
    assert np.isfinite(model.transform(flat).to_numpy()).all()
