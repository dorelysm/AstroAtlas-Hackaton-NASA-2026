"""Experimento: índice de emisividad MODIS para medir mejor el basalto de la Tierra (docs/PREREGISTRO_EMISIVIDAD.md).

Fase 1 (viabilidad, un mes de MOD11C3): índice C = E29 - (E31 + E32)/2 en ventanas de ±25 km, evaluado en 20 lugares de litología
conocida con tres puertas fijadas de antemano (cobertura, discriminación, campos pequeños). Si alguna falla, se detiene.

    python -m analogos.emissivity --phase1
"""
import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

from .config import DOCS, FEATURES_DIR, RAW_DIR, RESULTS_DIR
from .data import edl
from .data.earth_water import cell_windows, snow_grid, window_means

MONTH = ("2019-07-01", "2019-07-31")
SHORT = "MOD11C3"
BANDS = ("Emis_29", "Emis_31", "Emis_32")
SCALE, OFFSET = 0.002, 0.49
COV_SITES, COV_CELLS, AUC_MIN, SMALL_MIN = 0.90, 0.80, 0.80, 2

BASALT = {"Harrat Rahat": (23.5, 39.8), "Harrat Khaybar": (25.6, 39.9), "Harrat Uwayrid": (26.1, 37.8), "Decán": (19.0, 74.5),
          "Karoo/Lesoto": (-29.5, 28.5), "Paraná": (-25.0, -52.0), "río Columbia": (46.0, -119.5), "meseta etíope": (10.0, 38.0),
          "Hekla": (64.0, -19.7), "Jebel Marra": (12.9, 24.3)}
NON_BASALT = {"Rub al Khali": (21.0, 51.0), "Gran Mar de Arena": (27.0, 25.0), "arenal del Namib": (-24.8, 15.3),
              "Taklamakán": (38.9, 83.4), "desierto de Simpson": (-25.5, 137.0), "Sand Hills de Nebraska": (42.0, -101.5),
              "escudo canadiense": (52.0, -88.0), "Alpes": (46.5, 9.0), "Amazonia": (-3.0, -60.0), "Kalahari": (-23.0, 22.0)}


def litho_sites() -> pd.DataFrame:
    rows = [(n, la, lo, 1) for n, (la, lo) in BASALT.items()] + [(n, la, lo, 0) for n, (la, lo) in NON_BASALT.items()]
    return pd.DataFrame(rows, columns=["name", "lat", "lon", "basalt"])


def contrast_index(e29, e31, e32) -> np.ndarray:
    """C = E29 - (E31 + E32)/2. Mayor C = más máfico (el cuarzo baja E29)."""
    return np.asarray(e29, float) - (np.asarray(e31, float) + np.asarray(e32, float)) / 2.0


def read_emissivity(path) -> np.ndarray:
    """Índice C (3600 x 7200) con NaN donde falta alguna banda. Cierra el archivo (en Windows si no, no se puede borrar)."""
    from pyhdf.SD import SD, SDC

    sd = SD(str(path), SDC.READ)
    try:
        names = list(sd.datasets())
        missing = [b for b in BANDS if b not in names]
        if missing:
            raise KeyError(f"faltan bandas {missing}; hay {[n for n in names if 'mis' in n]}")
        e = []
        for b in BANDS:
            dn = sd.select(b).get().astype("float64")
            e.append(np.where(dn > 0, dn * SCALE + OFFSET, np.nan))
    finally:
        sd.end()
    return contrast_index(*e)


def download_month(directory: Path) -> Path:
    earthaccess = edl.login()
    res = earthaccess.search_data(short_name=SHORT, temporal=MONTH, count=2)
    if not res:
        raise RuntimeError("no se encontró el mes pedido de MOD11C3")
    directory.mkdir(parents=True, exist_ok=True)
    return Path(str(earthaccess.download(res[:1], str(directory))[0]))


def reduce_cells(c_grid: np.ndarray, cells: pd.DataFrame) -> np.ndarray:
    lats, lons = snow_grid()
    return window_means(c_grid, cell_windows(cells, lats, lons))


def gates(litho: pd.DataFrame, cell_values: np.ndarray, small: pd.DataFrame) -> dict:
    ok = litho["c"].notna()
    cov_sites = float(ok.mean())
    cov_cells = float(np.isfinite(cell_values).mean())
    auc = float(roc_auc_score(litho.loc[ok, "basalt"], litho.loc[ok, "c"])) if ok.sum() > 3 and litho.loc[ok, "basalt"].nunique() == 2 else float("nan")
    med = float(litho.loc[ok & (litho["basalt"] == 0), "c"].median())
    small_hits = int((small["c"] > med).sum())
    return {"cobertura_sitios": cov_sites, "cobertura_celdas": cov_cells, "auc": auc, "mediana_no_basalto": med,
            "pequenos_total": len(small), "pequenos_sobre_mediana": small_hits,
            "puerta1": cov_sites >= COV_SITES and cov_cells >= COV_CELLS, "puerta2": bool(auc >= AUC_MIN),
            "puerta3": small_hits >= SMALL_MIN}


def phase1() -> None:
    litho = litho_sites()
    earth = pd.read_parquet(FEATURES_DIR / "earth.parquet")
    ext = pd.concat([pd.read_csv(DOCS / "analogos_conocidos.csv"), pd.read_csv(DOCS / "analogos_ampliado.csv")], ignore_index=True)
    small_names = ["Pinacate (Mexico)", "Etna (Italia)", "Lanzarote"]
    small = ext[ext["name"].isin(small_names)][["name", "lat", "lon"]].reset_index(drop=True)
    tmp = RAW_DIR / "modis_emis"
    path = download_month(tmp)
    try:
        grid = read_emissivity(path)
        litho["c"] = reduce_cells(grid, litho)
        small["c"] = reduce_cells(grid, small)
        cell_values = reduce_cells(grid, earth)
    finally:
        path.unlink(missing_ok=True)
    res = gates(litho, cell_values, small)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    litho.round(4).to_csv(RESULTS_DIR / "emis_litologia.csv", index=False)
    small.round(4).to_csv(RESULTS_DIR / "emis_pequenos.csv", index=False)
    pd.set_option("display.width", 200)
    print(litho.round(4).to_string(index=False))
    print("\nCampos pequeños que GLiM subestima:")
    print(small.round(4).to_string(index=False))
    print("\nPuertas:", {k: (round(v, 3) if isinstance(v, float) else v) for k, v in res.items()})
    pd.DataFrame([res]).to_csv(RESULTS_DIR / "emis_puertas.csv", index=False)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase1", action="store_true")
    a = ap.parse_args()
    if a.phase1:
        phase1()
    else:
        ap.error("de momento solo existe --phase1; la Fase 2 solo se implementa si la Fase 1 pasa")


if __name__ == "__main__":
    main()
