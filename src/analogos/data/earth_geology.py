"""Geología de la Tierra (dimensión `geo`) con el mapa litológico global GLiM en rejilla de 0.5°.

EXCEPCIÓN A LA REGLA "SOLO DATOS NASA" (aprobada por el equipo el 14 nov 2026): GLiM no es de la NASA.
  Hartmann, J. & Moosdorf, N. (2012). Global Lithological Map Database v1.0 (gridded to 0.5° spatial
  resolution). PANGAEA, https://doi.org/10.1594/PANGAEA.788537  (licencia CC-BY 3.0; 38 kB).
  Paper: Geochemistry, Geophysics, Geosystems 13, Q12004, https://doi.org/10.1029/2012GC004370
  Descarga: https://epic.awi.de/id/eprint/31092/1/hartmann-moosdorf_2012.zip

Formato: ESRI ASCII (720 x 360, 0.5°), UNA clase litológica DOMINANTE por celda (no fracciones). Códigos de
`Classnames.txt`: su sedimentos no consolidados, vb volcánicas BÁSICAS, ss silicoclásticas, pb plutónicas
básicas, sm sedimentarias mixtas, sc carbonatadas, va volcánicas ácidas, mt metamórficas, pa plutónicas ácidas,
vi volcánicas intermedias, wb agua, py piroclastos, pi plutónicas intermedias, ev evaporitas, nd sin dato, ig hielo.
(Los significados salen del paper; el archivo solo trae los códigos.)

`geo__basalt_frac` = fracción de las celdas de roca de la ventana cuya clase dominante es `vb`.
Como cada celda es de ~55 km, la ventana es de 75 km de radio (unas 3 x 3 celdas), MAYOR que los 25 km que usa el
resto de variables: con 25 km saldría 0 o 1 según una sola celda. Ver docs/FUENTES.md para las limitaciones.

    python -m analogos.data.earth_geology
"""
import argparse
import urllib.request
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

from ..config import FEATURES_WRITE_DIR, RAW_DIR
from .earth_water import window_indices

GLIM_URL = "https://epic.awi.de/id/eprint/31092/1/hartmann-moosdorf_2012.zip"
GLIM_DIR = RAW_DIR / "glim"
GRID_NAME, CLASSES_NAME = "glim_wgs84_0point5deg.txt.asc", "Classnames.txt"
HALF_KM = 75.0
NODATA = -9999
NOT_ROCK = {"wb", "ig", "nd"}  # agua, hielo, sin dato: no cuentan como roca
BASALT = {"vb"}  # volcánicas básicas
MAFIC = {"vb", "pb"}  # + plutónicas básicas (gabro), solo diagnóstico


def safe_extract(zip_path: Path, out_dir: Path) -> None:
    """Extrae un zip descargado rechazando rutas absolutas o con `..` (zip slip)."""
    out_dir.mkdir(parents=True, exist_ok=True)
    root = out_dir.resolve()
    with zipfile.ZipFile(zip_path) as z:
        for info in z.infolist():
            if not (out_dir / info.filename).resolve().is_relative_to(root):
                raise ValueError(f"entrada sospechosa en el zip: {info.filename}")
        z.extractall(out_dir)


def ensure_glim(directory: Path = GLIM_DIR) -> Path:
    """Devuelve la carpeta con los archivos de GLiM, descargándolos (38 kB) si faltan."""
    extracted = directory / "extracted"
    if not (extracted / GRID_NAME).exists():
        directory.mkdir(parents=True, exist_ok=True)
        zip_path = directory / "hartmann-moosdorf_2012.zip"
        urllib.request.urlretrieve(GLIM_URL, zip_path)
        safe_extract(zip_path, extracted)
    return extracted


def load_glim(directory: Path | None = None) -> tuple[np.ndarray, dict[int, str], np.ndarray, np.ndarray]:
    """(rejilla de códigos, {código: clase}, latitudes de centro, longitudes de centro)."""
    d = directory or ensure_glim()
    names_df = pd.read_csv(d / CLASSES_NAME, sep=";")
    names = {int(v): str(x) for v, x in zip(names_df["Value_"], names_df["xx"])}
    header = dict(line.split() for line in (d / GRID_NAME).read_text(encoding="latin-1").splitlines()[:6])
    n_rows, n_cols, size = int(header["nrows"]), int(header["ncols"]), float(header["cellsize"])
    grid = np.loadtxt(d / GRID_NAME, skiprows=6, dtype=int)
    if grid.shape != (n_rows, n_cols):
        raise ValueError(f"rejilla {grid.shape} no coincide con la cabecera ({n_rows}, {n_cols})")
    lats = float(header["yllcorner"]) + size * (n_rows - np.arange(n_rows) - 0.5)  # fila 0 = norte
    lons = float(header["xllcorner"]) + size * (np.arange(n_cols) + 0.5)
    return grid, names, lats, lons


def class_masks(grid: np.ndarray, names: dict[int, str]) -> dict[str, np.ndarray]:
    code = {v: k for k, v in names.items()}
    in_set = lambda s: np.isin(grid, [code[c] for c in s if c in code])  # noqa: E731
    rock = (grid != NODATA) & ~in_set(NOT_ROCK)
    return {"rock": rock, "basalt": in_set(BASALT) & rock, "mafic": in_set(MAFIC) & rock}


def geology_features(cells: pd.DataFrame, grid, names, lats, lons, half_km: float = HALF_KM) -> pd.DataFrame:
    """Por celda: fracción de roca basáltica / máfica en la ventana, clase dominante y nº de celdas de roca."""
    m = class_masks(grid, names)
    out = {"geo__basalt_frac": [], "geo_glim_mafic_frac": [], "geo_glim_class": [], "geo_glim_rock_cells": []}
    for r in cells.itertuples():
        ii, jj = window_indices(lats, lons, r.lat, r.lon, half_km)
        rock = m["rock"][ii, jj]
        n = int(rock.sum())
        out["geo_glim_rock_cells"].append(n)
        if n == 0:  # hielo, agua o sin dato: NaN, no 0
            out["geo__basalt_frac"].append(np.nan)
            out["geo_glim_mafic_frac"].append(np.nan)
            out["geo_glim_class"].append(None)
            continue
        out["geo__basalt_frac"].append(float(m["basalt"][ii, jj].sum() / n))
        out["geo_glim_mafic_frac"].append(float(m["mafic"][ii, jj].sum() / n))
        vals, counts = np.unique(grid[ii, jj][rock], return_counts=True)
        out["geo_glim_class"].append(names.get(int(vals[np.argmax(counts)])))
    return pd.DataFrame(out, index=cells.index)


def apply_to_earth(earth: pd.DataFrame, geo: pd.DataFrame) -> pd.DataFrame:
    e = earth.copy()
    for col in geo.columns:
        e[col] = geo[col]
    return e


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--half-km", type=float, default=HALF_KM)
    a = ap.parse_args()
    grid, names, lats, lons = load_glim()
    for name in ("earth.parquet", "earth_sites.parquet"):
        p = FEATURES_WRITE_DIR / name
        if p.exists():
            t = pd.read_parquet(p)
            apply_to_earth(t, geology_features(t, grid, names, lats, lons, a.half_km)).to_parquet(p, index=False)
            g = pd.read_parquet(p)
            print(f"{name}: {len(g)} filas | geo__basalt_frac con dato: {int(g.geo__basalt_frac.notna().sum())} | "
                  f"con basalto (> 0): {int((g.geo__basalt_frac > 0).sum())}")


if __name__ == "__main__":
    main()
