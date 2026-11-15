"""Per-dimension ablation: which of topo / thermal / ice / geo carry signal for recovering the known analogs?

For every Moon and Mars target the Earth is scored with: all dimensions, ONE dimension only, and ALL BUT one.
Metric: u = P(score of a known analog > score of a cell of the Earth grid) (0.5 = chance), with the
analogs computed over the same 50 km windows as the targets (evaluate_sites in validate.py).

STATISTICAL NOTE: all targets of one body are evaluated against THE SAME analogs (4 to 8). The independent
unit is the analog, not the target. Intervals come from a bootstrap over the ANALOGS.

    python -m astroatlas.ablation
"""
import argparse
import json
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

from .config import DIMENSIONS, FEATURES_DIR, RESULTS_DIR
from .features import load_features
from .similarity import fit_topo_model, rank_cells, score_cells, site_profiles
from .validate import evaluate, evaluate_sites, known_for_body, load_earth_sites, load_known

DIMS = list(DIMENSIONS)


def weights_only(dim: str) -> dict[str, float]:
    return {d: 1.0 if d == dim else 0.0 for d in DIMS}


def weights_without(dim: str) -> dict[str, float]:
    return {d: 0.0 if d == dim else 1.0 for d in DIMS}


def configs() -> dict[str, dict[str, float]]:
    out = {"all": {d: 1.0 for d in DIMS}}
    out |= {f"only {d}": weights_only(d) for d in DIMS}
    out |= {f"without {d}": weights_without(d) for d in DIMS}
    return out


def run(features_dir: Path = FEATURES_DIR, compress_topo: bool = True) -> pd.DataFrame:
    """One row per (target, configuration, analog): u = P(analog > typical cell)."""
    earth = load_features("earth", features_dir)
    sites = load_earth_sites(features_dir / "earth_sites.parquet")
    if sites is None:
        raise FileNotFoundError("Falta earth_sites.parquet (python -m astroatlas.data.earth)")
    known = load_known()
    topo = fit_topo_model(earth) if compress_topo else None
    rows = []
    for body in ("moon", "mars"):
        profiles = site_profiles(load_features(body, features_dir))
        known_b = known_for_body(known, body)
        sites_b = sites[sites["name"].isin(known_b["name"])].reset_index(drop=True)
        for target, profile in profiles.iterrows():
            for cfg, w in configs().items():
                ranked = rank_cells(earth, profile, w, topo)
                sc = score_cells(sites_b, profile, w, topo, ref=earth).set_index("name")["score"]
                ms = evaluate_sites(ranked["score"], sc)
                auc_cells = evaluate(ranked, known_b)["auc"]
                for name, pct in ms["percentile_per_known"].items():
                    rows.append({"body": body, "target": target, "config": cfg, "analog": name,
                                 "u": 1 - pct / 100, "auc_cells": auc_cells})
    return pd.DataFrame(rows)


def _boot_ci(mat: np.ndarray, n_boot: int, rng) -> tuple[float, float]:
    """95 % CI of the mean of `mat` (targets x analogs), resampling the COLUMNS (analogs)."""
    if mat.shape[1] < 2:
        return float("nan"), float("nan")
    means = [np.nanmean(mat[:, rng.integers(0, mat.shape[1], mat.shape[1])]) for _ in range(n_boot)]
    return float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))


def summarize(df: pd.DataFrame, n_boot: int = 2000, seed: int = 0) -> pd.DataFrame:
    """Per body and configuration: mean u, bootstrap CI over analogs and paired difference against 'all'."""
    rng = np.random.default_rng(seed)
    out = []
    for body, g in df.groupby("body"):
        cube = {cfg: c.pivot(index="target", columns="analog", values="u") for cfg, c in g.groupby("config")}
        base = cube["all"]
        for cfg, mat in cube.items():
            m = mat.reindex(index=base.index, columns=base.columns).to_numpy()
            lo, hi = _boot_ci(m, n_boot, rng)
            d = m - base.to_numpy()
            dlo, dhi = _boot_ci(d, n_boot, rng) if cfg != "all" else (float("nan"), float("nan"))
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", RuntimeWarning)  # columns with no data at all (e.g. Mars thermal)
                per_analog = np.nanmean(m, axis=0)
            out.append({"body": body, "config": cfg, "n_targets": int(np.isfinite(m).any(axis=1).sum()),
                        "n_analogs": m.shape[1], "u_mean": float(np.nanmean(m)), "ci_lo": lo, "ci_hi": hi,
                        "delta_vs_all": float(np.nanmean(d)) if cfg != "all" else 0.0, "delta_lo": dlo,
                        "delta_hi": dhi, "share_analogs_above_0.5": float(np.mean(per_analog > 0.5))})
    return pd.DataFrame(out)


def per_analog_table(df: pd.DataFrame) -> pd.DataFrame:
    """Mean u of each analog (averaged over the body's targets) per configuration."""
    return df.groupby(["body", "config", "analog"])["u"].mean().unstack("analog").round(2)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--boot", type=int, default=2000)
    ap.add_argument("--no-pca", action="store_true")
    ap.add_argument("--out", type=Path, default=RESULTS_DIR)
    a = ap.parse_args()
    df = run(compress_topo=not a.no_pca)
    summ = summarize(df, a.boot)
    a.out.mkdir(parents=True, exist_ok=True)
    df.to_csv(a.out / "ablation_raw.csv", index=False)
    summ.to_csv(a.out / "ablation_summary.csv", index=False)
    (a.out / "ablation_summary.json").write_text(json.dumps(summ.round(4).to_dict("records"), indent=2, ensure_ascii=False))
    pd.set_option("display.width", 220)
    for body, g in summ.groupby("body"):
        print(f"\n=== {body}: {g['n_targets'].max()} objetivos x {g['n_analogs'].iloc[0]} analogs (u=0.5 is chance)")
        print(g[["config", "n_targets", "u_mean", "ci_lo", "ci_hi", "delta_vs_all", "delta_lo", "delta_hi"]]
              .round(2).to_string(index=False))


if __name__ == "__main__":
    main()
