"""Objetivos de hielo somero con evidencia publicada y variable de permafrost (docs/PREREGISTRO_HIELO_SOMERO.md).

    python -m analogos.hielo_somero --build   # características de los 8 objetivos nuevos (MOLA, ventana de 50 km)
    python -m analogos.hielo_somero           # evalúa P1, P2 y las secundarias
"""
import argparse
import json

import numpy as np
import pandas as pd

from .config import DOCS, FEATURES_DIR, FEATURES_WRITE_DIR, RESULTS_DIR
from .data.dem import build_target_features
from .data.planetary import add_properties
from .data.pds_dem import mola_dem
from .features import load_features
from .grupos import COLD_WEIGHTS, cold_analogs, per_analog
from .permafrost import earth_classes, to_class
from .polar_ice import H_ICE, lookup
from .similarity import fit_topo_model
from .validation2 import known2, sites2, tmean_set2
from .validation_ext import boot_mean, extended_known
from .variants import CONFIGS, evaluate, paired, profiles_with

CSV = DOCS / "objetivos_hielo_dundas.csv"
PARQUET = "mars_ice_targets.parquet"


def build_targets() -> pd.DataFrame:
    s = pd.read_csv(CSV)
    sites = pd.DataFrame({"site": s["site"], "body": "mars", "lat": s["lat"], "lon": s["lon"] % 360, "kind": "ice_target",
                          "source": "Dundas 2021"})
    return add_properties(build_target_features("mars", mola_dem(), sites, 25.0), "mars")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--build", action="store_true")
    if ap.parse_args().build:
        FEATURES_WRITE_DIR.mkdir(parents=True, exist_ok=True)
        t = build_targets()
        t.to_parquet(FEATURES_WRITE_DIR / PARQUET, index=False)
        print(t[["site", "lat", "lon", "topo__slope_mean_deg", "ice__water_frac", "geo__basalt_frac"]].round(3).to_string(index=False))
        return
    pd.set_option("display.width", 220)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    new = pd.read_parquet(FEATURES_DIR / PARQUET)
    mars = load_features("mars", FEATURES_DIR)
    h = pd.read_csv(FEATURES_DIR / "mars_hydrogen_targets.csv").set_index("site")
    rich_old = {t for t, v in h["rico_en_hielo"].items() if v}
    t_ice = list(new["site"]) + sorted(rich_old)
    cols = [c for c in mars.columns if c in new.columns]
    base_df = pd.concat([mars[cols], new[cols]], ignore_index=True)
    cls = {t: float(bool(v)) for t, v in h["rico_en_hielo"].items()}
    cls.update({t: 1.0 for t in new["site"]})
    perma_df = base_df.assign(ice__water_frac=base_df["site"].map(cls))
    # Tierra y análogos (los 23 + los 9 del segundo conjunto)
    earth_pf, sites_ext = earth_classes()
    s2 = sites2().assign(tmean_k=sites2()["name"].map(tmean_set2()).to_numpy())
    sites_all = pd.concat([sites_ext, s2], ignore_index=True)
    known_all = pd.concat([extended_known(), known2()], ignore_index=True)
    earth_v = earth_pf.assign(ice__water_frac=to_class(earth_pf["tmean_k"]))
    sites_v = sites_all.assign(ice__water_frac=to_class(sites_all["tmean_k"]))
    model = fit_topo_model(earth_pf)
    prov = lambda b, t: model  # noqa: E731
    cold = cold_analogs(sites_all, known_all)
    print(f"Objetivos de hielo ({len(t_ice)}): {t_ice}\nAnálogos fríos ({len(cold)}): {cold}")
    pb, pv = profiles_with(base_df), profiles_with(perma_df)
    cfg = {"todas": CONFIGS["todas"], "frio": COLD_WEIGHTS}
    rb = evaluate(earth_pf, {"mars": pb.loc[t_ice]}, sites_all, known_all, prov, cfg)
    rv = evaluate(earth_v, {"mars": pv.loc[t_ice]}, sites_v, known_all, prov, cfg)
    ub, uv = per_analog(rb, "frio").reindex(cold), per_analog(rv, "frio").reindex(cold)
    m1, lo1, hi1 = boot_mean(uv.to_numpy())
    mb, lob, hib = boot_mean(ub.to_numpy())
    d, dlo, dhi = boot_mean((uv - ub).to_numpy())
    p1, p2 = lo1 > 0.5, dlo > 0
    print(pd.DataFrame({"base": ub, "permafrost": uv, "dif": uv - ub}).round(3).to_string())
    print(f"\nP1 u permafrost {m1:.3f} (IC {lo1:.3f} a {hi1:.3f}) -> {'CUMPLE' if p1 else 'NO CUMPLE'}")
    print(f"P2 diferencia pareada {d:+.3f} (IC {dlo:+.3f} a {dhi:+.3f}) -> {'CUMPLE' if p2 else 'NO CUMPLE'}")
    print(f"(b) u base frente a los objetivos de hielo: {mb:.3f} (IC {lob:.3f} a {hib:.3f})")
    print("VEREDICTO PREREGISTRADO:", "SE ADOPTA" if (p1 and p2) else "NO SE ADOPTA")
    # (a) nuevos fríos por separado
    new_cold = [n for n in cold if n in set(s2["name"])]
    print("(a) fríos nuevos:", {n: (round(float(ub[n]), 3), round(float(uv[n]), 3)) for n in new_cold})
    # (c) efecto en «todas» al añadir los 8 objetivos
    rb14 = evaluate(earth_pf, {"mars": profiles_with(mars)}, sites_all, known_all, prov)
    rb22 = evaluate(earth_pf, {"mars": pb}, sites_all, known_all, prov)
    rv22 = evaluate(earth_v, {"mars": pv}, sites_v, known_all, prov)
    c1, c2 = paired(rb14, rb22, "mars", "todas"), paired(rb14, rv22, "mars", "todas")
    print(f"(c) 'todas' Marte: base 14 -> base 22 {c1['u_base']:.3f}->{c1['u_variante']:.3f} dif {c1['diff']:+.3f} ({c1['ic_lo']:+.3f} a {c1['ic_hi']:+.3f}); "
          f"base 14 -> permafrost 22 dif {c2['diff']:+.3f} ({c2['ic_lo']:+.3f} a {c2['ic_hi']:+.3f})")
    # (d) índice de neutrones en los 8 sitios
    cells = pd.read_parquet(FEATURES_DIR / "mars_hydrogen_cells.parquet")
    dd = []
    for r in new.itertuples():
        c = lookup(cells, r.lat, r.lon)
        dd.append({"site": r.site, "lat": r.lat, "H": round(float(c["H"]), 3), "rico_segun_H": bool(c["H"] >= H_ICE)})
    dd = pd.DataFrame(dd)
    print("\n(d) índice de neutrones en los 8 sitios con hielo publicado:\n", dd.to_string(index=False))
    print(f"    {int(dd['rico_segun_H'].sum())} de {len(dd)} marcados «ricos» por H")
    # EXPLORATORIO (no preregistrado): candidatas frías con la variante permafrost y los pesos del modelo frío
    from .similarity import score_cells
    from .usecases import pick_regions
    from .validate import haversine_km, known_for_body
    cols_s = [score_cells(earth_v, pv.loc[t], COLD_WEIGHTS, model, ref=earth_v)["score"].to_numpy() for t in t_ice]
    with np.errstate(all="ignore"):
        sc = np.nanmean(np.column_stack(cols_s), axis=1)
    kb = known_for_body(known_all, "mars")
    ok = earth_v["viable"].fillna(True).astype(bool) & ~earth_v["vegetated"].fillna(False).astype(bool)
    far = np.array([haversine_km(r.lat, r.lon, kb["lat"].to_numpy(), kb["lon"].to_numpy()).min() > 500 for r in earth_v.itertuples()])
    cand = earth_v[["cell_id", "lat", "lon"]].assign(score=sc, tmean_k=earth_v["tmean_k"])
    top = pick_regions(cand[ok.to_numpy() & far].dropna(subset=["score"]), 6)
    top.round(4).to_csv(RESULTS_DIR / "hielo_somero_candidatas_frias.csv", index=False)
    print("\nCandidatas frías (exploratorio):\n", top.round(3).to_string(index=False))
    pd.DataFrame({"base": ub, "permafrost": uv}).to_csv(RESULTS_DIR / "hielo_somero_frios.csv")
    dd.to_csv(RESULTS_DIR / "hielo_somero_indice_H.csv", index=False)
    (RESULTS_DIR / "hielo_somero_resumen.json").write_text(json.dumps({
        "n_frios": len(cold), "P1": {"u": m1, "lo": lo1, "hi": hi1, "cumple": bool(p1)},
        "P2": {"diff": d, "lo": dlo, "hi": dhi, "cumple": bool(p2)}, "u_base": mb, "c_base22": c1, "c_perma22": c2,
        "adopta": bool(p1 and p2)}, default=str, indent=1))


if __name__ == "__main__":
    main()
