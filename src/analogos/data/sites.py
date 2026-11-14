"""Sitios objetivo de la Luna y Marte: sitios base candidatos + aterrizajes históricos.

Fuentes (ver docs/FUENTES.md):
  - docs/sitios_objetivo.csv        -> kind="target_base"    (candidatos a base: Shackleton, Jezero...)
  - docs/aterrizajes_conocidos.csv  -> kind="landing"        (misiones aterrizadas)
                                       kind="candidate_site" (candidatos de MSL: Eberswalde, Holden...)

Por defecto solo entran filas con coordenadas VERIFICADAS. Se excluyen siempre las filas sin
coordenadas y los centros de elipse de aterrizaje (no son el punto real).
"""
import numpy as np
import pandas as pd

from ..config import LANDINGS_CSV, SITES_CSV
from ..validate import haversine_km

COLUMNS = ["site", "body", "lat", "lon", "kind", "source"]


def _dedupe(df: pd.DataFrame, min_km: float) -> pd.DataFrame:
    """Dentro de cada cuerpo, descarta los sitios a menos de `min_km` de otro ya aceptado
    (el orden manda: los sitios base van primero)."""
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
                         "lon": base["lon"] % 360, "kind": "target_base", "source": "sitios_objetivo.csv"})

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
        "source": "aterrizajes_conocidos.csv"})

    out = pd.concat([base, land], ignore_index=True)[COLUMNS]
    return _dedupe(out, dedupe_km).reset_index(drop=True)
