"""Cuevas y tubos de lava como CONTEXTO (no es una dimensión del modelo).

Fuentes abiertas (CC BY 4.0):
  - Luna: "Current Evidence of Lunar Lava Tubes and Associated Surface Features" (Losarcos y Dombard, Zenodo 10.5281/zenodo.20516852,
    jun 2026), capa `Pit-locations` = 278 pits y claraboyas de la base de datos de LROC QuickMap (Wagner y Robinson).
  - Tierra: Pyroduct Digital Catalog v1 (Romio y Lobosco 2024, Zenodo 10.5281/zenodo.14535886): 94 tubos de lava documentados
    en 8 países. El catálogo trae SOLO región y nombre, NO coordenadas; por eso no se puede marcar celda por celda en la Tierra.
  - Marte: Mars Global Cave Candidate Catalog (USGS, Cushing 2017-2019): el servidor del USGS bloquea la descarga automática, hay que
    bajarlo a mano (ver docs/DIMENSIONES_NO_MODELADAS.md). Sin él, no hay columna de Marte.

Por qué es solo contexto: en la Tierra no hay coordenadas de los tubos, y en la Luna y Marte "hay un pit cerca" depende de que haya
sido detectado en imágenes. Una celda terrestre sin tubos documentados no es una celda sin tubos.

    python -m analogos.data.caves            # añade columnas de pits a moon.parquet
"""
from pathlib import Path

import numpy as np
import pandas as pd

from ..config import FEATURES_WRITE_DIR, RAW_DIR
from ..validate import haversine_km

CAVES_DIR = RAW_DIR / "caves"
PITS_SHP = CAVES_DIR / "pits" / "x" / "pit-locations.shp"
COLUMNS = ["pits_within_50km", "nearest_pit_km", "nearest_pit_name"]


def load_pits(path: Path = PITS_SHP) -> pd.DataFrame:
    import shapefile

    r = shapefile.Reader(str(path), encoding="utf-8", encodingErrors="replace")
    names = [f[0] for f in r.fields[1:]]
    rows = [dict(zip(names, rec)) for rec in r.records()]
    d = pd.DataFrame(rows)[["Name", "Terrain", "HostFeatur", "Latitude", "Longitude", "Depth"]]
    d.columns = ["name", "terrain", "host", "lat", "lon", "depth_m"]
    d["depth_m"] = pd.to_numeric(d["depth_m"], errors="coerce")
    return d.dropna(subset=["lat", "lon"]).reset_index(drop=True)


def add_pit_context(df: pd.DataFrame, pits: pd.DataFrame, radius_km: float = 50.0) -> pd.DataFrame:
    """Nº de pits a menos de `radius_km`, distancia al más cercano y su nombre. Longitudes 0-360 este (igual que moon.parquet)."""
    out = df.drop(columns=[c for c in COLUMNS if c in df.columns]).copy()
    d = haversine_km(out["lat"].to_numpy()[:, None], out["lon"].to_numpy()[:, None],
                     pits["lat"].to_numpy()[None, :], pits["lon"].to_numpy()[None, :])
    out["pits_within_50km"] = (d < radius_km).sum(axis=1)
    j = d.argmin(axis=1)
    out["nearest_pit_km"] = d[np.arange(len(out)), j]
    out["nearest_pit_name"] = pits["name"].to_numpy()[j]
    return out


def main() -> None:
    pits = load_pits()
    print(f"{len(pits)} pits; por terreno: {pits['terrain'].value_counts().to_dict()}")
    p = FEATURES_WRITE_DIR / "moon.parquet"
    d = add_pit_context(pd.read_parquet(p), pits)
    d.to_parquet(p, index=False)
    near = d[d["pits_within_50km"] > 0]
    print(f"moon.parquet: {len(near)} de {len(d)} objetivos con algún pit a < 50 km")
    print(near[["site", "lat", "lon", "pits_within_50km", "nearest_pit_km", "nearest_pit_name"]].round(1).to_string(index=False))
    d[["site", "lat", "lon", *COLUMNS]].round(2).to_csv(FEATURES_WRITE_DIR / "moon_pits_context.csv", index=False)


if __name__ == "__main__":
    main()
