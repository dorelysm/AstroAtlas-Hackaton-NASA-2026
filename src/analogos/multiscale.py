"""Experimento B: topografía a varias escalas (docs/PREREGISTRO_MULTIESCALA.md).

Variante: H (pendiente de ln rugosidad frente a ln escala, L = 1, 2, 5 km), ln(rugosidad a 1 km) y ln(pendiente media + 0,1),
con PCA blanqueada (0,90 de varianza, máx. 3 componentes) ajustada con la Tierra. Solo cambia la topografía.

    python -m analogos.multiscale
"""
import numpy as np
import pandas as pd

from .config import FEATURES_DIR, RESULTS_DIR
from .features import load_features
from .similarity import fit_topo_model
from .validation_ext import extended_known, extended_sites
from .variants import evaluate, paired, profiles_with, usgs_stratified, verdict

SCALES_KM = np.array([1.0, 2.0, 5.0])
ROUGH = ["topo__rough_1km_m", "topo__rough_2km_m", "topo__rough_5km_m"]
MS_COLS = ["ms_hurst", "ms_lnr1", "ms_lnslope"]
FLOOR_M = 0.01


def hurst(rough: np.ndarray) -> np.ndarray:
    """Pendiente por mínimos cuadrados de ln(rugosidad) frente a ln(L) para L = 1, 2, 5 km (una fila por celda)."""
    y = np.log(np.maximum(np.asarray(rough, dtype=float), FLOOR_M))
    x = np.log(SCALES_KM)
    xc = x - x.mean()
    return (y - y.mean(axis=1, keepdims=True)) @ xc / (xc @ xc)


def add_multiscale(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    r = out[ROUGH].to_numpy(dtype=float)
    out["ms_hurst"] = hurst(r)
    out["ms_lnr1"] = np.log(np.maximum(r[:, 0], FLOOR_M))
    out["ms_lnslope"] = np.log(out["topo__slope_mean_deg"].astype(float) + 0.1)
    return out


def main() -> None:
    earth = add_multiscale(load_features("earth", FEATURES_DIR))
    profiles = {b: profiles_with(add_multiscale(load_features(b, FEATURES_DIR)), MS_COLS) for b in ("moon", "mars")}
    sites, known = add_multiscale(extended_sites()), extended_known()
    usgs = add_multiscale(pd.read_parquet(FEATURES_DIR / "earth_usgs.parquet"))
    base_model = fit_topo_model(earth)
    var_model = fit_topo_model(earth, features=MS_COLS, max_components=3)
    print(f"PCA base: {base_model.n_components} componentes ({base_model.cum_variance[-1]:.2f}); variante: "
          f"{var_model.n_components} ({var_model.cum_variance[-1]:.2f})")
    raw_b = evaluate(earth, profiles, sites, known, lambda b, t: base_model)
    raw_v = evaluate(earth, profiles, sites, known, lambda b, t: var_model)
    rows = [paired(raw_b, raw_v, body, cfg) for body in ("moon", "mars") for cfg in ("todas", "solo topo")]
    res = pd.DataFrame(rows)
    pd.set_option("display.width", 200)
    print(res.round(3).to_string(index=False))
    print("\nCRITERIO PREREGISTRADO (límite inferior de «todas» > 0 en un cuerpo y ningún límite superior < 0):", verdict(rows))
    us_b = usgs_stratified(earth, profiles, usgs, lambda b, t: base_model).assign(modelo="base")
    us_v = usgs_stratified(earth, profiles, usgs, lambda b, t: var_model).assign(modelo="multiescala")
    us = pd.concat([us_b, us_v])
    print("\nUSGS, AUC estratificado por pendiente:")
    print(us[["modelo", "body", "n_strata", "auc_estratificado", "ci_lo", "ci_hi", "senal"]].round(3).to_string(index=False))
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    res.to_csv(RESULTS_DIR / "multiescala_pareada.csv", index=False)
    us.to_csv(RESULTS_DIR / "multiescala_usgs.csv", index=False)


if __name__ == "__main__":
    main()
