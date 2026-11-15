import pandas as pd

from analogos.atlas import CONFIDENCE, MIN_USEFUL_SCORE, _has_data, aspect_case
from analogos.config import DIMENSIONS


def test_every_body_aspect_has_a_confidence_label():
    for body in ("moon", "mars"):
        for aspect in DIMENSIONS:
            c = CONFIDENCE[(body, aspect)]
            assert c.level in ("alta", "media", "baja", "muy baja", "sin datos") and c.why and c.doc


def test_no_aspect_is_labelled_high_confidence():
    """Con 4 a 8 análogos por cuerpo ningún aspecto se puede validar de forma concluyente."""
    assert all(c.level != "alta" for c in CONFIDENCE.values())


def test_aspect_case_weights_only_that_dimension():
    uc = aspect_case("mars", "geo", ["Jezero"])
    assert uc.weights["geo"] == 1.0 and sum(uc.weights.values()) == 1.0 and uc.body == "mars"


def test_has_data_uses_the_aspect_columns():
    p = pd.Series({"thermal__t_max_k": float("nan"), "thermal__t_range_k": float("nan"), "geo__basalt_frac": 0.5})
    assert not _has_data(p, "thermal") and _has_data(p, "geo")


def test_min_useful_score_is_positive():
    assert 0 < MIN_USEFUL_SCORE < 0.5
