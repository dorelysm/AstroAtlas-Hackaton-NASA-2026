"""Tests of data/settlements.py and its use in pipeline.py and validate.py (no network)."""
import numpy as np
import pandas as pd
import pytest

from astroatlas import pipeline as pl
from astroatlas.data import settlements as st
from astroatlas.validate import novel_candidates


def _s(rows):
    return pd.DataFrame(rows, columns=["name", "country", "lat", "lon", "pop"])


def _pts(*latlon):
    return pd.DataFrame({"cell_id": [f"c{i}" for i in range(len(latlon))], "lat": [a for a, _ in latlon], "lon": [b for _, b in latlon]})


def test_load_settlements_picks_best_population_and_handles_unknown(tmp_path):
    csv = tmp_path / "g.csv"
    lines = ["OBJECTID,Latitude,Longitude,Pop,ES00POP,Name1,Country",
             "1,10,20,-999,5000,Alfa,Chile",                 # ES00POP manda
             "2,11,21,3000,-999,Bêta,Perú",                   # without ES00POP: it uses Pop (with an accent, UTF-8)
             "3,12,22,-999,-999,SanÿGama,Perú"]          # without population; ÿ = space in the source
    csv.write_bytes(("\n".join(lines) + "\n").encode("utf-8"))
    s = st.load_settlements(csv)
    assert list(s["pop"].fillna(-1)) == [5000, 3000, -1]
    assert s.loc[1, "name"] == "Bêta" and s.loc[2, "name"] == "San Gama"  # the accent is kept and the "ÿ" becomes a space


def test_threshold_is_exactly_50_km_around_a_big_settlement():
    s = _s([("Pueblo", "X", 0.0, 0.0, 5000)])
    out = st.add_viability(_pts((0, 0.43), (0, 0.47), (0, 0.0)), s)  # 1° = 111.2 km: 47.8 km, 52.3 km, 0 km
    assert out["dist_settlement_km"].round(1).tolist() == [47.8, 52.3, 0.0]
    assert out["viable"].tolist() == [False, True, False]
    assert out["settlement_name"].eq("Pueblo").all() and out["settlement_pop"].eq(5000).all()


def test_population_threshold_and_unknown_population():
    far = ("Lejana", "X", 60.0, 100.0, 50000)  # a large settlement very far away, so the list never ends up with none
    small = _s([("Aldea", "X", 0.0, 0.1, 999), ("Sinpop", "X", 0.0, -0.1, np.nan), far])
    r = st.add_viability(_pts((0, 0)), small)
    assert r["viable"].iloc[0]  # 999 inhabitants and the one of unknown population do NOT disqualify the point
    assert r["settlement_name"].iloc[0] == "Lejana" and r["dist_settlement_km"].iloc[0] > 1000
    # but the distance to ANY settlement (also without population) remains as a warning
    assert r["dist_any_settlement_km"].iloc[0] == pytest.approx(11.1, abs=0.1)
    with_villa = st.add_viability(_pts((0, 0)), _s([("Villa", "X", 0.0, 0.1, 1000), far]))
    assert not with_villa["viable"].iloc[0] and with_villa["settlement_name"].iloc[0] == "Villa"  # 1,000 does count
    with pytest.raises(ValueError, match="no settlement"):  # without any large settlement nothing is marked viable
        st.add_viability(_pts((0, 0)), _s([("Aldea", "X", 0.0, 0.1, 999)]))


def test_distance_is_correct_across_antimeridian_and_at_the_pole():
    s = _s([("Fiyi", "X", 0.0, 179.9, 9000), ("Polo", "X", 89.9, 0.0, 9000)])
    out = st.add_viability(_pts((0.0, -179.9), (89.9, 180.0)), s)
    assert out["dist_settlement_km"].round(1).tolist() == [22.2, 22.2]  # 0.2° across ±180° and the pole
    assert out["viable"].tolist() == [False, False]


def test_add_viability_is_idempotent_and_keeps_rows_and_other_columns():
    s = _s([("A", "X", 10.0, 10.0, 8000)])
    base = _pts((10, 10), (40, 40)).assign(keep=[1, 2])
    once = st.add_viability(base, s)
    twice = st.add_viability(once, s)
    assert once.equals(twice) and list(twice["keep"]) == [1, 2] and len(twice) == 2
    assert [c for c in st.COLUMNS if c in twice.columns] == st.COLUMNS and not twice.columns.duplicated().any()


def test_attach_viability_to_a_ranking_keeps_order_and_scores():
    earth = _pts((0, 0), (0, 1), (0, 2)).assign(viable=[True, False, True], dist_settlement_km=[90.0, 10.0, 70.0],
                                                 settlement_name=["a", "b", "c"], settlement_pop=1, dist_any_settlement_km=5.0)
    ranked = pd.DataFrame({"cell_id": ["c2", "c0", "c1"], "score": [0.9, 0.5, 0.1], "rank": [1, 2, 3]})
    out = pl.attach_viability(ranked, earth)
    assert list(out["cell_id"]) == ["c2", "c0", "c1"] and list(out["score"]) == [0.9, 0.5, 0.1]  # the order does not change
    assert out.set_index("cell_id")["viable"].to_dict() == {"c2": True, "c0": True, "c1": False}
    assert pl.attach_viability(ranked, earth.drop(columns=["viable"]).iloc[:, :3]).shape == (3, 3)  # without viability columns: it does nothing


def test_novel_candidates_viable_only_filters_but_the_default_does_not():
    ranked = pd.DataFrame({"cell_id": list("abcd"), "lat": [0.0] * 4, "lon": [100.0, 110.0, 120.0, 130.0],
                           "score": [0.9, 0.8, 0.7, 0.6], "viable": [False, True, np.nan, False]})
    known = pd.DataFrame({"name": ["k"], "lat": [60.0], "lon": [-100.0]})
    assert list(novel_candidates(ranked, known, n=10)["cell_id"]) == list("abcd")  # by default it is not filtered
    assert list(novel_candidates(ranked, known, n=10, viable_only=True)["cell_id"]) == ["b", "c"]  # NaN is treated as viable
    assert list(novel_candidates(ranked.drop(columns="viable"), known, n=10, viable_only=True)["cell_id"]) == list("abcd")


def test_real_grump_file_if_present():
    if not (st.GRUMP_DIR / st.GRUMP_CSV).exists():
        pytest.skip("GRUMP no descargado")
    s = st.load_settlements()
    assert len(s) == 70629 and (s["pop"] >= st.MIN_POP).sum() > 50_000
    out = st.add_viability(_pts((28.96, -13.55), (23.0, 13.0), (-77.5, 162.0)), s)  # Reef, centre of the Sahara, Dry Valleys
    assert out["viable"].tolist() == [False, True, True] and out["settlement_name"].iloc[0] == "Arrecife"
