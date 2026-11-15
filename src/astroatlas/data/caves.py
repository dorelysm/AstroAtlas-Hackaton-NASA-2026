"""Caves and lava tubes as CONTEXT (not a model dimension).

Open sources (CC BY 4.0):
  - Moon: "Current Evidence of Lunar Lava Tubes and Associated Surface Features" (Losarcos and Dombard, Zenodo 10.5281/zenodo.20516852,
    Jun 2026), `Pit-locations` layer = 278 pits and skylights from the LROC QuickMap database (Wagner and Robinson).
  - Earth: Pyroduct Digital Catalog v1 (Romio and Lobosco 2024, Zenodo 10.5281/zenodo.14535886): 94 documented lava tubes
    in 8 countries. The catalogue holds ONLY region and name, NO coordinates; that is why cells cannot be flagged one by one on Earth.
  - Mars: Mars Global Cave Candidate Catalog (USGS, Cushing; PDS release 2019): 1,062 candidates with coordinates, type and priority.
    The USGS server blocks automatic download, so a team member downloaded it into data/raw/mgc3/. Note: the CSV header
    is scrambled; the real column order is that of the XML (ID_Tag, Longitude, Latitude, Type_Code, Priority, ...).

Why it is context only: on Earth the tubes have no coordinates, and on the Moon and Mars "a pit nearby" depends on it having
been detected in images. An Earth cell without documented tubes is not a cell without tubes.

    python -m astroatlas.data.caves            # adds pit columns to moon.parquet
"""
from pathlib import Path

import numpy as np
import pandas as pd

from ..config import FEATURES_WRITE_DIR, RAW_DIR
from ..validate import haversine_km

CAVES_DIR = RAW_DIR / "caves"
PITS_SHP = CAVES_DIR / "pits" / "x" / "pit-locations.shp"
MARS_CSV = RAW_DIR / "mgc3" / "mars_cave_catalog" / "data" / "Mars_Cave_Catalog.csv"
COLUMNS = ["pits_within_50km", "nearest_pit_km", "nearest_pit_name"]
MARS_COLUMNS = ["caves_within_50km", "nearest_cave_km", "nearest_cave_name"]


def load_pits(path: Path = PITS_SHP) -> pd.DataFrame:
    import shapefile

    r = shapefile.Reader(str(path), encoding="utf-8", encodingErrors="replace")
    names = [f[0] for f in r.fields[1:]]
    rows = [dict(zip(names, rec)) for rec in r.records()]
    d = pd.DataFrame(rows)[["Name", "Terrain", "HostFeatur", "Latitude", "Longitude", "Depth"]]
    d.columns = ["name", "terrain", "host", "lat", "lon", "depth_m"]
    d["depth_m"] = pd.to_numeric(d["depth_m"], errors="coerce")
    return d.dropna(subset=["lat", "lon"]).reset_index(drop=True)


def load_mars_caves(path: Path = MARS_CSV) -> pd.DataFrame:
    """Mars cave-entrance candidates. The (scrambled) CSV header is ignored and the XML order is used."""
    d = pd.read_csv(path, header=None, skiprows=1, names=["name", "lon", "lat", "type", "priority", "diam_m", "depth_m", "comment"])
    return d.dropna(subset=["lat", "lon"]).reset_index(drop=True)


def add_pit_context(df: pd.DataFrame, pits: pd.DataFrame, radius_km: float = 50.0, columns: list[str] | None = None) -> pd.DataFrame:
    """Number of items within `radius_km`, distance to the nearest and its name. Longitudes 0-360 east (same as moon/mars.parquet).
    `columns` = names of the 3 output columns (default: those of the lunar pits)."""
    cols = columns or COLUMNS
    out = df.drop(columns=[c for c in set(COLUMNS + MARS_COLUMNS) & set(cols) if c in df.columns]).copy()
    d = haversine_km(out["lat"].to_numpy()[:, None], out["lon"].to_numpy()[:, None],
                     pits["lat"].to_numpy()[None, :], pits["lon"].to_numpy()[None, :])
    out[cols[0]] = (d < radius_km).sum(axis=1)
    j = d.argmin(axis=1)
    out[cols[1]] = d[np.arange(len(out)), j]
    out[cols[2]] = pits["name"].to_numpy()[j]
    return out


def main() -> None:
    pits = load_pits()
    print(f"{len(pits)} pits; by terrain: {pits['terrain'].value_counts().to_dict()}")
    p = FEATURES_WRITE_DIR / "moon.parquet"
    d = add_pit_context(pd.read_parquet(p), pits)
    d.to_parquet(p, index=False)
    near = d[d["pits_within_50km"] > 0]
    print(f"moon.parquet: {len(near)} of {len(d)} targets with a pit within < 50 km")
    print(near[["site", "lat", "lon", "pits_within_50km", "nearest_pit_km", "nearest_pit_name"]].round(1).to_string(index=False))
    d[["site", "lat", "lon", *COLUMNS]].round(2).to_csv(FEATURES_WRITE_DIR / "moon_pits_context.csv", index=False)

    if MARS_CSV.exists():
        caves = load_mars_caves()
        print(f"\n{len(caves)} cave candidates on Mars; by type: {caves['type'].value_counts().to_dict()}")
        p = FEATURES_WRITE_DIR / "mars.parquet"
        m = add_pit_context(pd.read_parquet(p), caves, columns=MARS_COLUMNS)
        m.to_parquet(p, index=False)
        near = m.sort_values("nearest_cave_km")
        print(f"mars.parquet: {int((m['caves_within_50km'] > 0).sum())} of {len(m)} targets with a candidate within < 50 km")
        print(near[["site", "lat", "lon", *MARS_COLUMNS]].round(1).to_string(index=False))
        m[["site", "lat", "lon", *MARS_COLUMNS]].round(2).to_csv(FEATURES_WRITE_DIR / "mars_caves_context.csv", index=False)
    else:
        print("\nNo Mars catalogue (data/raw/mgc3/): it has to be downloaded by hand from the USGS.")


if __name__ == "__main__":
    main()
