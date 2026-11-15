import numpy as np
import pandas as pd
import pytest

from analogos import aspect as asp


def _tags(rows):
    t = pd.DataFrame(rows, columns=["name", "aspect", "nivel"])
    t["level"] = t["nivel"].map(asp.LEVELS)
    return t


TAGS = _tags([("A", "geo", "fuente"), ("B", "geo", "nota"), ("C", "ice", "fuente"), ("D", "ninguno", "fuente"),
              ("E", "geo", "general")])


def test_split_groups_respects_evidence_level_and_ignores_untagged():
    analogs = ["A", "B", "C", "D", "E", "F"]  # F no tiene etiquetas
    assert asp.split_groups(TAGS, analogs, "geo", 1) == (["A"], ["C", "D"])
    assert asp.split_groups(TAGS, analogs, "geo", 2) == (["A", "B"], ["C", "D"])
    pos, neg = asp.split_groups(TAGS, analogs, "geo", 3)
    assert pos == ["A", "B", "E"] and "F" not in neg and neg == ["C", "D"]  # F nunca es negativo


def test_exact_permutation_p_known_values():
    # 1 positivo de 4 con el valor más alto: la única asignación igual de extrema entre 4 posibles -> p = 1/4
    assert asp.permutation_p(np.array([0.9]), np.array([0.1, 0.2, 0.3])) == pytest.approx(0.25)
    # separación perfecta de 3 contra 3: 1 de las 20 asignaciones -> p = 0.05
    assert asp.permutation_p(np.array([0.7, 0.8, 0.9]), np.array([0.1, 0.2, 0.3])) == pytest.approx(0.05)
    # sin diferencia: p = 1 (todas las asignaciones son >= al gap observado de 0)
    assert asp.permutation_p(np.array([0.5, 0.5]), np.array([0.5, 0.5])) == pytest.approx(1.0)
    # el p nunca es menor que 1/C(n,k): con 1 contra 1 el mínimo es 0.5
    assert asp.permutation_p(np.array([1.0]), np.array([0.0])) == pytest.approx(0.5)


def test_evaluate_aspect_detects_and_rejects():
    u = pd.Series({"A": 0.9, "B": 0.8, "C": 0.2, "D": 0.1})
    t = _tags([("A", "geo", "fuente"), ("B", "geo", "fuente"), ("C", "ice", "fuente"), ("D", "topo", "fuente")])
    r = asp.evaluate_aspect(u, t, "geo", 1, n_boot=200)
    assert r["n_on"] == 2 and r["n_off"] == 2 and r["gap"] == pytest.approx(0.7)
    assert r["auc_rank"] == 1.0 and r["p_perm"] == pytest.approx(1 / 6) and r["gap_lo"] > 0
    # dimensión equivocada: los "positivos" puntúan peor que los negativos
    wrong = asp.evaluate_aspect(pd.Series({"A": 0.1, "B": 0.2, "C": 0.8, "D": 0.9}), t, "geo", 1, n_boot=200)
    assert wrong["gap"] < 0 and wrong["p_perm"] > 0.8


def test_aspect_without_one_group_is_not_evaluated():
    u = pd.Series({"A": 0.9, "C": 0.2})
    t = _tags([("A", "geo", "fuente"), ("C", "ice", "fuente")])
    r = asp.evaluate_aspect(u, t, "thermal", 1)  # nadie lleva la etiqueta thermal
    assert r["estado"].startswith("no evaluable") and np.isnan(r["gap"])


def test_analog_means_uses_only_the_single_dimension_config():
    df = pd.DataFrame([
        {"body": "mars", "target": "J", "config": "solo geo", "analog": "A", "u": 0.2},
        {"body": "mars", "target": "K", "config": "solo geo", "analog": "A", "u": 0.4},
        {"body": "mars", "target": "J", "config": "todas", "analog": "A", "u": 0.9},
        {"body": "moon", "target": "L", "config": "solo geo", "analog": "A", "u": 0.8}])
    assert asp.analog_means(df, "mars", "geo")["A"] == pytest.approx(0.3)


def test_real_tags_file_is_valid_and_hash_is_stable():
    t = asp.load_tags()
    assert set(t["aspect"]) <= set(asp.ASPECTS) | {"ninguno"} and set(t["nivel"]) <= set(asp.LEVELS)
    assert t["name"].isin(asp.load_known()["name"]).all()  # cada etiqueta apunta a un análogo que existe
    assert len(asp.tags_hash()) == 64 and asp.tags_hash() == asp.tags_hash()
