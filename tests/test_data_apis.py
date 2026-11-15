"""Tests with simulated responses (no network). The live test is in docs/reference/nasa-apis.md."""
import math

import pytest

from astroatlas.data import earth, ode
from astroatlas.features import validate_features

POWER_OK = {"properties": {"parameter": {
    "T2M_MAX": {"ANN": 32.75}, "T2M_MIN": {"ANN": -4.33}, "PRECTOTCORR": {"ANN": 0.03}}}}
POWER_MISSING = {"properties": {"parameter": {
    "T2M_MAX": {"ANN": -999.0}, "T2M_MIN": {"ANN": -999.0}, "PRECTOTCORR": {"ANN": -999.0}}}}


def test_parse_power():
    f = earth.parse_power(POWER_OK)
    assert f["thermal__t_max_k"] == pytest.approx(305.9)
    assert f["thermal__t_range_k"] == pytest.approx(37.08)
    assert f["ice__water_frac"] == pytest.approx(0.006)


def test_parse_power_missing_is_nan_not_minus_999():
    assert all(math.isnan(v) for v in earth.parse_power(POWER_MISSING).values())


def test_build_features_meets_contract(monkeypatch):
    monkeypatch.setattr(earth, "get_json", lambda url: POWER_OK)
    df = earth.build_features(step_deg=60, workers=1, topo=False)
    validate_features(df, "earth")
    assert df["thermal__t_max_k"].notna().all()
    assert df["topo__slope_mean_deg"].isna().all()  # still without DEM


def test_failed_point_becomes_nan(monkeypatch):
    def boom(url):
        raise RuntimeError("429")
    monkeypatch.setattr(earth, "get_json", boom)
    df = earth.build_features(step_deg=90, workers=1, topo=False)
    assert df["thermal__t_max_k"].isna().all()


def test_ode_products_single_and_error(monkeypatch):
    one = {"ODEResults": {"Status": "Success", "Products": {"Product": {"Product_name": "A", "FilesURL": "u"}}}}
    monkeypatch.setattr(ode, "get_json", lambda url: one)
    df = ode.products("mars", "MGS", "MOLA", "MEGDR")
    assert list(df["Product_name"]) == ["A"]
    monkeypatch.setattr(ode, "get_json", lambda url: {"ODEResults": {"Status": "ERROR", "Error": "mal"}})
    with pytest.raises(RuntimeError):
        ode.count("moon", "LRO", "LOLA", "RDR")


def test_bbox_wraps_longitude():
    assert ode.bbox_around(-89.9, 0.0) == pytest.approx((-90, -88.9, 359.0, 1.0))
