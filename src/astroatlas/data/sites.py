"""Moon and Mars target sites: candidate base sites + historical landings.

Sources (see docs/reference/data-sources.md):
  - docs/catalog/target_sites.csv        -> kind="target_base"    (base candidates: Shackleton, Jezero...)
  - docs/catalog/known_landings.csv  -> kind="landing"        (landed missions)
                                       kind="candidate_site" (MSL candidates: Eberswalde, Holden...)

By default only rows with VERIFIED coordinates are included. Rows without
coordinates and landing-ellipse centres (not the real point) are always excluded.
"""
import numpy as np
import pandas as pd

from ..config import LANDINGS_CSV, SITES_CSV
from ..validate import haversine_km

COLUMNS = ["site", "body", "lat", "lon", "kind", "source"]


def _dedupe(df: pd.DataFrame, min_km: float) -> pd.DataFrame:
    """Within each body, drops the sites closer than `min_km` to one already accepted
    (order matters: base sites come first)."""
    keep = []
    for _, g in df.groupby("body", sort=False):
        kept: list[int] = []
        for i, r in g.iterrows():
            if all(haversine_km(r.lat, r.lon, df.at[j, "lat"], df.at[j, "lon"]) >= min_km for j in kept):
                kept.append(i)
        keep += kept
    return df.loc[sorted(keep)]


def load_sites(include_unverified: bool = False, dedupe_km: float = 15.0,
               sites_csv=SITES_CSV, landings_csv=LANDINGS_CSV) -> pd.DataFrame:
    base = pd.read_csv(sites_csv)
    base = pd.DataFrame({"site": base["site"], "body": base["body"], "lat": base["lat"],
                         "lon": base["lon"] % 360, "kind": "target_base", "source": "catalog/target_sites.csv"})

    land = pd.read_csv(landings_csv).dropna(subset=["lat", "lon_east_0_360"])
    status = land["status"].fillna("").str.lower()
    keep = ~land["mission"].str.contains("centro de elipse", case=False)
    if not include_unverified:
        keep &= status.str.startswith("verificado")
    land, status = land[keep], status[keep]
    land = pd.DataFrame({
        "site": land["mission"], "body": land["body"], "lat": land["lat"],
        "lon": land["lon_east_0_360"] % 360,
        "kind": np.where(status.str.contains("candidato"), "candidate_site", "landing"),
        "source": "catalog/known_landings.csv"})

    out = pd.concat([base, land], ignore_index=True)[COLUMNS]
    return _dedupe(out, dedupe_km).reset_index(drop=True)
