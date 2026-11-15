"""Experimento: dos grupos de análogos, frío y cálido (docs/PREREGISTRO_GRUPOS.md). Solo Marte.

Análogos fríos: máximo mensual de la temperatura diurna de superficie < 295 K. Objetivos fríos: |latitud| >= 45°.
Modelo cálido = base («todas»); modelo frío = pesos {hielo 1, topografía 0,5} (los de usecases.py, fijados antes).

    python -m analogos.grupos
"""
import itertools

import numpy as np
import pandas as pd

from .config import FEATURES_DIR, RESULTS_DIR
from .features import load_features
from .similarity import fit_topo_model
from .validate import known_for_body
from .validation_ext import boot_mean, extended_known, extended_sites
from .variants import CONFIGS, evaluate, profiles_with

COLD_TMAX_K = 295.0
COLD_LAT = 45.0
COLD_WEIGHTS = {"topo": 0.5, "thermal": 0.0, "ice": 1.0, "geo": 0.0}


def cold_analogs(sites: pd.DataFrame, known: pd.DataFrame, body: str = "mars") -> list[str]:
    names = set(known_for_body(known, body)["name"])
    s = sites[sites["name"].isin(names)]
    return sorted(s.loc[s["thermal__t_max_k"] < COLD_TMAX_K, "name"])


def split_targets(profiles: pd.DataFrame, lat_by_site: pd.Series) -> tuple[list[str], list[str]]:
    cold = [t for t in profiles.index if abs(lat_by_site[t]) >= COLD_LAT]
    return cold, [t for t in profiles.index if t not in cold]


def exact_sign_flip_p(d: np.ndarray) -> float:
    """p exacta de una cola de que la media de las diferencias sea > 0 (todas las combinaciones de signos)."""
    d = d[np.isfinite(d)]
    obs = d.mean()
    means = [np.mean(np.array(s) * d) for s in itertools.product((-1, 1), repeat=len(d))]
    return float(np.mean(np.array(means) >= obs - 1e-12))


def per_analog(raw: pd.DataFrame, cfg: str) -> pd.Series:
    return raw[raw["config"] == cfg].groupby("analog")["u"].mean()


def main() -> None:
    earth = load_features("earth", FEATURES_DIR)
    mars = load_features("mars", FEATURES_DIR)
    prof = profiles_with(mars)
    lat = mars.groupby("site")["lat"].mean()
    cold_t, warm_t = split_targets(prof, lat)
    sites, known = extended_sites(), extended_known()
    cold_a = cold_analogs(sites, known)
    mars_a = sorted(known_for_body(known, "mars")["name"])
    warm_a = [a for a in mars_a if a not in cold_a]
    print(f"Objetivos fríos: {cold_t}\nAnálogos fríos ({len(cold_a)}): {cold_a}\nAnálogos cálidos: {len(warm_a)}")
    model = fit_topo_model(earth)
    configs = {"todas": CONFIGS["todas"], "frio": COLD_WEIGHTS}
    raw_cold = evaluate(earth, {"mars": prof.loc[cold_t]}, sites, known, lambda b, t: model, configs)
    raw_warm = evaluate(earth, {"mars": prof.loc[warm_t]}, sites, known, lambda b, t: model, configs)
    raw_all = evaluate(earth, {"mars": prof}, sites, known, lambda b, t: model, {"todas": CONFIGS["todas"]})

    # E1: análogos fríos frente a objetivos fríos
    base, cold = per_analog(raw_cold, "todas").reindex(cold_a), per_analog(raw_cold, "frio").reindex(cold_a)
    d = (cold - base).to_numpy()
    m, lo, hi = boot_mean(d)
    mu, mlo, mhi = boot_mean(cold.to_numpy())
    p = exact_sign_flip_p(d)
    ok = lo > 0 and mlo > 0.5
    pd.set_option("display.width", 200)
    print("\nE1 (análogos fríos, objetivos fríos):")
    print(pd.DataFrame({"base_todas": base, "modelo_frio": cold, "diff": cold - base}).round(3).to_string())
    print(f"  u base {base.mean():.3f} | u frío {mu:.3f} (IC {mlo:.3f} a {mhi:.3f}) | diferencia {m:+.3f} (IC {lo:+.3f} a {hi:+.3f}) | p exacta {p:.3f}")
    print("  CRITERIO PREREGISTRADO (IC inferior de la diferencia > 0 y u frío con IC inferior > 0,5):", ok)

    # E2: sistema por grupos (descriptiva)
    sys_u = pd.concat([per_analog(raw_warm, "todas").reindex(warm_a), cold]).reindex(mars_a)
    all_u = per_analog(raw_all, "todas").reindex(mars_a)
    ms, slo, shi = boot_mean(sys_u.to_numpy())
    dd = (sys_u - all_u).to_numpy()
    md, dlo, dhi = boot_mean(dd)
    print(f"\nE2 (descriptiva, objetivos distintos): u del sistema por grupos {ms:.3f} (IC {slo:.3f} a {shi:.3f}); "
          f"u base sobre los 14 objetivos {all_u.mean():.3f}; diferencia pareada {md:+.3f} (IC {dlo:+.3f} a {dhi:+.3f})")
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    pd.DataFrame({"base_todas": base, "modelo_frio": cold, "diff": cold - base}).round(4).to_csv(RESULTS_DIR / "grupos_e1.csv")
    pd.DataFrame([{"u_base": base.mean(), "u_frio": mu, "u_frio_lo": mlo, "u_frio_hi": mhi, "diff": m, "diff_lo": lo, "diff_hi": hi,
                   "p_exacta": p, "criterio": ok, "u_sistema": ms, "u_sistema_lo": slo, "u_sistema_hi": shi,
                   "u_base_14": all_u.mean(), "diff_e2": md, "diff_e2_lo": dlo, "diff_e2_hi": dhi}]).to_csv(RESULTS_DIR / "grupos_resumen.csv", index=False)


if __name__ == "__main__":
    main()
