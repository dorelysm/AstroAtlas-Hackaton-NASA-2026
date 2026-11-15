"""Datos de Marte (responsable: persona 4).

Topografía: MGS MOLA MEGDR 128 px/° (463 m) del NASA PDS, leído por filas con HTTP Range (ver pds_dem.py).
thermal__*, ice__* y geo__*: productos del NASA PDS, ver planetary.py y docs/FUENTES.md.

    python -m analogos.data.mars       # escribe data/features/mars.parquet
"""
import pandas as pd

from ..config import FEATURES_DIR
from .dem import build_target_features
from .planetary import add_properties
from .pds_dem import mola_dem
from .sites import load_sites

# Antes: mosaico del USGS. Ahora: los mismos datos desde el NASA PDS (regla: solo fuentes NASA).
DEM = mola_dem


def download() -> None:
    raise NotImplementedError  # TES/THEMIS/SHARAD: ver data/ode.py para localizar los productos


def build_features(include_unverified: bool = False, half_km: float = 25.0) -> pd.DataFrame:
    """DataFrame del contrato (body='mars', con columna `site`): topo__* + thermal__*, ice__*, geo__* (planetary.py).

    Sitios: candidatos a base + aterrizajes históricos con coordenadas verificadas (data/sites.py).
    """
    df = build_target_features("mars", DEM(), load_sites(include_unverified), half_km)
    return add_properties(df, "mars")


if __name__ == "__main__":
    FEATURES_DIR.mkdir(parents=True, exist_ok=True)
    out = build_features()
    out.to_parquet(FEATURES_DIR / "mars.parquet", index=False)
    cols = ["site", "topo__slope_mean_deg", "thermal__t_max_k", "thermal__t_range_k", "ice__water_frac",
            "geo__basalt_frac"]
    print(out[cols].round(3).to_string())
