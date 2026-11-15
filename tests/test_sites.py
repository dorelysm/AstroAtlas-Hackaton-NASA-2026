import pandas as pd
import pytest

from astroatlas.data.sites import load_sites
from astroatlas.validate import haversine_km


def test_default_sites_are_verified_and_clean():
    s = load_sites()
    assert s["site"].is_unique
    assert s[["lat", "lon"]].notna().all().all() and s["lon"].between(0, 360, inclusive="left").all()
    assert set(s["body"]) == {"moon", "mars"}
    assert {"target_base", "landing", "candidate_site"} <= set(s["kind"])
    assert not s["site"].str.contains("elipse", case=False).any()  # ellipse centre != real point
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
    # Gale (MSL candidate) and Curiosity are ~12 km apart: only one should remain
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
    assert list(s["site"]) == ["A", "C"]  # B is ~5 km from A (duplicate); D is not verified
    assert s.loc[0, "lon"] == 350.0


# --- update with the LROC tables (28 Jul 2016) ---
def test_lunar_sites_use_lroc_coordinates_and_include_the_new_ones():
    s = load_sites().set_index("site")
    # Surveyor: LROC values (before, those from NSSDCA, shifted 1 to 4 km)
    assert (s.loc["Surveyor 1", "lat"], s.loc["Surveyor 1", "lon"]) == pytest.approx((-2.4745, 316.6602))
    assert (s.loc["Surveyor 7", "lat"], s.loc["Surveyor 7", "lon"]) == pytest.approx((-40.9812, 348.4873))
    # sitios nuevos
    for name, lat, lon in [("Luna 16", -0.5137, 56.3638), ("Luna 17", 38.23764, 324.99837), ("Luna 20", 3.7863, 56.6242),
                           ("Luna 21", 25.9994, 30.4076), ("Luna 23", 12.6667, 62.1511), ("Chang'e 3", 44.1214, 340.4883)]:
        assert (s.loc[name, "lat"], s.loc[name, "lon"]) == pytest.approx((lat, lon)), name
    # Luna 24 is 2.3 km from Luna 23 and Surveyor 3 is 0.2 km from Apollo 12: same site, not counted twice
    assert "Luna 24" not in s.index and "Surveyor 3" not in s.index
    assert (s["body"] == "moon").sum() == 21


def test_apollo_coordinates_agree_with_lroc_within_a_few_meters():
    s = load_sites().set_index("site")
    lroc = {"Apollo 11 LM": (0.67416, 23.47314), "Apollo 12 LM": (-3.0128, 336.5781), "Apollo 14 LM": (-3.64589, 342.52806),
            "Apollo 15 LM": (26.13239, 3.63330), "Apollo 16 LM": (-8.9734, 15.5011), "Apollo 17 LM": (20.1911, 30.7723)}
    for name, (lat, lon) in lroc.items():
        assert (s.loc[name, "lat"], s.loc[name, "lon"]) == pytest.approx((lat, lon), abs=1e-4), name  # 1e-4° = 3 m


def test_merge_site_rows_replaces_and_adds():
    from astroatlas.data.moon import merge_site_rows

    old = pd.DataFrame({"site": ["A", "B"], "v": [1, 2]})
    new = pd.DataFrame({"site": ["B", "C"], "v": [20, 30]})
    out = merge_site_rows(old, new).set_index("site")["v"].to_dict()
    assert out == {"A": 1, "B": 20, "C": 30}
