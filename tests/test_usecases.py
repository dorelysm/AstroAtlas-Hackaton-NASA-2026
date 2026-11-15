import numpy as np
import pandas as pd
import pytest

from analogos.usecases import USE_CASES, UseCase, pick_regions, score_use_case


def test_pick_regions_enforces_separation():
    s = pd.DataFrame({"cell_id": list("abcd"), "lat": [0.0, 0.5, 40.0, -40.0], "lon": [0.0, 0.5, 0.0, 0.0],
                      "score": [0.9, 0.8, 0.7, 0.6]})
    out = pick_regions(s, n=3, min_sep_km=500)
    assert out["cell_id"].tolist() == ["a", "c", "d"]          # b está a < 500 km de a


def test_use_cases_are_well_formed():
    keys = [u.key for u in USE_CASES]
    assert len(keys) == len(set(keys)) and all(u.targets and sum(u.weights.values()) > 0 for u in USE_CASES)
    assert all(u.body in ("moon", "mars") and u.note and u.caveats for u in USE_CASES)


def test_score_use_case_requires_known_target():
    uc = UseCase("x", "x", "mars", ["no existe"], {"topo": 1.0}, "n")
    with pytest.raises(ValueError):
        score_use_case(uc, pd.DataFrame({"cell_id": ["a"], "lat": [0.0], "lon": [0.0]}), pd.DataFrame(index=["otro"]), None)
