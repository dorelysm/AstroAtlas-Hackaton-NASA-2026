"""Moon data.

Topography: LRO LOLA LDEM_256 (118 m) from the NASA PDS, read by rows with HTTP Range (see pds_dem.py).
thermal__*, ice__* and geo__*: NASA PDS products, see planetary.py and docs/reference/data-sources.md.

    python -m astroatlas.data.moon       # writes data/features/moon.parquet
"""
import pandas as pd

from ..config import FEATURES_WRITE_DIR
from .dem import build_target_features
from .planetary import add_properties
from .pds_dem import lola_dem
from .sites import load_sites

# Before: USGS mosaic. Now: the same data from the NASA PDS (rule: NASA sources only).
DEM = lola_dem


def download() -> None:
    raise NotImplementedError  # Diviner/LEND: see data/ode.py to locate the products


def build_features(include_unverified: bool = False, half_km: float = 25.0, only: list[str] | None = None) -> pd.DataFrame:
    """Contract DataFrame (body='moon', with a `site` column): topo__* + thermal__*, ice__*, geo__* (planetary.py).

    Sites: base candidates + historical landings with verified coordinates (data/sites.py).
    `only`: computes only those sites (by name). Useful to update a few without recomputing the polar ones, which
    require downloading ~600 MB of Diviner.
    """
    sites = load_sites(include_unverified)
    if only is not None:
        missing = set(only) - set(sites["site"])
        if missing:
            raise ValueError(f"unknown sites (check docs/catalog/known_landings.csv and the duplicate filter): {sorted(missing)}")
        sites = sites[sites["site"].isin(only)]
    df = build_target_features("moon", DEM(), sites, half_km)
    return add_properties(df, "moon")


def merge_site_rows(existing: pd.DataFrame, new: pd.DataFrame) -> pd.DataFrame:
    """Replaces in `existing` the rows of the sites present in `new` and adds the missing ones (key: `site`)."""
    return pd.concat([existing[~existing["site"].isin(new["site"])], new], ignore_index=True)


def update_sites(names: list[str]) -> pd.DataFrame:
    """Recomputes only `names` and merges them into data/features/moon.parquet (and moon.csv). Returns the full table."""
    path = FEATURES_WRITE_DIR / "moon.parquet"
    out = merge_site_rows(pd.read_parquet(path), build_features(only=names))
    out.to_parquet(path, index=False)
    out.to_csv(FEATURES_WRITE_DIR / "moon.csv", index=False)
    return out


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--only", nargs="+", help="update only these sites (names in quotes) instead of recomputing everything")
    a = ap.parse_args()
    FEATURES_WRITE_DIR.mkdir(parents=True, exist_ok=True)
    if a.only:
        out = update_sites(a.only)
    else:
        out = build_features()
        out.to_parquet(FEATURES_WRITE_DIR / "moon.parquet", index=False)
    cols = ["site", "topo__slope_mean_deg", "thermal__t_max_k", "thermal__t_range_k", "ice__water_frac",
            "geo__basalt_frac"]
    print(out[cols].round(3).to_string())
