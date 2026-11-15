"""Datos de la Luna (responsable: persona 3).

Topografía: LRO LOLA LDEM_256 (118 m) del NASA PDS, leído por filas con HTTP Range (ver pds_dem.py).
thermal__*, ice__* y geo__*: productos del NASA PDS, ver planetary.py y docs/FUENTES.md.

    python -m analogos.data.moon       # escribe data/features/moon.parquet
"""
import pandas as pd

from ..config import FEATURES_DIR
from .dem import build_target_features
from .planetary import add_properties
from .pds_dem import lola_dem
from .sites import load_sites

# Antes: mosaico del USGS. Ahora: los mismos datos desde el NASA PDS (regla: solo fuentes NASA).
DEM = lola_dem


def download() -> None:
    raise NotImplementedError  # Diviner/LEND: ver data/ode.py para localizar los productos


def build_features(include_unverified: bool = False, half_km: float = 25.0, only: list[str] | None = None) -> pd.DataFrame:
    """DataFrame del contrato (body='moon', con columna `site`): topo__* + thermal__*, ice__*, geo__* (planetary.py).

    Sitios: candidatos a base + aterrizajes históricos con coordenadas verificadas (data/sites.py).
    `only`: calcula solo esos sitios (por nombre). Útil para actualizar unos pocos sin recalcular los polares, que
    obligan a bajar ~600 MB de Diviner.
    """
    sites = load_sites(include_unverified)
    if only is not None:
        missing = set(only) - set(sites["site"])
        if missing:
            raise ValueError(f"sitios desconocidos (revisa docs/aterrizajes_conocidos.csv y el filtro de duplicados): {sorted(missing)}")
        sites = sites[sites["site"].isin(only)]
    df = build_target_features("moon", DEM(), sites, half_km)
    return add_properties(df, "moon")


def merge_site_rows(existing: pd.DataFrame, new: pd.DataFrame) -> pd.DataFrame:
    """Sustituye en `existing` las filas de los sitios que están en `new` y añade las que faltan (clave: `site`)."""
    return pd.concat([existing[~existing["site"].isin(new["site"])], new], ignore_index=True)


def update_sites(names: list[str]) -> pd.DataFrame:
    """Recalcula solo `names` y los fusiona en data/features/moon.parquet (y moon.csv). Devuelve la tabla completa."""
    path = FEATURES_DIR / "moon.parquet"
    out = merge_site_rows(pd.read_parquet(path), build_features(only=names))
    out.to_parquet(path, index=False)
    out.to_csv(FEATURES_DIR / "moon.csv", index=False)
    return out


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--only", nargs="+", help="actualizar solo estos sitios (nombres entre comillas) en vez de recalcular todo")
    a = ap.parse_args()
    FEATURES_DIR.mkdir(parents=True, exist_ok=True)
    if a.only:
        out = update_sites(a.only)
    else:
        out = build_features()
        out.to_parquet(FEATURES_DIR / "moon.parquet", index=False)
    cols = ["site", "topo__slope_mean_deg", "thermal__t_max_k", "thermal__t_range_k", "ice__water_frac",
            "geo__basalt_frac"]
    print(out[cols].round(3).to_string())
