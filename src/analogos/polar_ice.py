"""Índice de hidrógeno relativo de Marte con neutrones epitérmicos de Odyssey (docs/PREREGISTRO_HIELO_POLAR.md, Fase 1).

Fuente: NASA PDS, ODY-M-GRS-5-AND-V2.0 (tablas binarias de 5° x 5°, 11 columnas float32 big-endian; `CEPI` = tasa de conteo epitérmica).
Menos neutrones epitérmicos = más hidrógeno. Regla de estación para |lat| >= 40°: intervalos de Ls completos dentro de [105, 165] (norte) o
[285, 345] (sur). Índice H = -ln(CEPI / CEPI_ref), con CEPI_ref la mediana de las celdas con |lat| < 30°.

    python -m analogos.polar_ice           # descarga (≈ 33 MB, en caché), calcula y comprueba la puerta de validez
"""
import re
import time
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

from .config import FEATURES_DIR, FEATURES_WRITE_DIR, RAW_DIR
from .data import planetary

BASE = "https://pds-geosciences.wustl.edu/ody/ody-m-grs-5-and-v2/odgn2_xxxx"
CACHE = RAW_DIR / "ody_and"
COLS = ["lat", "lon", "ctherm", "ntherm", "stherm", "cepi", "nepi", "sepi", "cfast", "nfast", "sfast"]
SEASON = {"N": (105, 165), "S": (285, 345)}
HIGH_LAT = 40.0
REF_LAT = 30.0
GATE_RHO = 0.6
H_ICE = float(np.log(1.5))


def _get(url: str, tries: int = 5) -> bytes:
    """Descarga con reintentos (el servidor del PDS corta conexiones de vez en cuando); lo ya descargado queda en caché."""
    for k in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "analogos-research"}), timeout=60) as r:
                return r.read()
        except OSError:  # URLError, timeout, reset
            if k == tries - 1:
                raise
            time.sleep(3 * (k + 1))
    raise RuntimeError("inalcanzable")


def list_dirs(url: str, pattern: str) -> list[str]:
    html = _get(url + "/").decode("latin-1")
    return sorted(set(re.findall(pattern, html, flags=re.I)))


def file_list() -> list[tuple[str, int, int]]:
    """(ruta relativa del .dat, Ls inicial, Ls final) de todos los archivos del volumen."""
    out = []
    for yr in list_dirs(BASE, r"/(yr\d\d)/"):
        for sub in list_dirs(f"{BASE}/{yr}", rf"/({yr}_ls\d{{3}}_\d{{3}})/"):
            a, b = int(sub[-7:-4]), int(sub[-3:])
            nn = yr[2:]
            out.append((f"{yr}/{sub}/and_{nn}_{sub[-7:-4]}_{sub[-3:]}.dat", a, b))
    return out


def download(rel: str) -> Path:
    path = CACHE / Path(rel).name
    if not path.exists():
        CACHE.mkdir(parents=True, exist_ok=True)
        path.write_bytes(_get(f"{BASE}/{rel}"))
    return path


def read_table(path: Path) -> pd.DataFrame:
    a = np.fromfile(path, dtype=">f4")
    if a.size != 2592 * 11:
        raise ValueError(f"{path.name}: tamaño inesperado {a.size}")
    return pd.DataFrame(a.reshape(2592, 11).astype("float64"), columns=COLS)


def selected(lat: float, ls_a: int, ls_b: int) -> bool:
    """Regla de estación fijada de antemano."""
    if abs(lat) < HIGH_LAT:
        return True
    lo, hi = SEASON["N" if lat > 0 else "S"]
    return lo <= ls_a and ls_b <= hi


def cell_values(files: list[tuple[str, int, int]]) -> pd.DataFrame:
    """Mediana de CEPI por celda sobre los intervalos y años seleccionados (más cuántos se usaron)."""
    lat = lon = None
    stacks: list[np.ndarray] = []
    masks: list[np.ndarray] = []
    for rel, a, b in files:
        t = read_table(download(rel))
        if lat is None:
            lat, lon = t["lat"].to_numpy(), t["lon"].to_numpy()
        cepi = t["cepi"].to_numpy().copy()
        cepi[~np.isfinite(cepi) | (cepi <= 0)] = np.nan
        use = np.array([selected(la, a, b) for la in lat])
        stacks.append(np.where(use, cepi, np.nan))
    arr = np.vstack(stacks)
    with np.errstate(all="ignore"):
        med = np.nanmedian(arr, axis=0)
    return pd.DataFrame({"lat": lat, "lon": lon, "cepi": med, "n_obs": np.isfinite(arr).sum(axis=0)})


def hydrogen_index(cells: pd.DataFrame) -> pd.DataFrame:
    ref = float(cells.loc[cells["lat"].abs() < REF_LAT, "cepi"].median())
    out = cells.copy()
    out["H"] = -np.log(out["cepi"] / ref)
    out.attrs["cepi_ref"] = ref
    return out


def lookup(cells: pd.DataFrame, lat: float, lon_east: float) -> pd.Series:
    """Celda de 5° que contiene (lat, lon 0-360 este)."""
    la = 87.5 - 5.0 * np.floor((90.0 - lat) / 5.0)
    lo = 2.5 + 5.0 * np.floor((lon_east % 360.0) / 5.0)
    return cells.loc[(np.isclose(cells["lat"], la)) & (np.isclose(cells["lon"], lo))].iloc[0]


def existing_weh() -> pd.DataFrame:
    t = pd.read_fwf(planetary._download(planetary.ODY_URL + "h2o_sr_5x5.tab"), colspecs=[(0, 5), (15, 20), (28, 36), (45, 53)],
                    names=["lat", "lon", "weh", "sigma"], header=None).replace(9999.999, np.nan)
    t["lon"] = t["lon"] % 360.0
    return t


def validity(cells_h: pd.DataFrame) -> dict:
    w = existing_weh()
    m = cells_h.merge(w, on=["lat", "lon"], how="inner")
    m = m[(m["lat"].abs() < 42) & m["weh"].notna() & m["H"].notna()]
    rho = float(spearmanr(m["H"], m["weh"])[0])
    return {"n_celdas": len(m), "spearman": rho, "puerta": rho >= GATE_RHO}


def main() -> None:
    files = file_list()
    print(f"{len(files)} archivos en el volumen; descargando los que falten (≈ 114 kB cada uno)...", flush=True)
    cells = hydrogen_index(cell_values(files))
    ref = cells.attrs["cepi_ref"]
    v = validity(cells)
    print(f"CEPI de referencia (|lat| < 30°): {ref:.4f}; celdas con dato: {int(cells['cepi'].notna().sum())} de {len(cells)}")
    print(f"Puerta de validez: Spearman H frente al hidrógeno de h2o_sr_5x5 en {v['n_celdas']} celdas (|lat| < 42°): "
          f"rho = {v['spearman']:.3f} (mínimo {GATE_RHO}) -> {'PASA' if v['puerta'] else 'FALLA'}")
    mars = pd.read_parquet(FEATURES_DIR / "mars.parquet")[["site", "lat", "lon", "ice__water_frac"]]
    rows = []
    for r in mars.itertuples():
        c = lookup(cells, r.lat, r.lon)
        rows.append({"site": r.site, "lat": r.lat, "weh_existente": r.ice__water_frac, "cepi": c["cepi"], "H": c["H"],
                     "n_obs": int(c["n_obs"]), "rico_en_hielo": bool(c["H"] >= H_ICE) if np.isfinite(c["H"]) else None})
    t = pd.DataFrame(rows).sort_values("H", ascending=False)
    pd.set_option("display.width", 200)
    print(t.round(3).to_string(index=False))
    FEATURES_WRITE_DIR.mkdir(parents=True, exist_ok=True)
    cells.to_parquet(FEATURES_WRITE_DIR / "mars_hydrogen_cells.parquet", index=False)
    t.to_csv(FEATURES_WRITE_DIR / "mars_hydrogen_targets.csv", index=False)
    pd.DataFrame([{**v, "cepi_ref": ref, "H_ice": H_ICE}]).to_csv(FEATURES_WRITE_DIR / "mars_hydrogen_gate.csv", index=False)


if __name__ == "__main__":
    main()
