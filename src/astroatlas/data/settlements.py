"""Viability by proximity to populated places (Earth only).

Source (NASA SEDAC): Global Rural-Urban Mapping Project, Version 1 (GRUMPv1): Settlement Points, Revision 01.
  Center for International Earth Science Information Network (CIESIN), Columbia University, et al. 2017.
  NASA Socioeconomic Data and Applications Center (SEDAC). https://doi.org/10.7927/H4BC3WG1
  70,629 settlements with latitude, longitude and population; 2.8 MB CSV (zip), downloaded with the Earthdata login.

Rule decided by the team (14 Nov 2026): a point is NOT VIABLE if there is a settlement of >= 1,000 inhabitants within 50 km.
It is a FLAG (`viable` column), not part of the score: it changes neither the ranking nor the validation with known analogs.

LIMITATIONS (from the SEDAC documentation and checked against the data):
  - "Best available" list, NOT exhaustive: the probability that a settlement is included grows with its population, so
    towns of 1,000 to 10,000 inhabitants are less well covered. Checked example: San Pedro de Atacama does not appear.
  - Data from 1990 to 2010; populations and settlements have changed.
  - Latitudes from -54.8° to 78.9°: no Antarctic stations or extreme Arctic settlements.
  - 1,629 points have no population (-999). They do not count for `viable`; they do for `dist_any_settlement_km` (warning).
  "viable" means "no known settlement of >= 1,000 inhabitants in this list within 50 km", not "uninhabited".

    python -m astroatlas.data.settlements        # adds the columns to earth.parquet, earth_sites.parquet and earth_usgs.parquet
"""
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.spatial import cKDTree

from ..config import FEATURES_WRITE_DIR, RAW_DIR
from . import edl
from .earth_geology import safe_extract

GRUMP_DIR = RAW_DIR / "sedac" / "grump_csv"
GRUMP_CSV = "grump-v1-settlement-points-rev01.csv"
MIN_POP = 1000
RADIUS_KM = 50.0
EARTH_R_KM = 6371.0
COLUMNS = ["dist_settlement_km", "settlement_name", "settlement_country", "settlement_pop",
           "dist_any_settlement_km", "viable"]


def ensure_grump(directory: Path = GRUMP_DIR) -> Path:
    """Path of the GRUMP CSV; downloads it (2.8 MB) and extracts it with path checking if missing."""
    csv = directory / GRUMP_CSV
    if not csv.exists():
        earthaccess = edl.login()
        res = earthaccess.search_data(short_name="CIESIN_SEDAC_GRUMPv1_STLMNT01", version="1.01")
        granule = [g for g in res if "csv" in g["meta"]["native-id"].lower()]
        if len(granule) != 1:
            raise RuntimeError("cannot find the GRUMP CSV granule in the NASA catalogue")
        zip_path = Path(str(earthaccess.download(granule, str(directory.parent))[0]))
        safe_extract(zip_path, directory)
    return csv


def load_settlements(path: Path | None = None) -> pd.DataFrame:
    """Settlements with `pop`: ES00POP (year 2000) if present, otherwise `Pop` of the available year; NaN if unknown (-999)."""
    # The CSV is UTF-8 with an invalid byte here and there, and in 493 names the space comes as "ÿ" (a source artefact).
    # The names are only for display; distances do not depend on them.
    d = pd.read_csv(path or ensure_grump(), encoding="utf-8", encoding_errors="replace", low_memory=False,
                    usecols=["Latitude", "Longitude", "Pop", "ES00POP", "Name1", "Country"])
    for c in ("Pop", "ES00POP"):
        d[c] = pd.to_numeric(d[c], errors="coerce")
    pop = d["ES00POP"].where(d["ES00POP"] > 0, d["Pop"].where(d["Pop"] > 0))
    clean = lambda c: d[c].astype(str).str.replace("ÿ", " ", regex=False).str.strip()  # noqa: E731
    out = pd.DataFrame({"name": clean("Name1"), "country": clean("Country"),
                        "lat": d["Latitude"], "lon": d["Longitude"], "pop": pop})
    return out.dropna(subset=["lat", "lon"]).reset_index(drop=True)


def _xyz(lat, lon) -> np.ndarray:
    la, lo = np.radians(np.asarray(lat, float)), np.radians(np.asarray(lon, float))
    return np.column_stack([np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)])


def _nearest_km(tree: cKDTree, lat, lon) -> tuple[np.ndarray, np.ndarray]:
    """(distance in km on the sphere, index) to the nearest point. 3D tree: it does not fail at the antimeridian or the poles."""
    chord, idx = tree.query(_xyz(lat, lon), k=1)
    return 2 * EARTH_R_KM * np.arcsin(np.clip(chord / 2, 0, 1)), idx


def add_viability(df: pd.DataFrame, settlements: pd.DataFrame | None = None, min_pop: float = MIN_POP,
                  radius_km: float = RADIUS_KM) -> pd.DataFrame:
    """Adds `dist_settlement_km` (to the nearest with >= min_pop inhabitants), its name, country and population,
    `dist_any_settlement_km` (to the nearest of any kind, also without population) and `viable` (distance >= radius_km)."""
    s = load_settlements() if settlements is None else settlements
    big = s[s["pop"] >= min_pop].reset_index(drop=True)
    if big.empty:
        raise ValueError(f"no settlement with >= {min_pop} habitantes")
    out = df.drop(columns=[c for c in COLUMNS if c in df.columns]).copy()
    d_big, i_big = _nearest_km(cKDTree(_xyz(big["lat"], big["lon"])), out["lat"], out["lon"])
    d_any, _ = _nearest_km(cKDTree(_xyz(s["lat"], s["lon"])), out["lat"], out["lon"])
    out["dist_settlement_km"] = d_big
    out["settlement_name"] = big["name"].to_numpy()[i_big]
    out["settlement_country"] = big["country"].to_numpy()[i_big]
    out["settlement_pop"] = big["pop"].to_numpy()[i_big]
    out["dist_any_settlement_km"] = d_any
    out["viable"] = d_big >= radius_km
    return out


def main() -> None:
    s = load_settlements()
    print(f"{len(s)} settlements; with >= {MIN_POP} habitantes: {int((s['pop'] >= MIN_POP).sum())}; without population: {int(s['pop'].isna().sum())}")
    for name in ("earth.parquet", "earth_sites.parquet", "earth_usgs.parquet"):
        p = FEATURES_WRITE_DIR / name
        if not p.exists():
            continue
        d = add_viability(pd.read_parquet(p), s)
        d.to_parquet(p, index=False)
        print(f"{name}: {len(d)} filas | viables (>= {RADIUS_KM:.0f} km from a settlement of >= {MIN_POP} hab.): "
              f"{int(d['viable'].sum())} ({d['viable'].mean():.0%})")


if __name__ == "__main__":
    main()
