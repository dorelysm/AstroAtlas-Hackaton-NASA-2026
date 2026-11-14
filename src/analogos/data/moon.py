"""Datos de la Luna (responsable: persona 3).

Topografía: LOLA 118 m (USGS), leído por ventanas desde la URL (sin bajar los 8.5 GB).
Pendientes: thermal__* (Diviner), ice__* (LEND/Mini-RF) y geo__* (LROC/M3).

    python -m analogos.data.moon       # escribe data/features/moon.parquet
"""
import pandas as pd

from ..config import FEATURES_DIR
from .dem import build_target_features
from .sites import load_sites

DEM_URL = "https://planetarymaps.usgs.gov/mosaic/Lunar_LRO_LOLA_Global_LDEM_118m_Mar2014.tif"


def download() -> None:
    raise NotImplementedError  # Diviner/LEND: ver data/ode.py para localizar los productos


def build_features(include_unverified: bool = False, half_km: float = 25.0) -> pd.DataFrame:
    """DataFrame del contrato (body='moon', con columna `site`). Por ahora solo topo__*.

    Sitios: candidatos a base + aterrizajes históricos con coordenadas verificadas (data/sites.py).
    """
    return build_target_features("moon", DEM_URL, load_sites(include_unverified), half_km)


if __name__ == "__main__":
    FEATURES_DIR.mkdir(parents=True, exist_ok=True)
    out = build_features()
    out.to_parquet(FEATURES_DIR / "moon.parquet", index=False)
    print(out[["site", "topo__slope_mean_deg", "topo__rough_1km_m", "elev_mean_m", "valid_frac"]].round(2))
