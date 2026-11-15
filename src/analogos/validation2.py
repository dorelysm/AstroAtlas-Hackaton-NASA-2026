"""Segundo conjunto de análogos, independiente (docs/PREREGISTRO_VALIDACION2.md).

    python -m analogos.validation2 --build   # calcula las características de los 9 sitios nuevos (descarga MODIS)
    python -m analogos.validation2           # evalúa V1 (modelo base), V2 (unión A o B) y V3 (permafrost) en el conjunto nuevo
"""
import argparse
import json

import numpy as np
import pandas as pd

from . import aspect
from .config import DOCS, FEATURES_DIR, FEATURES_WRITE_DIR, RESULTS_DIR
from .data import earth, earth_geology, earth_thermal, earth_water
from .features import load_features
from .grupos import COLD_WEIGHTS, cold_analogs, per_analog, split_targets
from .modelos import EXCLUDE_KM, max_over, model_a, percentile_below, rank_pct, similarity_matrix
from .permafrost import annual_mean_k, load_lst, to_class
from .similarity import fit_topo_model, site_profiles
from .validate import haversine_km, known_for_body
from .validation_ext import YEAR, boot_mean, extended_known, extended_sites, raw_ablation
from .variants import CONFIGS, evaluate, paired, profiles_with

CSV = DOCS / "analogos_set2.csv"
TAGS = DOCS / "aspectos_set2.csv"
PARQUET = "earth_sites_ext2.parquet"
KEYFILE = "earth_sites_ext2_lst_key.json"


def build_sites() -> tuple[pd.DataFrame, str]:
    """Características de los sitios nuevos (mismo cálculo que los anteriores) y la clave de la caché de LST."""
    n = pd.read_csv(CSV)
    cells = pd.DataFrame({"cell_id": [f"earth_ext2_{i}" for i in range(len(n))], "body": "earth",
                          "lat": n["lat"], "lon": n["lon"], "name": n["name"]})
    df = pd.concat([cells, earth.build_topography(cells)], axis=1)
    df = earth_thermal.apply_to_earth(df, earth_thermal.run_lst(df, YEAR))
    df = earth_water.apply_to_earth(df, earth_water.run_snow(df, YEAR))
    grid, names, lats, lons = earth_geology.load_glim()
    df = earth_geology.apply_to_earth(df, earth_geology.geology_features(df, grid, names, lats, lons))
    return df, earth_water._key(cells, earth_water.HALF_KM)


def known2() -> pd.DataFrame:
    return pd.read_csv(CSV).assign(group="set2")


def sites2() -> pd.DataFrame:
    base = pd.read_parquet(FEATURES_DIR / "earth_sites.parquet")
    new = pd.read_parquet(FEATURES_DIR / PARQUET)
    return new[[c for c in base.columns if c in new.columns]].assign(group="set2")


def tmean_set2() -> pd.Series:
    key = json.loads((FEATURES_DIR / KEYFILE).read_text())["key"]
    day, night = load_lst(key)
    return pd.Series(annual_mean_k(day, night), index=pd.read_csv(CSV)["name"])


def v2_union(body: str, earth_df, sites_all, known_all, topo, new_group: str = "set2") -> pd.DataFrame:
    """V2: análogos del grupo `new_group` (por defecto el segundo conjunto) evaluados con A, B (referencias = SOLO los 23 del primer conjunto) y la unión (máximo)."""
    target = load_features(body, FEATURES_DIR)
    kb = known_for_body(known_all, body)
    old, new = kb[kb["group"] != new_group].reset_index(drop=True), kb[kb["group"] == new_group].reset_index(drop=True)
    if new.empty:
        return pd.DataFrame()
    s_old = sites_all.set_index("name").loc[list(old["name"])].reset_index()
    s_new = sites_all.set_index("name").loc[list(new["name"])].reset_index()
    S_cells = similarity_matrix(earth_df, s_old, earth_df, topo)
    S_new = similarity_matrix(s_new, s_old, earth_df, topo)
    A_cells, A_new = model_a(earth_df, s_new, target, topo)
    PA = rank_pct(A_cells)
    rows = []
    for i, r in new.iterrows():
        d = haversine_km(r["lat"], r["lon"], old["lat"].to_numpy(), old["lon"].to_numpy())
        refs = [j for j in range(len(old)) if d[j] >= EXCLUDE_KM]
        b_cells, b_site = max_over(S_cells, refs), max_over(S_new[[i]], refs)[0]
        pa_site, pb_site = percentile_below(A_cells, A_new[i]), percentile_below(b_cells, b_site)
        union = np.fmax(PA, rank_pct(b_cells))
        rows.append({"body": body, "analog": r["name"], "n_refs": len(refs), "P_A": pa_site, "u_B": pb_site,
                     "u_union": percentile_below(union, max(pa_site, pb_site))})
    return pd.DataFrame(rows)


def summarize_v2(res: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for body, g in res.groupby("body"):
        for col in ("P_A", "u_B", "u_union"):
            m, lo, hi = boot_mean(g[col].to_numpy())
            rows.append({"body": body, "medida": col, "n": int(g[col].notna().sum()), "u_medio": m, "ic_lo": lo, "ic_hi": hi})
        m, lo, hi = boot_mean((g["u_union"] - g["P_A"]).dropna().to_numpy())
        rows.append({"body": body, "medida": "u_union - P_A", "n": len(g), "u_medio": m, "ic_lo": lo, "ic_hi": hi})
    return pd.DataFrame(rows)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--build", action="store_true")
    a = ap.parse_args()
    if a.build:
        FEATURES_WRITE_DIR.mkdir(parents=True, exist_ok=True)
        df, key = build_sites()
        df.to_parquet(FEATURES_WRITE_DIR / PARQUET, index=False)
        (FEATURES_WRITE_DIR / KEYFILE).write_text(json.dumps({"key": key}))
        print(f"{len(df)} sitios; con térmica {int(df['thermal__t_max_k'].notna().sum())}, nieve {int(df['ice__water_frac'].notna().sum())}, "
              f"geología {int(df['geo__basalt_frac'].notna().sum())}; clave LST {key}")
        return
    pd.set_option("display.width", 220)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    earth_df = load_features("earth", FEATURES_DIR)
    topo = fit_topo_model(earth_df)
    k2, s2 = known2(), sites2()
    # V1: modelo base sobre el conjunto nuevo
    raw = raw_ablation(s2, k2)
    raw.to_csv(RESULTS_DIR / "v2_ablation_raw.csv", index=False)
    per = raw[raw["config"] == "todas"].groupby(["body", "analog"])["u"].mean()
    v1 = []
    for body, g in per.groupby(level=0):
        m, lo, hi = boot_mean(g.to_numpy())
        v1.append({"body": body, "n_analogos": len(g), "u_medio": m, "ic_lo": lo, "ic_hi": hi, "cumple": bool(lo > 0.5 and len(g) >= 8)})
    v1 = pd.DataFrame(v1)
    print("V1 (modelo base, conjunto nuevo):\n", v1.round(3).to_string(index=False))
    print(per.round(3).to_string())
    v1.to_csv(RESULTS_DIR / "v2_v1.csv", index=False)
    per.round(4).to_csv(RESULTS_DIR / "v2_u_por_analogo.csv")
    # V2: unión A o B con referencias = los 23 anteriores
    known_all = pd.concat([extended_known(), k2], ignore_index=True)
    sites_all = pd.concat([extended_sites(), s2], ignore_index=True)
    res = pd.concat([v2_union(b, earth_df, sites_all, known_all, topo) for b in ("moon", "mars")], ignore_index=True)
    summ = summarize_v2(res)
    res.round(4).to_csv(RESULTS_DIR / "v2_union_por_analogo.csv", index=False)
    summ.round(4).to_csv(RESULTS_DIR / "v2_union_resumen.csv", index=False)
    print("\nV2 (unión A o B, referencias = los 23 anteriores):\n", summ.round(3).to_string(index=False))
    print(res[res["body"] == "mars"].round(2).to_string(index=False))
    # V3: variable de permafrost
    h = pd.read_csv(FEATURES_DIR / "mars_hydrogen_targets.csv").set_index("site")
    mars = load_features("mars", FEATURES_DIR)
    mars_v = mars.assign(ice__water_frac=mars["site"].map(h["rico_en_hielo"].astype(float)))
    from .permafrost import earth_classes
    earth_pf, _ = earth_classes()
    t2 = tmean_set2()
    s2_v = s2.assign(ice__water_frac=to_class(s2["name"].map(t2)), tmean_k=s2["name"].map(t2).to_numpy())
    print("\nClase de permafrost de los análogos nuevos:", s2_v.set_index("name")["ice__water_frac"].to_dict(),
          "\ntemperatura media anual (K):", t2.round(1).to_dict())
    model = fit_topo_model(earth_pf)
    prof_b, prof_v = profiles_with(mars), profiles_with(mars_v)
    earth_v = earth_pf.assign(ice__water_frac=to_class(earth_pf["tmean_k"]))
    raw_b = evaluate(earth_pf, {"mars": prof_b}, s2, k2, lambda b, t: model)
    raw_v = evaluate(earth_v, {"mars": prof_v}, s2_v, k2, lambda b, t: model)
    prim = paired(raw_b, raw_v, "mars", "todas")
    print(f"\nV3 primaria (Marte 'todas'): base {prim['u_base']:.3f} -> {prim['u_variante']:.3f}; dif {prim['diff']:+.3f} "
          f"(IC {prim['ic_lo']:+.3f} a {prim['ic_hi']:+.3f}) -> {'CUMPLE' if prim['ic_lo'] > 0 else 'NO CUMPLE'}")
    lat = mars.groupby("site")["lat"].mean()
    cold_t, _ = split_targets(prof_b, lat)
    cold_a = [n for n in cold_analogs(s2, k2)]
    sec = {"n_frios": len(cold_a), "frios": cold_a}
    if len(cold_a) >= 5:
        cfg = {"todas": CONFIGS["todas"], "frio": COLD_WEIGHTS}
        cb = evaluate(earth_pf, {"mars": prof_b.loc[cold_t]}, s2, k2, lambda b, t: model, cfg)
        cv = evaluate(earth_v, {"mars": prof_v.loc[cold_t]}, s2_v, k2, lambda b, t: model, cfg)
        ub, uv = per_analog(cb, "frio").reindex(cold_a), per_analog(cv, "frio").reindex(cold_a)
        m, lo, hi = boot_mean(uv.to_numpy())
        sec.update({"u_variante": m, "lo": lo, "hi": hi, "cumple": bool(lo > 0.5)})
    else:
        sec["veredicto"] = "sin veredicto (< 5 análogos fríos nuevos)"
        if cold_a:
            cfg = {"todas": CONFIGS["todas"], "frio": COLD_WEIGHTS}
            cb = evaluate(earth_pf, {"mars": prof_b.loc[cold_t]}, s2, k2, lambda b, t: model, cfg)
            cv = evaluate(earth_v, {"mars": prof_v.loc[cold_t]}, s2_v, k2, lambda b, t: model, cfg)
            sec["u_base"] = per_analog(cb, "frio").reindex(cold_a).round(3).to_dict()
            sec["u_variante"] = per_analog(cv, "frio").reindex(cold_a).round(3).to_dict()
    print("V3 secundaria:", sec)
    pd.DataFrame([prim]).to_csv(RESULTS_DIR / "v2_v3_primaria.csv", index=False)
    (RESULTS_DIR / "v2_v3_secundaria.json").write_text(json.dumps(sec, default=str, indent=1))


if __name__ == "__main__":
    main()
