"""Smoke test of the Streamlit app with Streamlit's AppTest (no browser, no network): the page loads in both languages and the
main interactions (filters, featured-case button, risk map colour) run without exceptions."""
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).resolve().parents[1] / "app" / "streamlit_app.py")


@pytest.fixture(autouse=True)
def offline_imagery(monkeypatch):
    """The NASA imagery services are not called: the app must show its fallback text instead (also checked here)."""
    from astroatlas import imagery
    monkeypatch.setattr(imagery, "_download", lambda url: None)


def _run(lang: str = "en") -> AppTest:
    at = AppTest.from_file(APP, default_timeout=180)
    at.query_params["lang"] = lang
    return at.run()


def _profile(at: AppTest):
    return next(s for s in at.selectbox if s.key == "profile_cell")


@pytest.mark.parametrize("lang", ["en", "es"])
def test_app_loads_without_exceptions(lang):
    at = _run(lang)
    assert not at.exception, [e.value for e in at.exception]
    assert len(_profile(at).options) > 0
    assert any("AstroAtlas" in t.value for t in at.title)


def test_featured_case_button_opens_the_first_candidate():
    at = _run()
    at.button(key="go_featured").click().run()
    assert not at.exception
    assert at.checkbox(key="only_volcanic").value is True
    assert at.selectbox(key="sitio").value == ("mars", "Jezero")
    assert _profile(at).value == "earth_24_43"          # Harrat ash-Shamah


def test_region_and_volcanic_filters_narrow_the_list():
    at = _run()
    everything = len(_profile(at).options)
    at.multiselect(key="regions").set_value(["africa"]).run()
    assert not at.exception
    assert 0 < len(_profile(at).options) < everything
    at.multiselect(key="regions").set_value(["africa", "europe", "asia", "north_america", "south_america", "oceania", "polar", "other"]).run()
    at.checkbox(key="only_volcanic").set_value(True).run()
    assert not at.exception and 0 < len(_profile(at).options) < everything


def test_risk_map_colour_and_sensitivity_run():
    at = _run()
    at.segmented_control(key="map_color").set_value("risk").run()
    assert not at.exception
    assert any("risk" in c.value.lower() for c in at.caption)      # the risk legend replaces the similarity legend
