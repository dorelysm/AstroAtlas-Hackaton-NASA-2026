"""Mars data.

Topography: MGS MOLA MEGDR 128 px/° (463 m) from the NASA PDS, read by rows with HTTP Range (see pds_dem.py).
thermal__*, ice__* and geo__*: NASA PDS products, see planetary.py and docs/reference/data-sources.md.

    python -m astroatlas.data.mars       # writes data/features/mars.parquet
"""
import pandas as pd

from ..config import FEATURES_WRITE_DIR
from .dem import build_target_features
from .planetary import add_properties
from .pds_dem import mola_dem
from .sites import load_sites

# Before: USGS mosaic. Now: the same data from the NASA PDS (rule: NASA sources only).
DEM = mola_dem


def download() -> None:
    raise NotImplementedError  # TES/THEMIS/SHARAD: see data/ode.py to locate the products


def build_features(include_unverified: bool = False, half_km: float = 25.0) -> pd.DataFrame:
    """Contract DataFrame (body='mars', with a `site` column): topo__* + thermal__*, ice__*, geo__* (planetary.py).

    Sites: base candidates + historical landings with verified coordinates (data/sites.py).
    """
    df = build_target_features("mars", DEM(), load_sites(include_unverified), half_km)
    return add_properties(df, "mars")


if __name__ == "__main__":
    FEATURES_WRITE_DIR.mkdir(parents=True, exist_ok=True)
    out = build_features()
    out.to_parquet(FEATURES_WRITE_DIR / "mars.parquet", index=False)
    cols = ["site", "topo__slope_mean_deg", "thermal__t_max_k", "thermal__t_range_k", "ice__water_frac",
            "geo__basalt_frac"]
    print(out[cols].round(3).to_string())
