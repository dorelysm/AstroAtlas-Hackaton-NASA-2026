"""Clase de permafrost a partir del mapa de Obu et al. (2018) para el caso de uso frío (docs/PREREGISTRO_PERMAFROST_MAPA.md).

    python -m analogos.permafrost_mapa      # usa data/raw/permafrost/UiO_PEX_25km.nc (PANGAEA 888600, CC-BY 3.0)
"""
import json

import numpy as np
import pandas as pd
from scipy.spatial import cKDTree

from .config import DEMO_DIR, FEATURES_DIR, RAW_DIR, RESULTS_DIR
from .features import load_features
from .grupos import COLD_WEIGHTS, cold_analogs, per_analog
from .permafrost import PERMAFROST_K, earth_classes
from .similarity import fit_topo_model, score_cells
from .usecases import pick_regions
from .validate import haversine_km, known_for_body
from .validation2 import known2, sites2, tmean_set2
from .validation3 import known3, sites3
from .validation_ext import boot_mean, extended_known, extended_sites
from .variants import CONFIGS, evaluate, profiles_with

NC = RAW_DIR / "permafrost" / "UiO_PEX_25km.nc"
R_EARTH_KM = 6371.0
WINDOW_KM, NEAREST_KM, THRESHOLD = 25.0, 30.0, 0.5


def _xyz(lat, lon):
    la, lo = np.radians(np.asarray(lat, float)), np.radians(np.asarray(lon, float))
    return np.column_stack([np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)])


def perprob_window(lats: np.ndarray, lons: np.ndarray) -> np.ndarray:
    """Media de PerProb (píxeles válidos a <= 25 km; si no hay píxel, el más cercano a <= 30 km); NaN si no hay dato."""
    import netCDF4 as nc

    d = nc.Dataset(NC)
    p = np.ma.filled(d["PerProb"][:].astype(float), np.nan).ravel()
    la = np.ma.filled(d["latitude"][:].astype(float), np.nan).ravel()
    lo = np.ma.filled(d["longitude"][:].astype(float), np.nan).ravel()
    ok = np.isfinite(la) & np.isfinite(lo)
    tree = cKDTree(_xyz(la[ok], lo[ok]))
    pv = p[ok]
    out = np.full(len(lats), np.nan)
    pts = _xyz(lats, lons)
    for k, idx in enumerate(tree.query_ball_point(pts, WINDOW_KM / R_EARTH_KM)):
        if not idx:
            dist, j = tree.query(pts[k])
            idx = [j] if dist * R_EARTH_KM <= NEAREST_KM else []
        v = pv[idx]
        v = v[np.isfinite(v)]
        if v.size:
            out[k] = float(v.mean())
    return out


def pf3_class(pp: np.ndarray) -> np.ndarray:
    """1 si PerProb medio >= 0,5; 0 en cualquier otro caso (incluye sin dato: hielo, hemisferio sur, mar)."""
    return np.where(np.isfinite(pp) & (pp >= THRESHOLD), 1.0, 0.0)


UC_KEY = "frio_marte_permafrost"
UC_TITLE = "Hielo en el suelo y permafrost (Marte), con mapa de permafrost"


def append_use_case(top: pd.DataFrame, earth_v: pd.DataFrame, known_all: pd.DataFrame, n_targets: int) -> None:
    """Añade (o reemplaza) las filas del caso frío en data/results/usecases.csv y en su copia de demo_data (idempotente)."""
    k = known_all[known_all["analog_of"].fillna("").str.contains("mars")]
    ex = earth_v.set_index("cell_id")
    rows = []
    for rank, r in enumerate(top.itertuples(), 1):
        d = haversine_km(r.lat, r.lon, k["lat"].to_numpy(), k["lon"].to_numpy())
        j = int(d.argmin())
        rows.append({"use_case": UC_KEY, "title": UC_TITLE, "rank": rank, "cell_id": r.cell_id, "lat": r.lat, "lon": r.lon, "score": r.score,
                     "n_targets": n_targets, "nearest_known": k["name"].iloc[j], "nearest_known_km": float(d[j]),
                     "dist_settlement_km": ex.loc[r.cell_id].get("dist_settlement_km"), "ndvi_max": ex.loc[r.cell_id].get("veg_ndvi_max")})
    new = pd.DataFrame(rows)
    for path in (RESULTS_DIR / "usecases.csv", DEMO_DIR / "results" / "usecases.csv"):
        if path.exists():
            old = pd.read_csv(path)
            pd.concat([old[old["use_case"] != UC_KEY], new], ignore_index=True).to_csv(path, index=False)


def main() -> None:
    pd.set_option("display.width", 220)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    new = pd.read_parquet(FEATURES_DIR / "mars_ice_targets.parquet")
    mars = load_features("mars", FEATURES_DIR)
    h = pd.read_csv(FEATURES_DIR / "mars_hydrogen_targets.csv").set_index("site")
    t_ice = list(new["site"]) + sorted(t for t, v in h["rico_en_hielo"].items() if v)
    cols = [c for c in mars.columns if c in new.columns]
    base_df = pd.concat([mars[cols], new[cols]], ignore_index=True)
    cls = {t: float(bool(v)) for t, v in h["rico_en_hielo"].items()}
    cls.update({t: 1.0 for t in new["site"]})
    perma_df = base_df.assign(ice__water_frac=base_df["site"].map(cls))
    earth_pf, sites_ext = earth_classes()
    s2 = sites2().assign(tmean_k=sites2()["name"].map(tmean_set2()).to_numpy())
    s3 = sites3().assign(tmean_k=np.nan)
    sites_all = pd.concat([sites_ext, s2, s3], ignore_index=True)
    known_all = pd.concat([extended_known(), known2(), known3()], ignore_index=True)
    # clases con el mapa
    pe = perprob_window(earth_pf["lat"].to_numpy(), earth_pf["lon"].to_numpy())
    ps = perprob_window(sites_all["lat"].to_numpy(), sites_all["lon"].to_numpy())
    earth_v = earth_pf.assign(ice__water_frac=pf3_class(pe), perprob=pe)
    sites_v = sites_all.assign(ice__water_frac=pf3_class(ps), perprob=ps)
    n_map, n_T = int((earth_v["ice__water_frac"] == 1).sum()), int((earth_pf["tmean_k"] < PERMAFROST_K).sum())
    agree = int(((earth_v["ice__water_frac"] == 1) & (earth_pf["tmean_k"] < PERMAFROST_K)).sum())
    print(f"Celdas con clase 1: mapa {n_map}; regla de temperatura {n_T}; ambas {agree} (de las {n_T} por temperatura, "
          f"{n_T - agree} no son permafrost según el mapa)")
    cold = cold_analogs(sites_all, known_all)
    print("Análogos fríos y su PerProb medio (clase PF3):\n", sites_v.set_index("name").loc[cold, ["perprob", "ice__water_frac"]].round(3).to_string())
    model = fit_topo_model(earth_pf)
    prov = lambda b, t: model  # noqa: E731
    pb, pv = profiles_with(base_df), profiles_with(perma_df)
    cfg = {"todas": CONFIGS["todas"], "frio": COLD_WEIGHTS}
    rb = evaluate(earth_pf, {"mars": pb.loc[t_ice]}, sites_all, known_all, prov, cfg)
    rv = evaluate(earth_v, {"mars": pv.loc[t_ice]}, sites_v, known_all, prov, cfg)
    ub, uv = per_analog(rb, "frio").reindex(cold), per_analog(rv, "frio").reindex(cold)
    m1, lo1, hi1 = boot_mean(uv.to_numpy())
    d, dlo, dhi = boot_mean((uv - ub).to_numpy())
    r1, r2 = lo1 > 0.5, dlo > 0
    print(pd.DataFrame({"base": ub, "PF3": uv, "dif": uv - ub}).round(3).to_string())
    print(f"\nR1 u PF3 {m1:.3f} (IC {lo1:.3f} a {hi1:.3f}) -> {'CUMPLE' if r1 else 'NO CUMPLE'}")
    print(f"R2 diferencia pareada {d:+.3f} (IC {dlo:+.3f} a {dhi:+.3f}) -> {'CUMPLE' if r2 else 'NO CUMPLE'}")
    prev7 = [n for n in cold if n in set(extended_known()["name"]) or n in {"CRREL Permafrost Tunnel (Fairbanks Alaska)", "Tuktoyaktuk (Canada)"}]
    if prev7:
        m7, l7, h7 = boot_mean(uv.reindex(prev7).to_numpy())
        d7, dl7, dh7 = boot_mean((uv - ub).reindex(prev7).to_numpy())
        print(f"(subconjunto de los análogos fríos anteriores, n={len(prev7)}): u PF3 {m7:.3f} (IC {l7:.3f} a {h7:.3f}); dif {d7:+.3f} (IC {dl7:+.3f} a {dh7:+.3f})")
    # candidatas
    cols_s = [score_cells(earth_v, pv.loc[t], COLD_WEIGHTS, model, ref=earth_v)["score"].to_numpy() for t in t_ice]
    with np.errstate(all="ignore"):
        sc = np.nanmean(np.column_stack(cols_s), axis=1)
    kb = known_for_body(known_all, "mars")
    ok = earth_v["viable"].fillna(True).astype(bool) & ~earth_v["vegetated"].fillna(False).astype(bool)
    far = np.array([haversine_km(r.lat, r.lon, kb["lat"].to_numpy(), kb["lon"].to_numpy()).min() > 500 for r in earth_v.itertuples()])
    cand = earth_v[["cell_id", "lat", "lon"]].assign(score=sc, perprob=pe, pf3=earth_v["ice__water_frac"])
    top = pick_regions(cand[ok.to_numpy() & far].dropna(subset=["score"]), 6)
    top["fuera_capa_hielo"] = [not (r.lat < -60 or (r.lat > 66 and -75 <= r.lon <= -10 and not np.isfinite(r.perprob))) for r in top.itertuples()]
    r3 = bool((top["pf3"] == 1).all() and top["fuera_capa_hielo"].all())
    print("\nCandidatas frías con PF3:\n", top.round(3).to_string(index=False))
    print(f"R3 credibilidad: {'CUMPLE' if r3 else 'NO CUMPLE'}")
    print("VEREDICTO PREREGISTRADO:", "SE INTEGRA AL CASO FRÍO" if (r1 and r2 and r3) else "NO SE INTEGRA")
    if r1 and r2 and r3:
        append_use_case(top, earth_v, known_all, len(t_ice))
    top.round(4).to_csv(RESULTS_DIR / "permafrost_mapa_candidatas.csv", index=False)
    pd.DataFrame({"base": ub, "PF3": uv}).to_csv(RESULTS_DIR / "permafrost_mapa_analogos.csv")
    (RESULTS_DIR / "permafrost_mapa_resumen.json").write_text(json.dumps({
        "celdas_mapa": n_map, "celdas_temperatura": n_T, "ambas": agree, "R1": {"u": m1, "lo": lo1, "hi": hi1, "cumple": bool(r1)},
        "R2": {"diff": d, "lo": dlo, "hi": dhi, "cumple": bool(r2)}, "R3": r3, "integra": bool(r1 and r2 and r3), "n_frios": len(cold)}, indent=1))


if __name__ == "__main__":
    main()
