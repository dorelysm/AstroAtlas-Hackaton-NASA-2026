"""Validación del aspecto TOPOGRAFÍA con la capa de sitios análogos del USGS frente a un control de puntos aleatorios.

Protocolo fijado antes de calcular ningún score: docs/VALIDACION_ASPECTO.md ("Protocolo con la capa del USGS").
Pregunta: ¿los cráteres de impacto (y las dunas) puntúan, con la topografía SOLA, más que puntos aleatorios de tierra firme?
La comparación contra el control separa "cráter" de "terreno llano y estable" (los cráteres se conservan en cratones).

    python -m analogos.aspect_usgs
"""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu

from .ablation import weights_only
from .config import FEATURES_DIR, RESULTS_DIR
from .features import load_features
from .similarity import fit_topo_model, rank_cells, score_cells, site_profiles


def u_of_sites(sites: pd.DataFrame, earth: pd.DataFrame, profile: pd.Series, topo_model) -> np.ndarray:
    """u de cada sitio = P(score del sitio > score de una celda de la malla), con la topografía sola."""
    w = weights_only("topo")
    cells = rank_cells(earth, profile, w, topo_model)["score"].dropna().to_numpy()
    sc = score_cells(sites, profile, w, topo_model, ref=earth)["score"].to_numpy()
    return np.array([(cells < s).mean() + 0.5 * (cells == s).mean() if np.isfinite(s) else np.nan for s in sc])


def mean_u_per_site(sites: pd.DataFrame, body: str, features_dir: Path = FEATURES_DIR, topo_model=None) -> pd.Series:
    earth = load_features("earth", features_dir)
    topo_model = fit_topo_model(earth) if topo_model is None else topo_model
    cols = [u_of_sites(sites, earth, prof, topo_model) for _, prof in site_profiles(load_features(body, features_dir)).iterrows()]
    return pd.Series(np.nanmean(np.vstack(cols), axis=0), index=sites.index)


def auc_rank(pos: np.ndarray, ctrl: np.ndarray) -> float:
    """P(u de un positivo > u de un control), con 0.5 en los empates."""
    d = np.asarray(pos)[:, None] - np.asarray(ctrl)[None, :]
    return float(((d > 0) + 0.5 * (d == 0)).mean())


def compare(pos: np.ndarray, ctrl: np.ndarray, n_boot: int = 2000, seed: int = 0) -> dict:
    pos, ctrl = np.asarray(pos, float), np.asarray(ctrl, float)
    pos, ctrl = pos[np.isfinite(pos)], ctrl[np.isfinite(ctrl)]
    if len(pos) < 2 or len(ctrl) < 2:
        return {"n_pos": len(pos), "n_ctrl": len(ctrl), "auc_rank": np.nan, "estado": "no evaluable"}
    rng = np.random.default_rng(seed)
    boots = [auc_rank(rng.choice(pos, len(pos)), rng.choice(ctrl, len(ctrl))) for _ in range(n_boot)]
    p = float(mannwhitneyu(pos, ctrl, alternative="greater").pvalue)
    lo, hi = float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))
    return {"n_pos": len(pos), "n_ctrl": len(ctrl), "u_pos": float(pos.mean()), "u_ctrl": float(ctrl.mean()),
            "share_pos_above_half": float((pos > 0.5).mean()), "share_ctrl_above_half": float((ctrl > 0.5).mean()),
            "auc_rank": auc_rank(pos, ctrl), "ci_lo": lo, "ci_hi": hi, "p_mannwhitney": p,
            "senal": bool(lo > 0.5), "estado": "ok"}


def run(features_dir: Path = FEATURES_DIR, n_boot: int = 2000) -> pd.DataFrame:
    sites = pd.read_parquet(features_dir / "earth_usgs.parquet")
    rows = []
    for body in ("moon", "mars"):
        u = mean_u_per_site(sites, body, features_dir)
        pos = sites["group"].isin(["crater", "dunes"]).to_numpy()
        ctrl = (sites["group"] == "control").to_numpy()
        for label, mask in (("topografía (cráteres + dunas)", pos), ("solo cráteres", (sites["group"] == "crater").to_numpy())):
            rows.append({"body": body, "positivos": label, **compare(u[mask].to_numpy(), u[ctrl].to_numpy(), n_boot)})
        for name, g in sites[sites["group"].isin(["volcanic", "dunes"])].iterrows():
            rows.append({"body": body, "positivos": f"informativo: {g['name']} ({g['group']})", "n_pos": 1,
                         "u_pos": float(u[name]), "estado": "n = 1, solo informativo"})
    return pd.DataFrame(rows)


def compare_stratified(u: np.ndarray, pos: np.ndarray, ctrl: np.ndarray, control_var: np.ndarray, n_bins: int = 5,
                       min_n: int = 3, n_boot: int = 2000, seed: int = 0) -> dict:
    """AUC cráter > control DENTRO de estratos de `control_var` (p. ej. la pendiente media), ponderado por n_pos*n_ctrl.
    Separa "es un cráter" de "es terreno igual de llano que los cráteres". Protocolo: docs/PREREGISTRO_LLANURA.md."""
    u, cv = np.asarray(u, float), np.asarray(control_var, float)
    ok = np.isfinite(u) & np.isfinite(cv) & (np.asarray(pos) | np.asarray(ctrl))
    edges = np.quantile(cv[ok], np.linspace(0, 1, n_bins + 1))
    bins = np.clip(np.searchsorted(edges, cv, side="right") - 1, 0, n_bins - 1)
    strata = []
    for b in range(n_bins):
        p, c = u[ok & (bins == b) & pos], u[ok & (bins == b) & ctrl]
        if len(p) >= min_n and len(c) >= min_n:
            strata.append((p, c))
    if not strata:
        return {"estado": "no evaluable", "n_strata": 0}
    w = np.array([len(p) * len(c) for p, c in strata], float)

    def agg(sets):
        return float(np.average([auc_rank(p, c) for p, c in sets], weights=w))

    rng = np.random.default_rng(seed)
    boots = [agg([(rng.choice(p, len(p)), rng.choice(c, len(c))) for p, c in strata]) for _ in range(n_boot)]
    lo, hi = float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))
    return {"estado": "ok", "n_strata": len(strata), "n_pos": int(sum(len(p) for p, _ in strata)),
            "n_ctrl": int(sum(len(c) for _, c in strata)), "auc_estratificado": agg(strata), "ci_lo": lo, "ci_hi": hi,
            "senal": bool(lo > 0.5)}


def run_stratified(features_dir: Path = FEATURES_DIR, n_boot: int = 2000) -> pd.DataFrame:
    sites = pd.read_parquet(features_dir / "earth_usgs.parquet")
    pos = sites["group"].isin(["crater", "dunes"]).to_numpy()
    ctrl = (sites["group"] == "control").to_numpy()
    rows = []
    for body in ("moon", "mars"):
        u = mean_u_per_site(sites, body, features_dir).to_numpy()
        rows.append({"body": body, **compare_stratified(u, pos, ctrl, sites["topo__slope_mean_deg"].to_numpy(), n_boot=n_boot)})
    return pd.DataFrame(rows)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--boot", type=int, default=2000)
    ap.add_argument("--out", type=Path, default=RESULTS_DIR)
    a = ap.parse_args()
    res = run(n_boot=a.boot)
    a.out.mkdir(parents=True, exist_ok=True)
    res.to_csv(a.out / "aspect_usgs.csv", index=False)
    (a.out / "aspect_usgs.json").write_text(json.dumps(res.round(4).to_dict("records"), indent=2, ensure_ascii=False, default=str))
    pd.set_option("display.width", 220)
    print(res.round(3).to_string(index=False))
    strat = run_stratified(n_boot=a.boot)
    strat.to_csv(a.out / "aspect_usgs_estratificado.csv", index=False)
    print("\nEstratificado por pendiente media (docs/PREREGISTRO_LLANURA.md):")
    print(strat.round(3).to_string(index=False))


if __name__ == "__main__":
    main()
