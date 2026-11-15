"""Segundo conjunto de análogos (docs/PREREGISTRO_VALIDACION2.md): integridad de la lista congelada y de las funciones."""
import hashlib

import numpy as np
import pandas as pd

from analogos.config import DOCS
from analogos.validate import haversine_km
from analogos.validation2 import CSV, TAGS, summarize_v2


def _sha(path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()[:16]  # insensible a CRLF/LF


def test_frozen_lists_unchanged():
    assert _sha(CSV) == "ec1a07d1da462b70"
    assert _sha(TAGS) == "9612fd97ab33f8d6"


def test_independence_rule_100_km():
    new = pd.read_csv(CSV)
    old = pd.concat([pd.read_csv(DOCS / "analogos_conocidos.csv"), pd.read_csv(DOCS / "analogos_ampliado.csv")])
    for r in new.itertuples():
        assert haversine_km(r.lat, r.lon, old["lat"].to_numpy(), old["lon"].to_numpy()).min() >= 100
    for i in range(len(new)):
        for j in range(i + 1, len(new)):
            assert haversine_km(new.lat[i], new.lon[i], new.lat[j], new.lon[j]) >= 100


def test_tags_refer_to_listed_sites_with_source_level():
    tags, new = pd.read_csv(TAGS), pd.read_csv(CSV)
    assert set(tags["name"]) <= set(new["name"])
    assert set(tags["nivel"]) <= {"fuente", "nota"}


def test_summarize_v2_reports_union_minus_pa():
    res = pd.DataFrame({"body": "mars", "analog": list("abcd"), "P_A": [0.5, 0.6, 0.7, 0.8], "u_B": [0.4, 0.5, 0.6, 0.7],
                        "u_union": [0.6, 0.7, 0.8, 0.9]})
    s = summarize_v2(res).set_index("medida")
    assert np.isclose(s.loc["u_union - P_A", "u_medio"], 0.1)
    assert np.isclose(s.loc["u_union", "u_medio"], 0.75)
