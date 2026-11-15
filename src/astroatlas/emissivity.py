"""Experiment: MODIS emissivity index to better measure Earth's basalt (docs/preregistrations/emissivity.md).

Phase 1 (feasibility, one month of MOD11C3): index C = E29 - (E31 + E32)/2 in ±25 km windows, evaluated at 20 places of known
lithology with three gates fixed in advance (coverage, discrimination, small fields). If any fails, it stops.

    python -m astroatlas.emissivity --phase1
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

BASALT = {"Harrat Rahat": (23.5, 39.8), "Harrat Khaybar": (25.6, 39.9), "Harrat Uwayrid": (26.1, 37.8), "Deccan": (19.0, 74.5),
          "Karoo/Lesoto": (-29.5, 28.5), "Paraná": (-25.0, -52.0), "Columbia River": (46.0, -119.5), "Ethiopian plateau": (10.0, 38.0),
          "Hekla": (64.0, -19.7), "Jebel Marra": (12.9, 24.3)}
NON_BASALT = {"Rub al Khali": (21.0, 51.0), "Great Sand Sea": (27.0, 25.0), "Namib sand sea": (-24.8, 15.3),
              "Taklamakan": (38.9, 83.4), "Simpson Desert": (-25.5, 137.0), "Nebraska Sand Hills": (42.0, -101.5),
              "escudo canadiense": (52.0, -88.0), "Alpes": (46.5, 9.0), "Amazonia": (-3.0, -60.0), "Kalahari": (-23.0, 22.0)}


def litho_sites() -> pd.DataFrame:
    rows = [(n, la, lo, 1) for n, (la, lo) in BASALT.items()] + [(n, la, lo, 0) for n, (la, lo) in NON_BASALT.items()]
    return pd.DataFrame(rows, columns=["name", "lat", "lon", "basalt"])


def contrast_index(e29, e31, e32) -> np.ndarray:
    """C = E29 - (E31 + E32)/2. Higher C = more mafic (quartz lowers E29)."""
    return np.asarray(e29, float) - (np.asarray(e31, float) + np.asarray(e32, float)) / 2.0


def read_emissivity(path) -> np.ndarray:
    """Index C (3600 x 7200) with NaN where any band is missing. Closes the file (on Windows otherwise it cannot be deleted)."""
    from pyhdf.SD import SD, SDC

    sd = SD(str(path), SDC.READ)
    try:
        names = list(sd.datasets())
        missing = [b for b in BANDS if b not in names]
        if missing:
            raise KeyError(f"faltan bandas {missing}; there are {[n for n in names if 'mis' in n]}")
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
        raise RuntimeError("the requested MOD11C3 month was not found")
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
    return {"site_coverage": cov_sites, "cell_coverage": cov_cells, "auc": auc, "median_non_basalt": med,
            "small_total": len(small), "small_above_median": small_hits,
            "puerta1": cov_sites >= COV_SITES and cov_cells >= COV_CELLS, "puerta2": bool(auc >= AUC_MIN),
            "puerta3": small_hits >= SMALL_MIN}


def phase1() -> None:
    litho = litho_sites()
    earth = pd.read_parquet(FEATURES_DIR / "earth.parquet")
    ext = pd.concat([pd.read_csv(DOCS / "catalog/known_analogs.csv"), pd.read_csv(DOCS / "catalog/extended_analogs.csv")], ignore_index=True)
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
    litho.round(4).to_csv(RESULTS_DIR / "emis_lithology.csv", index=False)
    small.round(4).to_csv(RESULTS_DIR / "emis_small.csv", index=False)
    pd.set_option("display.width", 200)
    print(litho.round(4).to_string(index=False))
    print("\nSmall fields that GLiM underestimates:")
    print(small.round(4).to_string(index=False))
    print("\nPuertas:", {k: (round(v, 3) if isinstance(v, float) else v) for k, v in res.items()})
    pd.DataFrame([res]).to_csv(RESULTS_DIR / "emis_gates.csv", index=False)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase1", action="store_true")
    a = ap.parse_args()
    if a.phase1:
        phase1()
    else:
        ap.error("only --phase1 exists for now; Phase 2 is implemented only if Phase 1 passes")


if __name__ == "__main__":
    main()
