"""Viabilidad por cercanía a centros poblados (solo Tierra).

Fuente (NASA SEDAC): Global Rural-Urban Mapping Project, Version 1 (GRUMPv1): Settlement Points, Revision 01.
  Center for International Earth Science Information Network (CIESIN), Columbia University, et al. 2017.
  NASA Socioeconomic Data and Applications Center (SEDAC). https://doi.org/10.7927/H4BC3WG1
  70 629 asentamientos con latitud, longitud y población; archivo CSV de 2.8 MB (zip), bajado con el login de Earthdata.

Regla decidida por el equipo (14 nov 2026): un punto es INVIABLE si hay un asentamiento de >= 1 000 habitantes a menos de 50 km.
Es una MARCA (columna `viable`), no parte del score: no cambia el ranking ni la validación con análogos conocidos.

LIMITACIONES (de la documentación de SEDAC y comprobadas con los datos):
  - Lista "mejor disponible" NO exhaustiva: la probabilidad de que un asentamiento esté incluido crece con su población, así que
    los pueblos de 1 000 a 10 000 habitantes están peor cubiertos. Ejemplo comprobado: San Pedro de Atacama no aparece.
  - Datos de 1990 a 2010; las poblaciones y los asentamientos han cambiado.
  - Latitudes de -54.8° a 78.9°: no hay estaciones antárticas ni asentamientos árticos extremos.
  - 1 629 puntos no tienen población (-999). No cuentan para `viable`; sí para `dist_any_settlement_km` (aviso).
  "viable" significa "ningún asentamiento de >= 1 000 habitantes conocido en esta lista a menos de 50 km", no "deshabitado".

    python -m analogos.data.settlements        # añade las columnas a earth.parquet, earth_sites.parquet y earth_usgs.parquet
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
    """Ruta del CSV de GRUMP; lo descarga (2.8 MB) y lo extrae con comprobación de rutas si falta."""
    csv = directory / GRUMP_CSV
    if not csv.exists():
        earthaccess = edl.login()
        res = earthaccess.search_data(short_name="CIESIN_SEDAC_GRUMPv1_STLMNT01", version="1.01")
        granule = [g for g in res if "csv" in g["meta"]["native-id"].lower()]
        if len(granule) != 1:
            raise RuntimeError("no encuentro el gránulo CSV de GRUMP en el catálogo de la NASA")
        zip_path = Path(str(earthaccess.download(granule, str(directory.parent))[0]))
        safe_extract(zip_path, directory)
    return csv


def load_settlements(path: Path | None = None) -> pd.DataFrame:
    """Asentamientos con `pop`: ES00POP (año 2000) si existe, si no `Pop` del año disponible; NaN si se desconoce (-999)."""
    # El CSV es UTF-8 con algún byte inválido, y en 493 nombres el espacio viene como "ÿ" (artefacto de la fuente).
    # Los nombres solo sirven para mostrar; las distancias no dependen de ellos.
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
    """(distancia en km sobre la esfera, índice) al punto más cercano. Árbol en 3D: no falla en el antimeridiano ni en los polos."""
    chord, idx = tree.query(_xyz(lat, lon), k=1)
    return 2 * EARTH_R_KM * np.arcsin(np.clip(chord / 2, 0, 1)), idx


def add_viability(df: pd.DataFrame, settlements: pd.DataFrame | None = None, min_pop: float = MIN_POP,
                  radius_km: float = RADIUS_KM) -> pd.DataFrame:
    """Añade `dist_settlement_km` (al más cercano con >= min_pop habitantes), su nombre, país y población,
    `dist_any_settlement_km` (al más cercano de cualquier tipo, también sin población) y `viable` (distancia >= radius_km)."""
    s = load_settlements() if settlements is None else settlements
    big = s[s["pop"] >= min_pop].reset_index(drop=True)
    if big.empty:
        raise ValueError(f"ningún asentamiento con >= {min_pop} habitantes")
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
    print(f"{len(s)} asentamientos; con >= {MIN_POP} habitantes: {int((s['pop'] >= MIN_POP).sum())}; sin población: {int(s['pop'].isna().sum())}")
    for name in ("earth.parquet", "earth_sites.parquet", "earth_usgs.parquet"):
        p = FEATURES_WRITE_DIR / name
        if not p.exists():
            continue
        d = add_viability(pd.read_parquet(p), s)
        d.to_parquet(p, index=False)
        print(f"{name}: {len(d)} filas | viables (>= {RADIUS_KM:.0f} km de un asentamiento de >= {MIN_POP} hab.): "
              f"{int(d['viable'].sum())} ({d['viable'].mean():.0%})")


if __name__ == "__main__":
    main()
