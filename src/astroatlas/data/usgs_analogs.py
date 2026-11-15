"""Layer "Known Terrestrial Analog Sites for Planetary Science" (USGS, Hunter 2020, DOI 10.5066/P9J72921, public domain).

Shapefile of 192 points with `Name`, `AnalogType` (Impact Crater 190, Dunes 1, Volcanic Eruption 1), `Lat`, `Lon` and
`AnalogBody` (empty in 191). According to its metadata: "to identify areas of research, not for analysis"; the
points may be up to 10 km from the centroid. The craters come from the Earth Impact Database (Univ. of New Brunswick).
The file is downloaded by a team member into data/raw/usgs_analogs/ (the server blocks automatic download).

Here, for each site and for a CONTROL group of random points on dry land, only the variables needed for the
per-aspect validation are computed (topography and geology). The control is defined in
docs/validation/per-aspect-validation.md (protocol fixed before computing any score).

    python -m astroatlas.data.usgs_analogs     # writes data/features/earth_usgs.parquet
"""
import numpy as np
import pandas as pd

from ..config import FEATURES, FEATURES_WRITE_DIR, RAW_DIR
from ..validate import haversine_km
from . import earth, earth_geology

USGS_DIR = RAW_DIR / "usgs_analogs" / "TerrestrialAnalogs"
GROUPS = {"Impact Crater": "crater", "Dunes": "dunes", "Volcanic Eruption": "volcanic"}
SEED = 20261114
N_CONTROL = 200
LAT_RANGE = (-35.0, 76.0)  # the latitude range of the layer's craters
MIN_KM = 50.0


def load_usgs_sites(directory=USGS_DIR) -> pd.DataFrame:
    """Reads the shapefile with pyshp (pure Python: it executes nothing from the file)."""
    import shapefile

    cpg = directory / "TerrestrialAnalogs.cpg"
    enc = cpg.read_text().strip() if cpg.exists() else "utf-8"
    recs = [r.as_dict() for r in shapefile.Reader(str(directory / "TerrestrialAnalogs"), encoding=enc).records()]
    df = pd.DataFrame(recs).rename(columns={"Name": "name", "AnalogType": "analog_type", "Lat": "lat", "Lon": "lon",
                                            "AnalogBody": "analog_body"})
    df["name"] = df["name"].astype(str).str.strip()
    df["analog_body"] = df["analog_body"].astype(str).str.strip().str.lower().replace({"": None, "nan": None})
    df["group"] = df["analog_type"].map(GROUPS)
    if df["group"].isna().any():
        raise ValueError(f"unknown analog types: {set(df.loc[df['group'].isna(), 'analog_type'])}")
    return df


def dedupe_sites(df: pd.DataFrame, km: float = MIN_KM) -> pd.DataFrame:
    """Merges the records with the same name and type within `km` (it is the same site with another coordinate)."""
    keep = []
    for _, g in df.groupby(["name", "analog_type"], sort=False):
        kept: list[int] = []
        for i, r in g.iterrows():
            if all(haversine_km(r.lat, r.lon, df.at[j, "lat"], df.at[j, "lon"]) >= km for j in kept):
                kept.append(i)
        keep += kept
    return df.loc[sorted(keep)].reset_index(drop=True)


def sample_control_points(n: int, exclude: pd.DataFrame, seed: int = SEED, lat_range=LAT_RANGE,
                          min_km: float = MIN_KM) -> pd.DataFrame:
    """n random points: latitude uniform in its sine (uniform area), longitude uniform, at >= min_km from `exclude`."""
    rng = np.random.default_rng(seed)
    z0, z1 = np.sin(np.radians(lat_range))
    out: list[tuple[float, float]] = []
    while len(out) < n:
        lat = float(np.degrees(np.arcsin(rng.uniform(z0, z1))))
        lon = float(rng.uniform(-180, 180))
        if haversine_km(lat, lon, exclude["lat"].to_numpy(), exclude["lon"].to_numpy()).min() >= min_km:
            out.append((lat, lon))
    return pd.DataFrame({"cell_id": [f"control_{i}" for i in range(n)], "body": "earth", "name": "control",
                         "lat": [a for a, _ in out], "lon": [b for _, b in out], "group": "control"})


def site_features(points: pd.DataFrame, workers: int = 8) -> pd.DataFrame:
    """Topography (Copernicus, 50 km window) and geology (GLiM, 75 km window) of each point."""
    topo = earth.build_topography(points, workers=workers)
    grid, names, lats, lons = earth_geology.load_glim()
    geo = earth_geology.geology_features(points, grid, names, lats, lons)
    out = pd.concat([points, topo, geo], axis=1)
    for col in FEATURES:  # thermal and ice are not computed for these sites: they are not needed and stay NaN
        if col not in out:
            out[col] = np.nan
    return out


def usable_controls(feats: pd.DataFrame, n: int = N_CONTROL) -> pd.DataFrame:
    """First n controls (in sampling order) with a valid DEM that are not flat sea nor ice, water or no data."""
    ok = ((feats["valid_frac"].fillna(0) >= 0.5) & ~earth.is_flat_water(feats) & (feats["geo_glim_rock_cells"] > 0)
          & feats["topo__slope_mean_deg"].notna())
    return feats[ok].head(n).reset_index(drop=True)


def build(workers: int = 8, n_control: int = N_CONTROL, candidates_factor: int = 4) -> pd.DataFrame:
    sites = dedupe_sites(load_usgs_sites())
    sites = sites.assign(cell_id=[f"usgs_{i}" for i in range(len(sites))], body="earth")
    controls = sample_control_points(n_control * candidates_factor, sites)
    feats_sites = site_features(sites[["cell_id", "body", "name", "lat", "lon", "group", "analog_type", "analog_body"]], workers)
    feats_ctrl = usable_controls(site_features(controls, workers), n_control)
    return pd.concat([feats_sites, feats_ctrl], ignore_index=True)


def main() -> None:
    FEATURES_WRITE_DIR.mkdir(parents=True, exist_ok=True)
    out = build()
    out.to_parquet(FEATURES_WRITE_DIR / "earth_usgs.parquet", index=False)
    print(out["group"].value_counts().to_dict(), "| with topography:", int(out["topo__slope_mean_deg"].notna().sum()))


if __name__ == "__main__":
    main()
