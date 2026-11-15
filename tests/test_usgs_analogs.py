"""Tests sin red de usgs_analogs.py y aspect_usgs.py."""
import numpy as np
import pandas as pd
import pytest

from analogos import aspect_usgs as au
from analogos.data import usgs_analogs as ua


def test_dedupe_merges_same_name_nearby_but_keeps_distant_namesakes():
    df = pd.DataFrame({
        "name": ["Lockne", "Lockne", "Ritland", "Ritland", "Boltysh"], "analog_type": ["Impact Crater"] * 2 + ["Impact Crater", "Volcanic Eruption", "Impact Crater"],
        "lat": [63.0, 62.9167, 59.2, 64.93, 48.75], "lon": [14.8, 14.55, 6.4, -16.5, 32.2]})
    out = ua.dedupe_sites(df)
    assert len(out) == 4  # los dos Lockne (22 km) se fusionan; Ritland cráter y Ritland volcán son sitios distintos
    assert (out["name"] == "Ritland").sum() == 2 and (out["name"] == "Lockne").sum() == 1


def test_control_points_are_reproducible_in_range_and_away_from_craters():
    craters = pd.DataFrame({"lat": [10.0, 40.0], "lon": [20.0, -100.0]})
    a, b = ua.sample_control_points(300, craters, seed=1), ua.sample_control_points(300, craters, seed=1)
    assert a.equals(b) and not a.equals(ua.sample_control_points(300, craters, seed=2))
    assert a["lat"].between(*ua.LAT_RANGE).all() and a["lon"].between(-180, 180).all()
    d = ua.haversine_km(a["lat"].to_numpy()[:, None], a["lon"].to_numpy()[:, None],
                        craters["lat"].to_numpy()[None, :], craters["lon"].to_numpy()[None, :])
    assert d.min() >= ua.MIN_KM
    # uniforme en el seno de la latitud (área uniforme): menos puntos por grado hacia los polos
    assert (a["lat"].abs() < 30).mean() > (a["lat"].abs() > 55).mean()


def test_usable_controls_drop_ocean_ice_and_invalid():
    feats = pd.DataFrame({
        "valid_frac": [1.0, 1.0, 1.0, 0.2, 1.0], "topo__relief_m": [50.0, 0.0, 80.0, 60.0, 40.0],
        "elev_mean_m": [300.0, 0.0, 200.0, 100.0, 150.0], "geo_glim_rock_cells": [3, 3, 0, 3, 4],
        "topo__slope_mean_deg": [2.0, 0.0, 1.0, 1.0, np.nan]})
    assert list(ua.usable_controls(feats, 10).index) == [0]  # mar plano, hielo, DEM inválido y sin pendiente se descartan


def test_auc_rank_and_compare_detect_real_difference_and_null():
    rng = np.random.default_rng(0)
    pos, ctrl = rng.normal(0.7, 0.05, 80), rng.normal(0.4, 0.05, 80)
    assert au.auc_rank(pos, ctrl) == 1.0 and au.auc_rank(ctrl, pos) == 0.0
    r = au.compare(pos, ctrl, n_boot=200)
    assert r["senal"] and r["ci_lo"] > 0.5 and r["p_mannwhitney"] < 1e-6
    same = au.compare(rng.normal(0.5, 0.1, 100), rng.normal(0.5, 0.1, 100), n_boot=200)
    assert not same["senal"] and 0.4 < same["auc_rank"] < 0.6  # sin diferencia real: no hay señal
    assert au.compare([0.9], [0.1, 0.2])["estado"] == "no evaluable"
    assert au.auc_rank(np.array([0.5]), np.array([0.5])) == 0.5  # empates cuentan 0.5


def test_load_real_shapefile_if_present():
    if not (ua.USGS_DIR / "TerrestrialAnalogs.dbf").exists():
        pytest.skip("la capa del USGS no está descargada")
    pytest.importorskip("shapefile")
    df = ua.load_usgs_sites()
    assert len(df) == 192 and set(df["group"]) == {"crater", "dunes", "volcanic"}
    assert df["lat"].between(-90, 90).all() and df["lon"].between(-180, 180).all()
    assert df["analog_body"].notna().sum() == 1 and df.loc[df["analog_body"].notna(), "analog_body"].iloc[0] == "mars"
    assert len(ua.dedupe_sites(df)) < len(df)
