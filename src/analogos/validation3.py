"""Tercer conjunto de análogos, del catálogo CAFE de la ESA (docs/PREREGISTRO_VALIDACION3.md).

    python -m analogos.validation3 --build   # características de los 13 sitios nuevos (descarga MODIS)
    python -m analogos.validation3           # evalúa V1 (modelo base) y V2 (unión A o B)
"""
import argparse
import json

import numpy as np
import pandas as pd

from .config import DOCS, FEATURES_DIR, FEATURES_WRITE_DIR, RESULTS_DIR
from .data import earth, earth_geology, earth_thermal, earth_water
from .features import load_features
from .grupos import cold_analogs
from .similarity import fit_topo_model
from .validation2 import known2, sites2, summarize_v2, v2_union
from .validation_ext import YEAR, boot_mean, extended_known, extended_sites, raw_ablation

CSV = DOCS / "analogos_set3.csv"
PARQUET = "earth_sites_ext3.parquet"


def build_sites() -> pd.DataFrame:
    n = pd.read_csv(CSV)
    cells = pd.DataFrame({"cell_id": [f"earth_ext3_{i}" for i in range(len(n))], "body": "earth",
                          "lat": n["lat"], "lon": n["lon"], "name": n["name"]})
    df = pd.concat([cells, earth.build_topography(cells)], axis=1)
    df = earth_thermal.apply_to_earth(df, earth_thermal.run_lst(df, YEAR))
    df = earth_water.apply_to_earth(df, earth_water.run_snow(df, YEAR))
    grid, names, lats, lons = earth_geology.load_glim()
    return earth_geology.apply_to_earth(df, earth_geology.geology_features(df, grid, names, lats, lons))


def known3() -> pd.DataFrame:
    return pd.read_csv(CSV).assign(group="set3")


def sites3() -> pd.DataFrame:
    base = pd.read_parquet(FEATURES_DIR / "earth_sites.parquet")
    new = pd.read_parquet(FEATURES_DIR / PARQUET)
    return new[[c for c in base.columns if c in new.columns]].assign(group="set3")


def per_analog_u(raw: pd.DataFrame) -> pd.Series:
    return raw[raw["config"] == "todas"].groupby(["body", "analog"])["u"].mean()


def v1_rows(per: pd.Series, label: str, body: str, names: list[str]) -> dict:
    v = per.xs(body, level="body").reindex(names).dropna().to_numpy()
    m, lo, hi = boot_mean(v)
    return {"conjunto": label, "body": body, "n_analogos": len(v), "u_medio": m, "ic_lo": lo, "ic_hi": hi,
            "veredicto": ("cumple" if lo > 0.5 else "no cumple") if len(v) >= 8 else "sin veredicto (< 8)"}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--build", action="store_true")
    if ap.parse_args().build:
        FEATURES_WRITE_DIR.mkdir(parents=True, exist_ok=True)
        df = build_sites()
        df.to_parquet(FEATURES_WRITE_DIR / PARQUET, index=False)
        print(f"{len(df)} sitios; térmica {int(df['thermal__t_max_k'].notna().sum())}, nieve {int(df['ice__water_frac'].notna().sum())}, "
              f"geología {int(df['geo__basalt_frac'].notna().sum())}")
        return
    pd.set_option("display.width", 220)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    earth_df = load_features("earth", FEATURES_DIR)
    topo = fit_topo_model(earth_df)
    k2, s2, k3, s3 = known2(), sites2(), known3(), sites3()
    # V1
    raw = raw_ablation(pd.concat([s2, s3], ignore_index=True), pd.concat([k2, k3], ignore_index=True))
    per = per_analog_u(raw)
    n3 = list(k3["name"])
    moon_pool = n3 + [n for n in k2["name"] if n in per.xs("moon", level="body").index]
    rows = [v1_rows(per, "set3", "mars", n3), v1_rows(per, "set3", "moon", n3),
            v1_rows(per, "set2+set3 (Luna, preregistrado)", "moon", moon_pool),
            v1_rows(per, "set2+set3 (Marte, descriptivo)", "mars", n3 + list(k2["name"]))]
    v1 = pd.DataFrame(rows)
    print("V1 (modelo base):\n", v1.round(3).to_string(index=False))
    print(per.round(3).to_string())
    v1.to_csv(RESULTS_DIR / "v3_v1.csv", index=False)
    per.round(4).to_csv(RESULTS_DIR / "v3_u_por_analogo.csv")
    # V2
    known_all = pd.concat([extended_known(), k2, k3], ignore_index=True)
    sites_all = pd.concat([extended_sites(), s2, s3], ignore_index=True)
    res = pd.concat([v2_union(b, earth_df, sites_all, known_all, topo, "set3") for b in ("moon", "mars")], ignore_index=True)
    summ = summarize_v2(res)
    res.round(4).to_csv(RESULTS_DIR / "v3_union_por_analogo.csv", index=False)
    summ.round(4).to_csv(RESULTS_DIR / "v3_union_resumen.csv", index=False)
    print("\nV2 (unión A o B; referencias = los 32 anteriores):\n", summ.round(3).to_string(index=False))
    print(res.round(2).to_string(index=False))
    ok = {}
    for body in ("mars", "moon"):
        g = summ[(summ["body"] == body)]
        u = g[g["medida"] == "u_union"].iloc[0]; dif = g[g["medida"] == "u_union - P_A"].iloc[0]
        ok[body] = {"n": int(u["n"]), "u_lo_gt_05": bool(u["ic_lo"] > 0.5), "dif_lo_gt_0": bool(dif["ic_lo"] > 0), "dif_hi_lt_0": bool(dif["ic_hi"] < 0)}
    adopt = (all(v["u_lo_gt_05"] for v in ok.values() if v["n"] >= 8) and any(v["dif_lo_gt_0"] for v in ok.values() if v["n"] >= 8)
             and not any(v["dif_hi_lt_0"] for v in ok.values() if v["n"] >= 8))
    print("\nV2 veredicto preregistrado:", "SE ADOPTA" if adopt else "NO SE ADOPTA", ok)
    # descriptivo: sitios fríos del conjunto
    cold = cold_analogs(s3, k3)
    print("\nSitios fríos del conjunto:", {n: round(float(per.xs('mars', level='body').get(n, np.nan)), 3) for n in cold})
    (RESULTS_DIR / "v3_resumen.json").write_text(json.dumps({"V2": ok, "adopta_union": bool(adopt)}, indent=1))


if __name__ == "__main__":
    main()
