"""Datos de Marte (responsable: persona 4).

Topografía: MOLA 463 m (USGS), leído por ventanas desde la URL (sin bajar los 2.1 GB).
Pendientes: thermal__* (TES/THEMIS), ice__* (SHARAD/GRS) y geo__* (CRISM).

    python -m analogos.data.mars       # escribe data/features/mars.parquet
"""
import pandas as pd

from ..config import FEATURES_DIR
from .dem import build_target_features
from .sites import load_sites

DEM_URL = "https://planetarymaps.usgs.gov/mosaic/Mars_MGS_MOLA_DEM_mosaic_global_463m.tif"


def download() -> None:
    raise NotImplementedError  # TES/THEMIS/SHARAD: ver data/ode.py para localizar los productos


def build_features(include_unverified: bool = False, half_km: float = 25.0) -> pd.DataFrame:
    """DataFrame del contrato (body='mars', con columna `site`). Por ahora solo topo__*.

    Sitios: candidatos a base + aterrizajes históricos con coordenadas verificadas (data/sites.py).
    """
    return build_target_features("mars", DEM_URL, load_sites(include_unverified), half_km)


if __name__ == "__main__":
    FEATURES_DIR.mkdir(parents=True, exist_ok=True)
    out = build_features()
    out.to_parquet(FEATURES_DIR / "mars.parquet", index=False)
    print(out[["site", "topo__slope_mean_deg", "topo__rough_1km_m", "elev_mean_m", "valid_frac"]].round(2))
