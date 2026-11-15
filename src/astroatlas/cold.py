"""Permafrost without ice sheets for the cold use case (docs/preregistrations/cold-permafrost.md).

    python -m astroatlas.cold
"""
import json

import numpy as np
import pandas as pd

from .config import FEATURES_DIR, RESULTS_DIR
from .features import load_features
from .groups import COLD_WEIGHTS, cold_analogs, per_analog
from .permafrost import PERMAFROST_K, earth_classes
from .similarity import fit_topo_model, score_cells
from .usecases import pick_regions
from .validate import haversine_km, known_for_body
from .validation2 import known2, sites2, tmean_set2
from .validation_ext import boot_mean, extended_known
from .variants import CONFIGS, evaluate, profiles_with

SNOW_MAX = 0.9


def pf2_class(tmean: pd.Series, snow: pd.Series) -> pd.Series:
    """1 if mean annual temperature < 271 K and mean annual snow < 0.9; 0 otherwise; NaN without temperature."""
    ok = (tmean < PERMAFROST_K) & ~(snow >= SNOW_MAX)
    return pd.Series(np.where(tmean.notna(), ok.astype(float), np.nan), index=tmean.index)


def on_ice_sheet(lat: float, lon: float, snow: float) -> bool:
    """Antarctica (south of 60° S) or the Greenland interior (> 66° N, 75° W to 10° W) with snow >= 0.9."""
    return bool(lat < -60 or (lat > 66 and -75 <= lon <= -10 and snow >= SNOW_MAX))


def main() -> None:
    pd.set_option("display.width", 220)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    new = pd.read_parquet(FEATURES_DIR / "mars_ice_targets.parquet")
    mars = load_features("mars", FEATURES_DIR)
    h = pd.read_csv(FEATURES_DIR / "mars_hydrogen_targets.csv").set_index("site")
    t_ice = list(new["site"]) + sorted(t for t, v in h["ice_rich"].items() if v)
    cols = [c for c in mars.columns if c in new.columns]
    base_df = pd.concat([mars[cols], new[cols]], ignore_index=True)
    cls = {t: float(bool(v)) for t, v in h["ice_rich"].items()}
    cls.update({t: 1.0 for t in new["site"]})
    perma_df = base_df.assign(ice__water_frac=base_df["site"].map(cls))
    earth_pf, sites_ext = earth_classes()
    s2 = sites2().assign(tmean_k=sites2()["name"].map(tmean_set2()).to_numpy())
    sites_all = pd.concat([sites_ext, s2], ignore_index=True)
    known_all = pd.concat([extended_known(), known2()], ignore_index=True)
    earth_v = earth_pf.assign(ice__water_frac=pf2_class(earth_pf["tmean_k"], earth_pf["ice__water_frac"]))
    sites_v = sites_all.assign(ice__water_frac=pf2_class(sites_all["tmean_k"], sites_all["ice__water_frac"]))
    model = fit_topo_model(earth_pf)
    prov = lambda b, t: model  # noqa: E731
    cold = cold_analogs(sites_all, known_all)
    # descriptivo
    old_cls = (earth_pf["tmean_k"] < PERMAFROST_K)
    n_old, n_new = int(old_cls.sum()), int((earth_v["ice__water_frac"] == 1).sum())
    print(f"Cells with class 1: before {n_old}, with the rule {n_new} ({n_old - n_new} turn to 0 because of perennial snow)")
    snow_an = sites_all.set_index("name").loc[cold, ["ice__water_frac", "tmean_k"]].assign(class_PF2=sites_v.set_index("name").loc[cold, "ice__water_frac"])
    print("Cold analogs (mean annual snow, mean annual T, class PF2):\n", snow_an.round(3).to_string())
    pb, pv = profiles_with(base_df), profiles_with(perma_df)
    cfg = {"all": CONFIGS["all"], "cold": COLD_WEIGHTS}
    rb = evaluate(earth_pf, {"mars": pb.loc[t_ice]}, sites_all, known_all, prov, cfg)
    rv = evaluate(earth_v, {"mars": pv.loc[t_ice]}, sites_v, known_all, prov, cfg)
    ub, uv = per_analog(rb, "cold").reindex(cold), per_analog(rv, "cold").reindex(cold)
    m1, lo1, hi1 = boot_mean(uv.to_numpy())
    d, dlo, dhi = boot_mean((uv - ub).to_numpy())
    q1, q2 = lo1 > 0.5, dlo > 0
    print(pd.DataFrame({"base": ub, "PF2": uv, "dif": uv - ub}).round(3).to_string())
    print(f"\nQ1 u PF2 {m1:.3f} (IC {lo1:.3f} a {hi1:.3f}) -> {'MET' if q1 else 'NO MET'}")
    print(f"Q2 diferencia pareada {d:+.3f} (IC {dlo:+.3f} a {dhi:+.3f}) -> {'MET' if q2 else 'NO MET'}")
    # candidatas
    cols_s = [score_cells(earth_v, pv.loc[t], COLD_WEIGHTS, model, ref=earth_v)["score"].to_numpy() for t in t_ice]
    with np.errstate(all="ignore"):
        sc = np.nanmean(np.column_stack(cols_s), axis=1)
    kb = known_for_body(known_all, "mars")
    ok = earth_v["viable"].fillna(True).astype(bool) & ~earth_v["vegetated"].fillna(False).astype(bool)
    far = np.array([haversine_km(r.lat, r.lon, kb["lat"].to_numpy(), kb["lon"].to_numpy()).min() > 500 for r in earth_v.itertuples()])
    cand = earth_v[["cell_id", "lat", "lon"]].assign(score=sc, tmean_k=earth_pf["tmean_k"], snow=earth_pf["ice__water_frac"])
    top = pick_regions(cand[ok.to_numpy() & far].dropna(subset=["score"]), 6)
    top["perm_ok"] = (top["tmean_k"] < PERMAFROST_K) & (top["snow"] < SNOW_MAX)
    top["ice_sheet"] = [on_ice_sheet(r.lat, r.lon, r.snow) for r in top.itertuples()]
    print("\nCold candidates with PF2:\n", top.round(3).to_string(index=False))
    q3 = bool(top["perm_ok"].all() and not top["ice_sheet"].any())
    print(f"Q3 credibilidad: {'MET' if q3 else 'NO MET'}")
    print("VERDICT PREREGISTRADO:", "SE INTEGRA AL CASO FRÍO" if (q1 and q2 and q3) else "NO SE INTEGRA")
    # EXPLORATORY (after seeing Q3, NOT preregistered): exclude all of Antarctica and Greenland (> 60° N, 60° W to 10° W)
    pool = cand[ok.to_numpy() & far].dropna(subset=["score"])
    pool = pool[~((pool["lat"] < -60) | ((pool["lat"] > 60) & (pool["lon"] >= -60) & (pool["lon"] <= -10)))]
    alt = pick_regions(pool, 6)
    print("\nEXPLORATORY (without Antarctica or Greenland, decided after seeing Q3):\n", alt.round(3).to_string(index=False))
    alt.round(4).to_csv(RESULTS_DIR / "cold_candidates_exploratory.csv", index=False)
    top.round(4).to_csv(RESULTS_DIR / "cold_candidates.csv", index=False)
    pd.DataFrame({"base": ub, "PF2": uv}).to_csv(RESULTS_DIR / "cold_analogs.csv")
    (RESULTS_DIR / "cold_summary.json").write_text(json.dumps({
        "cells_class1_before": n_old, "cells_class1_PF2": n_new, "Q1": {"u": m1, "lo": lo1, "hi": hi1, "cumple": bool(q1)},
        "Q2": {"diff": d, "lo": dlo, "hi": dhi, "cumple": bool(q2)}, "Q3": q3, "integra": bool(q1 and q2 and q3)}, indent=1))


if __name__ == "__main__":
    main()
