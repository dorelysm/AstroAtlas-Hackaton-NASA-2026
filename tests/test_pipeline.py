import numpy as np
import pandas as pd
import pytest

from analogos.config import DIMENSIONS, FEATURES
from analogos.features import validate_features
from analogos.report import ficha
from analogos.similarity import rank_cells, site_profiles
from analogos.synthetic import synthetic_earth, synthetic_target
from analogos.validate import evaluate, haversine_km, load_known, novel_candidates

SITES = pd.DataFrame(
    {"site": ["A", "B"], "body": ["moon", "moon"], "lat": [-89.0, 8.0], "lon": [0.0, 33.0]}
)


@pytest.fixture(scope="module")
def earth():
    return synthetic_earth(step_deg=5.0)


def test_contract_ok_and_errors(earth):
    validate_features(earth, "earth")
    with pytest.raises(ValueError):
        validate_features(earth.drop(columns=["lat"]), "earth")
    with pytest.raises(ValueError):
        validate_features(earth.assign(extra__x=1.0), "earth")
    with pytest.raises(ValueError):  # falta 'site'
        validate_features(earth.assign(body="moon"), "moon")


def test_identical_cell_ranks_first(earth):
    profile = earth.iloc[100][FEATURES]
    ranked = rank_cells(earth, profile)
    assert ranked.loc[0, "cell_id"] == earth.iloc[100]["cell_id"]
    assert ranked.loc[0, "score"] == pytest.approx(1.0)
    assert (ranked[list(DIMENSIONS)].dropna().le(1).all()).all().all()


def test_nan_features_do_not_break_scores(earth):
    broken = earth.copy()
    broken.loc[:20, "ice__water_frac"] = np.nan
    ranked = rank_cells(broken, earth.iloc[5][FEATURES])
    assert ranked["score"].notna().all()


def test_site_profiles_and_ficha(earth):
    moon = synthetic_target("moon", SITES, cells_per_site=5)
    validate_features(moon, "moon")
    profiles = site_profiles(moon)
    assert list(profiles.index) == ["A", "B"]
    ranked = rank_cells(earth, profiles.loc["A"])
    f = ficha(ranked.iloc[0], "A", "moon")
    assert f["rank"] == 1 and f["limits"]


def test_haversine_known_distance():
    assert haversine_km(0, 0, 0, 0) == pytest.approx(0)
    assert haversine_km(0, 0, 0, 90) == pytest.approx(10007.5, rel=1e-3)


def test_validation_and_novel_candidates(earth):
    ranked = rank_cells(earth, earth.iloc[100][FEATURES])
    known = load_known()
    m = evaluate(ranked, known, radius_km=600)
    assert 0 <= m["auc"] <= 1 and m["n_known_covered"] > 0
    nov = novel_candidates(ranked, known, min_km=1000, n=5)
    assert len(nov) == 5
