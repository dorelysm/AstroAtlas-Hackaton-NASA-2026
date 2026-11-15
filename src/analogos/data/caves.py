"""Cuevas y tubos de lava como CONTEXTO (no es una dimensión del modelo).

Fuentes abiertas (CC BY 4.0):
  - Luna: "Current Evidence of Lunar Lava Tubes and Associated Surface Features" (Losarcos y Dombard, Zenodo 10.5281/zenodo.20516852,
    jun 2026), capa `Pit-locations` = 278 pits y claraboyas de la base de datos de LROC QuickMap (Wagner y Robinson).
  - Tierra: Pyroduct Digital Catalog v1 (Romio y Lobosco 2024, Zenodo 10.5281/zenodo.14535886): 94 tubos de lava documentados
    en 8 países. El catálogo trae SOLO región y nombre, NO coordenadas; por eso no se puede marcar celda por celda en la Tierra.
  - Marte: Mars Global Cave Candidate Catalog (USGS, Cushing; PDS release 2019): 1 062 candidatas con coordenadas, tipo y prioridad.
    El servidor del USGS bloquea la descarga automática, así que la descargó una persona del equipo en data/raw/mgc3/. Ojo: la cabecera
    del CSV está desordenada; el orden real de las columnas es el del XML (ID_Tag, Longitude, Latitude, Type_Code, Priority, ...).

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
    """Candidatas a entrada de cueva de Marte. Se ignora la cabecera del CSV (desordenada) y se usa el orden del XML."""
    d = pd.read_csv(path, header=None, skiprows=1, names=["name", "lon", "lat", "type", "priority", "diam_m", "depth_m", "comment"])
    return d.dropna(subset=["lat", "lon"]).reset_index(drop=True)


def add_pit_context(df: pd.DataFrame, pits: pd.DataFrame, radius_km: float = 50.0, columns: list[str] | None = None) -> pd.DataFrame:
    """Nº de elementos a menos de `radius_km`, distancia al más cercano y su nombre. Longitudes 0-360 este (igual que moon/mars.parquet).
    `columns` = nombres de las 3 columnas de salida (por defecto las de pits lunares)."""
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
    print(f"{len(pits)} pits; por terreno: {pits['terrain'].value_counts().to_dict()}")
    p = FEATURES_WRITE_DIR / "moon.parquet"
    d = add_pit_context(pd.read_parquet(p), pits)
    d.to_parquet(p, index=False)
    near = d[d["pits_within_50km"] > 0]
    print(f"moon.parquet: {len(near)} de {len(d)} objetivos con algún pit a < 50 km")
    print(near[["site", "lat", "lon", "pits_within_50km", "nearest_pit_km", "nearest_pit_name"]].round(1).to_string(index=False))
    d[["site", "lat", "lon", *COLUMNS]].round(2).to_csv(FEATURES_WRITE_DIR / "moon_pits_context.csv", index=False)

    if MARS_CSV.exists():
        caves = load_mars_caves()
        print(f"\n{len(caves)} candidatas a cueva en Marte; por tipo: {caves['type'].value_counts().to_dict()}")
        p = FEATURES_WRITE_DIR / "mars.parquet"
        m = add_pit_context(pd.read_parquet(p), caves, columns=MARS_COLUMNS)
        m.to_parquet(p, index=False)
        near = m.sort_values("nearest_cave_km")
        print(f"mars.parquet: {int((m['caves_within_50km'] > 0).sum())} de {len(m)} objetivos con alguna candidata a < 50 km")
        print(near[["site", "lat", "lon", *MARS_COLUMNS]].round(1).to_string(index=False))
        m[["site", "lat", "lon", *MARS_COLUMNS]].round(2).to_csv(FEATURES_WRITE_DIR / "mars_caves_context.csv", index=False)
    else:
        print("\nSin catálogo de Marte (data/raw/mgc3/): falta descargarlo a mano del USGS.")


if __name__ == "__main__":
    main()
