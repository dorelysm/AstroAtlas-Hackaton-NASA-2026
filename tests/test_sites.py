import pandas as pd
import pytest

from analogos.data.sites import load_sites
from analogos.validate import haversine_km


def test_default_sites_are_verified_and_clean():
    s = load_sites()
    assert s["site"].is_unique
    assert s[["lat", "lon"]].notna().all().all() and s["lon"].between(0, 360, inclusive="left").all()
    assert set(s["body"]) == {"moon", "mars"}
    assert {"target_base", "landing", "candidate_site"} <= set(s["kind"])
    assert not s["site"].str.contains("elipse", case=False).any()  # centro de elipse != punto real
    assert not s["site"].str.contains("Artemis|Zhurong|Chandrayaan|SLIM|Beagle|Polar Lander").any()
    assert {"Apollo 11 LM", "Surveyor 1", "Viking 1", "Spirit (MER-A)", "Shackleton rim", "Jezero"} <= set(s["site"])
    counts = s["body"].value_counts()
    assert counts["moon"] >= 12 and counts["mars"] >= 10


def test_unverified_adds_more_but_never_rows_without_coordinates():
    base, extra = load_sites(), load_sites(include_unverified=True)
    assert len(extra) > len(base)
    assert {"Chandrayaan-3 Vikram", "SLIM", "Zhurong (Tianwen-1)"} <= set(extra["site"])
    assert not extra["site"].str.contains("Artemis|InSight \\(centro").any()


def test_no_two_sites_closer_than_dedupe_distance():
    s = load_sites()
    for _, g in s.groupby("body"):
        for i, a in g.iterrows():
            others = g.drop(index=i)
            if len(others):
                assert haversine_km(a.lat, a.lon, others["lat"].to_numpy(), others["lon"].to_numpy()).min() >= 15.0
    # Gale (candidato MSL) y Curiosity están a ~12 km: solo debe quedar uno
    assert s["site"].str.contains("Gale|Curiosity").sum() == 1


def test_apollo_12_longitude_is_converted_to_east_positive():
    s = load_sites().set_index("site")
    assert s.loc["Apollo 12 LM", "lon"] == pytest.approx(336.5781, abs=1e-3)


def test_custom_csv_inputs(tmp_path):
    base = tmp_path / "base.csv"
    base.write_text("site,body,lat,lon\nA,moon,0,-10\nB,moon,0.05,-10\n")
    land = tmp_path / "land.csv"
    land.write_text("body,mission,lat,lon_east_0_360,status\nmoon,C,10,20,verificado\nmoon,D,11,21,NO VERIFICADO\n")
    s = load_sites(sites_csv=base, landings_csv=land)
    assert list(s["site"]) == ["A", "C"]  # B está a ~5 km de A (duplicado); D no verificado
    assert s.loc[0, "lon"] == 350.0
