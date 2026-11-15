"""Experiment: two groups of analogs, cold and warm (docs/preregistrations/cold-warm-groups.md). Mars only.

Cold analogs: monthly maximum of the daytime surface temperature < 295 K. Cold targets: |latitude| >= 45°.
Warm model = base ("all"); cold model = weights {ice 1, topography 0.5} (those of usecases.py, fixed beforehand).

    python -m astroatlas.groups
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
    """Exact one-sided p that the mean of the differences is > 0 (all sign combinations)."""
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
    print(f"Cold targets: {cold_t}\nCold analogs ({len(cold_a)}): {cold_a}\nWarm analogs: {len(warm_a)}")
    model = fit_topo_model(earth)
    configs = {"all": CONFIGS["all"], "cold": COLD_WEIGHTS}
    raw_cold = evaluate(earth, {"mars": prof.loc[cold_t]}, sites, known, lambda b, t: model, configs)
    raw_warm = evaluate(earth, {"mars": prof.loc[warm_t]}, sites, known, lambda b, t: model, configs)
    raw_all = evaluate(earth, {"mars": prof}, sites, known, lambda b, t: model, {"all": CONFIGS["all"]})

    # E1: cold analogs against cold targets
    base, cold = per_analog(raw_cold, "all").reindex(cold_a), per_analog(raw_cold, "cold").reindex(cold_a)
    d = (cold - base).to_numpy()
    m, lo, hi = boot_mean(d)
    mu, mlo, mhi = boot_mean(cold.to_numpy())
    p = exact_sign_flip_p(d)
    ok = lo > 0 and mlo > 0.5
    pd.set_option("display.width", 200)
    print("\nE1 (cold analogs, cold targets):")
    print(pd.DataFrame({"base_all": base, "cold_model": cold, "diff": cold - base}).round(3).to_string())
    print(f"  u base {base.mean():.3f} | cold u {mu:.3f} (IC {mlo:.3f} a {mhi:.3f}) | diferencia {m:+.3f} (IC {lo:+.3f} a {hi:+.3f}) | p exacta {p:.3f}")
    print("  PREREGISTERED CRITERION (lower CI of the difference > 0 and cold u with lower CI > 0.5):", ok)

    # E2: system by groups (descriptive)
    sys_u = pd.concat([per_analog(raw_warm, "all").reindex(warm_a), cold]).reindex(mars_a)
    all_u = per_analog(raw_all, "all").reindex(mars_a)
    ms, slo, shi = boot_mean(sys_u.to_numpy())
    dd = (sys_u - all_u).to_numpy()
    md, dlo, dhi = boot_mean(dd)
    print(f"\nE2 (descriptive, different targets): u of the system by groups {ms:.3f} (IC {slo:.3f} a {shi:.3f}); "
          f"base u over the 14 targets {all_u.mean():.3f}; diferencia pareada {md:+.3f} (IC {dlo:+.3f} a {dhi:+.3f})")
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    pd.DataFrame({"base_all": base, "cold_model": cold, "diff": cold - base}).round(4).to_csv(RESULTS_DIR / "groups_e1.csv")
    pd.DataFrame([{"u_base": base.mean(), "u_cold": mu, "u_cold_lo": mlo, "u_cold_hi": mhi, "diff": m, "diff_lo": lo, "diff_hi": hi,
                   "p_exacta": p, "criterio": ok, "u_sistema": ms, "u_sistema_lo": slo, "u_sistema_hi": shi,
                   "u_base_14": all_u.mean(), "diff_e2": md, "diff_e2_lo": dlo, "diff_e2_hi": dhi}]).to_csv(RESULTS_DIR / "groups_summary.csv", index=False)


if __name__ == "__main__":
    main()
