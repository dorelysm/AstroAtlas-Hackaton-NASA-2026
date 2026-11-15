"""Optional treatment of cells without data in a dimension (similarity.global_score, missing_data)."""
import numpy as np
import pandas as pd
import pytest

from astroatlas.config import DIMENSIONS, FEATURES
from astroatlas.missing_data import cells_with_gaps, gap_share, summarize
from astroatlas.similarity import fit_topo_model, global_score, rank_cells, score_cells
from astroatlas.synthetic import synthetic_earth

DIMS = pd.DataFrame({
    "topo": [0.8, 0.8, 0.8, np.nan],
    "thermal": [np.nan, np.nan, np.nan, np.nan],   # the target has no data here (like Mars thermal)
    "ice": [0.6, np.nan, 0.6, np.nan],
    "geo": [0.4, 0.4, np.nan, np.nan],
})


def test_default_is_the_published_model():
    """Same numbers as before the option existed: mean over the dimensions each cell has data for."""
    s = global_score(DIMS)
    assert s.tolist()[:3] == pytest.approx([0.6, 0.6, 0.7])
    assert np.isnan(s.iloc[3])
    pd.testing.assert_series_equal(global_score(DIMS, missing="renormalize"), s)


def test_zero_scores_a_gap_as_no_similarity():
    s = global_score(DIMS, missing="zero")
    # topo, ice and geo count for every cell (thermal has no score for anyone, so it is dropped)
    assert s.iloc[0] == pytest.approx((0.8 + 0.6 + 0.4) / 3)
    assert s.iloc[1] == pytest.approx((0.8 + 0 + 0.4) / 3)   # no ice data -> 0, not ignored
    assert s.iloc[2] == pytest.approx((0.8 + 0.6 + 0) / 3)
    assert np.isnan(s.iloc[3])                               # a cell with no score at all stays NaN


def test_zero_respects_weights_and_expected_dimensions():
    s = global_score(DIMS, {"ice": 0.0}, missing="zero")
    assert s.iloc[0] == pytest.approx((0.8 + 0.4) / 2)
    s = global_score(DIMS, missing="zero", expected=["topo", "ice"])
    assert s.iloc[1] == pytest.approx(0.8 / 2)


def test_zero_penalises_a_cell_with_a_gap_against_an_equal_cell_with_data():
    d = pd.DataFrame({"topo": [0.5, 0.5], "thermal": [0.2, np.nan], "ice": [0.5, 0.5], "geo": [0.5, 0.5]})
    assert global_score(d).iloc[1] > global_score(d).iloc[0]                        # published model: the gap wins
    assert global_score(d, missing="zero").iloc[1] < global_score(d, missing="zero").iloc[0]


def test_unknown_mode_is_rejected():
    with pytest.raises(ValueError):
        global_score(DIMS, missing="median")


@pytest.fixture(scope="module")
def earth():
    e = synthetic_earth(step_deg=10.0)
    e.loc[e.index[:30], DIMENSIONS["geo"]] = np.nan            # a block of cells without geology
    return e


def test_rank_and_score_cells_default_unchanged(earth):
    profile = earth.iloc[100][FEATURES]
    topo = fit_topo_model(earth)
    a = rank_cells(earth, profile, None, topo)
    b = rank_cells(earth, profile, None, topo, missing="renormalize")
    pd.testing.assert_frame_equal(a, b)
    pd.testing.assert_series_equal(score_cells(earth, profile, None, topo)["score"],
                                   score_cells(earth, profile, None, topo, missing="renormalize")["score"])


def test_zero_mode_ranks_cells_with_gaps_lower(earth):
    profile = earth.iloc[100][FEATURES]
    topo = fit_topo_model(earth)
    gap = cells_with_gaps(earth).set_axis(earth["cell_id"])
    base = rank_cells(earth, profile, None, topo)
    zero = rank_cells(earth, profile, None, topo, missing="zero")
    mean_rank = lambda r: r.set_index("cell_id")["rank"].reindex(earth["cell_id"])[gap.to_numpy()].mean()
    assert mean_rank(zero) > mean_rank(base)                    # the gap cells move down the ranking


def test_zero_mode_drops_a_dimension_the_target_lacks(earth):
    profile = earth.iloc[100][FEATURES].copy()
    profile[DIMENSIONS["thermal"]] = np.nan                     # like a Mars target
    topo = fit_topo_model(earth)
    sc = score_cells(earth, profile, None, topo, missing="zero")
    assert sc["thermal"].isna().all() and sc["score"].notna().any()
    ref = sc[["topo", "ice", "geo"]].fillna(0).mean(axis=1)     # thermal does not enter the denominator
    ok = sc[["topo", "ice", "geo"]].notna().any(axis=1)
    assert sc["score"][ok].to_numpy() == pytest.approx(ref[ok].to_numpy())


def test_gap_share_and_summarize(earth):
    topo = fit_topo_model(earth)
    profiles = earth.iloc[[100, 120]].set_index("cell_id")[FEATURES]
    g = gap_share(earth, profiles, topo, n=20)
    assert list(g["mode"].unique()) == ["renormalize"] and (g["gaps_in_top20"] <= 20).all()
    raw = pd.DataFrame({"body": "mars", "mode": ["renormalize"] * 3 + ["zero"] * 3, "target": "T",
                        "analog": ["a", "b", "c"] * 2, "u": [0.4, 0.5, 0.6, 0.5, 0.6, 0.7]})
    s = summarize(raw).set_index("mode")
    assert s.loc["zero", "change_vs_baseline"] == pytest.approx(0.1)
    assert s.loc["renormalize", "mean_u"] == pytest.approx(0.5)
