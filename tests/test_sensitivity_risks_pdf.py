"""Sensitivity chart data, field-site risk indicators and the PDF site report (demo data; no network)."""
import numpy as np
import pandas as pd
import pytest

from astroatlas.config import DIMENSIONS
from astroatlas.features import load_features
from astroatlas.i18n import TEXTS
from astroatlas.report_pdf import build_report, clean
from astroatlas.risks import KEYS, RULES, level_name, risk_levels, target_slope_level
from astroatlas.sensitivity import aspect_scenarios, rank_span, sensitivity
from astroatlas.similarity import fit_topo_model, site_profiles


@pytest.fixture(scope="module")
def setup():
    earth, mars = load_features("earth"), load_features("mars")
    return earth, site_profiles(mars).loc["Jezero"], fit_topo_model(earth)


def test_scenarios_switch_off_one_aspect_at_a_time():
    w = {d: 1.0 for d in DIMENSIONS}
    sc = aspect_scenarios(w)
    assert [k for k, _ in sc] == ["all", *DIMENSIONS]
    assert all(sum(v == 0 for v in ws.values()) == (0 if k == "all" else 1) for k, ws in sc)
    assert [k for k, _ in aspect_scenarios({**{d: 0.0 for d in DIMENSIONS}, "topo": 1.0})] == ["all"]   # one aspect: nothing to compare


def test_sensitivity_ranks_the_place_in_every_scenario(setup):
    earth, profile, topo = setup
    w = {d: 1.0 for d in DIMENSIONS}
    best = str(earth.iloc[0]["cell_id"])
    tab = sensitivity(earth, profile, w, topo, best)
    assert list(tab["scenario"]) == ["all", *DIMENSIONS]
    assert (tab["n"] > 0).all() and tab["rank"].between(1, tab["n"]).all()
    # the rank in the "all" scenario matches the plain ranking
    from astroatlas.similarity import rank_cells
    r = rank_cells(earth, profile, w, topo).sort_values("score", ascending=False).reset_index(drop=True)
    assert tab.loc[0, "rank"] == r.index[r["cell_id"].astype(str) == best][0] + 1
    lo, hi = rank_span(tab)
    assert 1 <= lo <= hi


def test_sensitivity_respects_the_visible_cells(setup):
    earth, profile, topo = setup
    w = {d: 1.0 for d in DIMENSIONS}
    ids = set(map(str, earth["cell_id"].iloc[:50]))
    tab = sensitivity(earth, profile, w, topo, str(earth.iloc[0]["cell_id"]), ids)
    assert (tab["n"] <= 50).all()
    hidden = sensitivity(earth, profile, w, topo, str(earth.iloc[200]["cell_id"]), ids)
    assert hidden["rank"].isna().all()   # a place that is not visible has no rank


def test_risk_levels_follow_the_thresholds():
    df = pd.DataFrame({"topo__slope_p90_deg": [2.0, 9.0, 20.0, np.nan], "thermal__t_max_k": [300.0, 310.0, 325.0, 300.0],
                       "thermal_lst_night_min_k": [260.0, 245.0, 230.0, 260.0], "dust_surface_ugm3": [1.0, 80.0, 200.0, 1.0]})
    r = risk_levels(df)
    assert list(r["slope"].fillna(-1)) == [0, 1, 2, -1]
    assert list(r["heat"]) == [0, 1, 2, 0]
    assert list(r["cold"]) == [0, 1, 2, 0]                 # colder is riskier
    assert list(r["dust"]) == [0, 1, 2, 0]
    assert r["wind"].isna().all()                          # missing columns stay "no data"
    assert r["overall"].iloc[2] == 2 and r["overall"].iloc[0] == 0
    assert set(r.columns) == {*KEYS, "overall"} and set(KEYS) == set(RULES)


def test_one_high_indicator_is_never_hidden_by_the_average():
    r = risk_levels(pd.DataFrame({"thermal__t_max_k": [325.0], "topo__slope_p90_deg": [1.0], "dust_surface_ugm3": [1.0],
                                  "wind10m_ms": [1.0], "dist_settlement_km": [10.0]}))
    assert r["heat"].iloc[0] == 2 and r["overall"].iloc[0] == 1


def test_level_names_and_target_slope():
    assert [level_name(x) for x in (0, 1, 2, np.nan, None)] == ["low", "medium", "high", "unknown", "unknown"]
    v, lvl = target_slope_level(pd.Series({"topo__slope_p90_deg": 16.0}))
    assert v == 16.0 and lvl == 2
    assert np.isnan(target_slope_level(pd.Series({"x": 1}))[0])


def test_demo_earth_has_all_risk_columns_and_a_spread_of_levels():
    r = risk_levels(load_features("earth"))
    assert r["overall"].notna().all() and r["overall"].nunique() == 3


def test_new_texts_exist_in_both_languages():
    for key in [k for k in TEXTS if k.startswith(("sens_", "riesgo_", "r_", "rv_", "pdf_", "mapa_color", "leyenda_riesgo", "tooltip_riesgo"))]:
        assert {"es", "en"} <= set(TEXTS[key]), key


def test_clean_makes_text_latin1_safe():
    s = clean("≥ 8° · µg/m³ ≈ 5 − 2 … ñ ‘x’ 日本")
    s.encode("latin-1")
    assert "°" in s and "ñ" in s


@pytest.mark.parametrize("lang", ["en", "es"])
def test_pdf_report_is_a_valid_pdf(lang):
    d = {"date": "2026-11-15", "place": "Harrat ash-Shamah", "country": "Syria / Jordan", "site": "Jezero", "body_name": "Mars",
         "coords": "32.5° N, 37.5° E", "terrain": "volcanic rock, flat", "match_pct": 82, "n_aspects": 3, "n_total": 4,
         "aspects": [{"name": "Terrain", "pct": 53, "level": "Moderate match", "text": "Somewhat flatter than Jezero."},
                     {"name": "Temperature", "pct": None, "level": "Not compared", "text": "No Mars temperature map."}],
         "reliability": {"nivel": "Low confidence", "pct": 60, "lo": 52, "hi": 67, "n": 40, "texto": "Recognizes dry, volcanic places."},
         "sensitivity": {"summary": "Robust: ...", "rows": [{"scenario": "All aspects", "rank": "#5 / 700", "score": "82%"}]},
         "risk_overall": ("medium", "medium"),
         "risks": [{"name": "Slope", "level": "low", "level_text": "low", "value": "3.1° (p90)"},
                   {"name": "Dust", "level": "unknown", "level_text": "no data", "value": "-"}],
         "target_risk": "At the Jezero site itself: slope 5° (low).", "limits": ["Gravity: 38% of Earth's", "Thin atmosphere"],
         "images": [(None, "Jezero (Mars)", "NASA/JPL/USGS"), (None, "Harrat ash-Shamah", "NASA GIBS")]}
    pdf = build_report(d, lang)
    assert pdf[:5] == b"%PDF-" and len(pdf) > 2000 and b"%%EOF" in pdf[-20:]
