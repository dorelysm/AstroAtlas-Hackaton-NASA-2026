"""Modelo de análogos Tierra-Tierra (E1) y consenso entre modelos (E2): docs/PREREGISTRO_MODELOS.md.

E1: cada celda se puntúa por su parecido con los análogos conocidos del cuerpo (máximo sobre las referencias), todo con variables
terrestres. Evaluación dejando fuera uno (y a los análogos a < 500 km). E2: consenso = mínimo de los percentiles del modelo A (parecido con
los objetivos de la Luna o Marte) y del modelo B.

    python -m analogos.modelos
"""
import numpy as np
import pandas as pd

from .config import DIMENSIONS, FEATURES, FEATURES_DIR, RESULTS_DIR
from .features import load_features
from .grupos import COLD_TMAX_K
from .similarity import fit_topo_model, score_cells, site_profiles
from .usecases import pick_regions
from .validate import haversine_km, known_for_body
from .validation_ext import boot_mean, extended_known, extended_sites

EXCLUDE_KM = 500.0
WEIGHTS = {d: 1.0 for d in DIMENSIONS}


def percentile_below(values: np.ndarray, x: float) -> float:
    """Fracción de `values` por debajo de x (los empates cuentan la mitad); NaN si x es NaN."""
    v = values[np.isfinite(values)]
    if not np.isfinite(x) or len(v) == 0:
        return float("nan")
    return float(((v < x).sum() + 0.5 * (v == x).sum()) / len(v))


def rank_pct(values: np.ndarray) -> np.ndarray:
    """Percentil (0-1) de cada valor entre todos (empates: mitad); NaN se queda NaN."""
    v = np.asarray(values, dtype=float)
    out = np.full(len(v), np.nan)
    ok = np.isfinite(v)
    s = np.sort(v[ok])
    out[ok] = (np.searchsorted(s, v[ok], side="left") + np.searchsorted(s, v[ok], side="right")) / (2 * len(s))
    return out


def similarity_matrix(cells: pd.DataFrame, refs: pd.DataFrame, earth: pd.DataFrame, topo) -> np.ndarray:
    """(celdas x referencias): puntaje global de cada celda con el perfil terrestre de cada referencia."""
    cols = [score_cells(cells, r[FEATURES].astype(float), WEIGHTS, topo, ref=earth)["score"].to_numpy() for _, r in refs.iterrows()]
    return np.column_stack(cols)


def max_over(S: np.ndarray, idx: list[int]) -> np.ndarray:
    if not idx:
        return np.full(S.shape[0], np.nan)
    with np.errstate(all="ignore"):
        return np.nanmax(S[:, idx], axis=1)


def model_a(earth: pd.DataFrame, sites: pd.DataFrame, target: pd.DataFrame, topo) -> tuple[np.ndarray, np.ndarray]:
    """A(c) = media del puntaje global sobre los objetivos del cuerpo; para las celdas y para los sitios análogos."""
    prof = site_profiles(target)
    cells = np.column_stack([score_cells(earth, p, WEIGHTS, topo, ref=earth)["score"].to_numpy() for _, p in prof.iterrows()])
    sit = np.column_stack([score_cells(sites, p, WEIGHTS, topo, ref=earth)["score"].to_numpy() for _, p in prof.iterrows()])
    with np.errstate(all="ignore"):
        return np.nanmean(cells, axis=1), np.nanmean(sit, axis=1)


def evaluate_body(body: str, earth, sites, known, topo) -> pd.DataFrame:
    target = load_features(body, FEATURES_DIR)
    kb = known_for_body(known, body)
    names = list(kb["name"])
    s = sites.set_index("name").loc[names].reset_index()
    pos = kb.set_index("name").loc[names][["lat", "lon"]].reset_index()
    S_cells = similarity_matrix(earth, s, earth, topo)   # celdas x referencias
    S_sites = similarity_matrix(s, s, earth, topo)       # sitios x referencias
    A_cells, A_sites = model_a(earth, s, target, topo)
    PA_cells = rank_pct(A_cells)
    rows = []
    for i, name in enumerate(names):
        d = haversine_km(pos.loc[i, "lat"], pos.loc[i, "lon"], pos["lat"].to_numpy(), pos["lon"].to_numpy())
        refs = [j for j in range(len(names)) if j != i and d[j] >= EXCLUDE_KM]
        b_cells, b_site = max_over(S_cells, refs), max_over(S_sites[[i]], refs)[0]
        pb_cells = rank_pct(b_cells)
        pa_site, pb_site = percentile_below(A_cells, A_sites[i]), percentile_below(b_cells, b_site)
        cons_cells = np.fmin(PA_cells, pb_cells)
        union_cells = np.fmax(PA_cells, pb_cells)   # EXPLORATORIO (no preregistrado): buena en cualquiera de los dos modelos
        rows.append({"body": body, "analog": name, "n_refs": len(refs), "P_A": pa_site, "u_B": pb_site,
                     "u_consenso": percentile_below(cons_cells, np.fmin(pa_site, pb_site)),
                     "u_union_exploratorio": percentile_below(union_cells, np.fmax(pa_site, pb_site)),
                     "frio": bool(s.loc[i, "thermal__t_max_k"] < COLD_TMAX_K)})
    return pd.DataFrame(rows)


def candidates(body: str, earth, sites, known, topo, n: int = 6) -> pd.DataFrame:
    """Celdas de mayor consenso con TODAS las referencias (solo para proponer candidatas, no para evaluar)."""
    target = load_features(body, FEATURES_DIR)
    kb = known_for_body(known, body)
    s = sites.set_index("name").loc[list(kb["name"])].reset_index()
    A_cells, _ = model_a(earth, s, target, topo)
    B = max_over(similarity_matrix(earth, s, earth, topo), list(range(len(s))))
    cons = np.fmin(rank_pct(A_cells), rank_pct(B))
    df = earth[["cell_id", "lat", "lon"]].assign(P_A=rank_pct(A_cells), P_B=rank_pct(B), score=cons)
    ok = earth["viable"].fillna(True).astype(bool) & ~earth["vegetated"].fillna(False).astype(bool)
    far = np.array([haversine_km(r.lat, r.lon, kb["lat"].to_numpy(), kb["lon"].to_numpy()).min() > 500 for r in df.itertuples()])
    top = pick_regions(df[ok.to_numpy() & far].dropna(subset=["score"]), n)
    return top.assign(body=body)


def summarize(res: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for body, g in res.groupby("body"):
        for label, sel in (("todos", g), ("fríos", g[g["frio"]]), ("cálidos", g[~g["frio"]])):
            for col in ("P_A", "u_B", "u_consenso", "u_union_exploratorio"):
                m, lo, hi = boot_mean(sel[col].to_numpy())
                rows.append({"body": body, "grupo": label, "modelo": col, "n": int(sel[col].notna().sum()), "u_medio": m, "ic_lo": lo, "ic_hi": hi})
            for col in ("u_B", "u_consenso", "u_union_exploratorio"):
                m, lo, hi = boot_mean((sel[col] - sel["P_A"]).dropna().to_numpy())
                rows.append({"body": body, "grupo": label, "modelo": f"{col} − P_A", "n": int(sel[col].notna().sum()), "u_medio": m, "ic_lo": lo, "ic_hi": hi})
    return pd.DataFrame(rows)


def main() -> None:
    earth = load_features("earth", FEATURES_DIR)
    topo = fit_topo_model(earth)
    sites, known = extended_sites(), extended_known()
    res = pd.concat([evaluate_body(b, earth, sites, known, topo) for b in ("moon", "mars")], ignore_index=True)
    summ = summarize(res)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    res.round(4).to_csv(RESULTS_DIR / "modelos_por_analogo.csv", index=False)
    summ.round(4).to_csv(RESULTS_DIR / "modelos_resumen.csv", index=False)
    cand = pd.concat([candidates(b, earth, sites, known, topo) for b in ("mars", "moon")])
    cand.round(4).to_csv(RESULTS_DIR / "modelos_candidatas_consenso.csv", index=False)
    pd.set_option("display.width", 220)
    print(summ[summ["grupo"] == "todos"].round(3).to_string(index=False))
    print("\nPor grupo (modelo B y consenso):")
    print(summ[(summ["grupo"] != "todos") & summ["modelo"].isin(["P_A", "u_B", "u_consenso", "u_union_exploratorio"])].round(3).to_string(index=False))
    print("\nPor análogo (Marte):")
    print(res[res["body"] == "mars"].sort_values("u_B", ascending=False).round(2).to_string(index=False))
    print("\nCandidatas de consenso:")
    print(cand[["body", "cell_id", "lat", "lon", "P_A", "P_B", "score"]].round(3).to_string(index=False))


if __name__ == "__main__":
    main()
