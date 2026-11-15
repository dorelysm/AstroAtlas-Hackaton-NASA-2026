"""Variable de «hielo en el suelo» comparable entre cuerpos (docs/PREREGISTRO_HIELO_POLAR.md, Fase 2).

Marte: clase *rico en hielo* si el índice de hidrógeno H de los neutrones epitérmicos de Odyssey es >= ln(1,5) (polar_ice.py).
Tierra: clase *permafrost probable* si la temperatura media anual de superficie (MODIS 2019, media de (día + noche)/2) es < 271 K.
Las dos clases sustituyen a `ice__water_frac` (agua en Marte, nieve en la Tierra). Evaluación con los 23 análogos congelados.

    python -m analogos.permafrost
"""
import glob

import numpy as np
import pandas as pd

from .config import FEATURES_DIR, RAW_DIR, RESULTS_DIR
from .features import load_features
from .grupos import COLD_LAT, COLD_WEIGHTS, cold_analogs, per_analog, split_targets
from .similarity import fit_topo_model
from .validation_ext import boot_mean, extended_known, extended_sites
from .variants import CONFIGS, evaluate, paired, profiles_with

PERMAFROST_K = 271.0
MIN_MONTHS = 6
REDUCED = RAW_DIR / "earthdata" / "reduced"
KEY_MAIN, KEY_EXT = "5122d582a7", "8f6728403c"


def load_lst(key: str) -> tuple[np.ndarray, np.ndarray]:
    """(meses x celdas) de LST diurna y nocturna de la caché de reducciones de MODIS."""
    a = np.vstack([np.load(f) for f in sorted(glob.glob(str(REDUCED / f"lst_*_{key}.npy")))])
    n = a.shape[1] // 2
    return a[:, :n], a[:, n:]


def annual_mean_k(day: np.ndarray, night: np.ndarray) -> np.ndarray:
    """Media anual de (día + noche)/2 sobre los meses con dato; NaN si hay menos de MIN_MONTHS."""
    m = (day + night) / 2.0
    with np.errstate(all="ignore"):
        mean = np.nanmean(m, axis=0)
    return np.where(np.isfinite(m).sum(axis=0) >= MIN_MONTHS, mean, np.nan)


def align(cache_t: np.ndarray, current_tmax: np.ndarray) -> list[int]:
    """Índices de las columnas de la caché que corresponden a las filas actuales (la tabla perdió 4 celdas de agua desde entonces).
    Se alinean con dos punteros comparando el máximo mensual de temperatura, que se guardó en la tabla."""
    i = j = 0
    idx: list[int] = []
    while i < len(cache_t) and j < len(current_tmax):
        if np.isclose(cache_t[i], current_tmax[j], atol=1e-4, equal_nan=True):
            idx.append(i)
            i += 1
            j += 1
        else:
            i += 1
    if len(idx) != len(current_tmax):
        raise RuntimeError(f"no se pudo alinear la caché: {len(idx)} de {len(current_tmax)}")
    return idx


def earth_classes() -> tuple[pd.DataFrame, pd.DataFrame]:
    """(celdas de la Tierra, sitios análogos ampliados) con `ice__water_frac` sustituido por la clase de permafrost y `tmean_k`."""
    earth = pd.read_parquet(FEATURES_DIR / "earth.parquet")
    base = pd.read_parquet(FEATURES_DIR / "earth_sites.parquet")
    day, night = load_lst(KEY_MAIN)
    tm = annual_mean_k(day, night)
    cur = np.concatenate([earth["thermal__t_max_k"].to_numpy(), base["thermal__t_max_k"].to_numpy()])
    idx = align(_tmax(day), cur)
    t_all = tm[idx]
    earth = earth.assign(tmean_k=t_all[: len(earth)])
    sites = extended_sites()
    t_sites = {n: t for n, t in zip(base["name"], t_all[len(earth):])}
    dx, nx = load_lst(KEY_EXT)
    ext = pd.read_parquet(FEATURES_DIR / "earth_sites_ext.parquet")
    t_sites.update({n: t for n, t in zip(ext["name"], annual_mean_k(dx, nx))})
    sites = sites.assign(tmean_k=sites["name"].map(t_sites))
    return earth, sites


def _tmax(day: np.ndarray) -> np.ndarray:
    with np.errstate(all="ignore"):
        return np.nanmax(day, axis=0)


def to_class(tmean: pd.Series) -> pd.Series:
    return pd.Series(np.where(tmean.notna(), (tmean < PERMAFROST_K).astype(float), np.nan), index=tmean.index)


def main() -> None:
    earth, sites = earth_classes()
    mars = load_features("mars", FEATURES_DIR)
    h = pd.read_csv(FEATURES_DIR / "mars_hydrogen_targets.csv").set_index("site")
    mars_v = mars.assign(ice__water_frac=mars["site"].map(h["rico_en_hielo"].astype(float)))
    earth_v = earth.assign(ice__water_frac=to_class(earth["tmean_k"]))
    sites_v = sites.assign(ice__water_frac=to_class(sites["tmean_k"]))
    known = extended_known()
    model = fit_topo_model(earth)
    lat = mars.groupby("site")["lat"].mean()
    prof_b, prof_v = profiles_with(mars), profiles_with(mars_v)
    cold_t, _ = split_targets(prof_b, lat)
    cold_a = cold_analogs(sites, known)
    print(f"Tierra: celdas con permafrost probable {int(earth_v['ice__water_frac'].sum())} de {int(earth_v['ice__water_frac'].notna().sum())}; "
          f"clase de los análogos fríos: {sites_v.set_index('name').loc[cold_a, 'ice__water_frac'].to_dict()}")
    print(f"Marte, objetivos ricos en hielo: {[t for t, v in h['rico_en_hielo'].items() if v]}")

    raw_b = evaluate(earth, {"mars": prof_b}, sites, known, lambda b, t: model)
    raw_v = evaluate(earth_v, {"mars": prof_v}, sites_v, known, lambda b, t: model)
    rows = [paired(raw_b, raw_v, "mars", cfg) for cfg in ("todas", "solo topo")]
    prim = rows[0]
    print(f"\nPRIMARIA, Marte 'todas': base {prim['u_base']:.3f} -> variante {prim['u_variante']:.3f}; diferencia pareada "
          f"{prim['diff']:+.3f} (IC {prim['ic_lo']:+.3f} a {prim['ic_hi']:+.3f})  ->  {'CUMPLE' if prim['ic_lo'] > 0 else 'NO CUMPLE'}")

    cfg = {"todas": CONFIGS["todas"], "frio": COLD_WEIGHTS}
    cold_b = evaluate(earth, {"mars": prof_b.loc[cold_t]}, sites, known, lambda b, t: model, cfg)
    cold_v = evaluate(earth_v, {"mars": prof_v.loc[cold_t]}, sites_v, known, lambda b, t: model, cfg)
    ub, uv = per_analog(cold_b, "frio").reindex(cold_a), per_analog(cold_v, "frio").reindex(cold_a)
    m, lo, hi = boot_mean(uv.to_numpy())
    d, dlo, dhi = boot_mean((uv - ub).to_numpy())
    sec = lo > 0.5
    print(f"SECUNDARIA, análogos fríos frente a objetivos fríos {cold_t} con pesos del modelo frío:")
    print(pd.DataFrame({"base": ub, "variante": uv, "diff": uv - ub}).round(3).to_string())
    print(f"  u variante {m:.3f} (IC {lo:.3f} a {hi:.3f}); diferencia con la base {d:+.3f} (IC {dlo:+.3f} a {dhi:+.3f})  ->  "
          f"{'CUMPLE' if sec else 'NO CUMPLE'}")
    print("\nVEREDICTO PREREGISTRADO (primaria Y secundaria):", "SE ADOPTA" if (prim["ic_lo"] > 0 and sec) else "NO SE ADOPTA")
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(RESULTS_DIR / "permafrost_pareada.csv", index=False)
    pd.DataFrame({"base": ub, "variante": uv}).to_csv(RESULTS_DIR / "permafrost_frios.csv")
    pd.DataFrame([{"u_frio": m, "lo": lo, "hi": hi, "diff": d, "diff_lo": dlo, "diff_hi": dhi,
                   "primaria": prim["ic_lo"] > 0, "secundaria": sec}]).to_csv(RESULTS_DIR / "permafrost_resumen.csv", index=False)


if __name__ == "__main__":
    main()
