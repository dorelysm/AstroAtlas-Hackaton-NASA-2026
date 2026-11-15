"""End-to-end pipeline: features -> scores -> validation -> results.

    python -m astroatlas.pipeline                       # topography PCA + validation by type (recommended)
    python -m astroatlas.pipeline --no-pca --all-analogs --out data/results_baseline    # comparison

Writes {scores.parquet, clusters.parquet, metrics.json, validation_summary.json, candidates.csv}.
"""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from .cluster import cluster_cells
from .config import FEATURES_DIR, RESULTS_DIR
from .features import load_features
from .similarity import fit_topo_model, rank_cells, score_cells, site_profiles
from .validate import (evaluate, evaluate_sites, known_for_body, load_earth_sites, load_known,
                       novel_candidates)


def summarize(metrics: dict) -> dict:
    """Per-body mean of the metrics of all targets (with the range, not only the mean)."""
    rows = []
    for key, m in metrics.items():
        body = key.split("/")[0]
        rows.append({"body": body, "auc_cells": m["auc"], "recall_cells": m["recall_at_top_pct"],
                     "auc_sites": m.get("sites", {}).get("auc", np.nan),
                     "recall_sites": m.get("sites", {}).get("recall_at_top_pct", np.nan)})
    df = pd.DataFrame(rows)
    out = {}
    for body, g in [("all", df), *df.groupby("body")]:
        out[body] = {"n_targets": len(g), **{
            c: {"mean": float(g[c].mean()), "min": float(g[c].min()), "max": float(g[c].max())}
            for c in ("auc_cells", "recall_cells", "auc_sites", "recall_sites")}}
    return out


VIABILITY_COLS = ["viable", "dist_settlement_km", "settlement_name", "settlement_pop", "dist_any_settlement_km",
                  "veg_ndvi_max", "vegetated"]  # context flags: they enter neither the score nor the validation


def attach_viability(df: pd.DataFrame, earth: pd.DataFrame) -> pd.DataFrame:
    """Adds to a ranking the population-viability columns (data/settlements.py), if `earth` has them.
    It is information only: it alters neither the order nor the score."""
    cols = [c for c in VIABILITY_COLS if c in earth.columns and c not in df.columns]
    return df.merge(earth[["cell_id", *cols]], on="cell_id", how="left") if cols else df


def run(top_n: int = 500, weights: dict[str, float] | None = None, compress_topo: bool = True,
        by_body: bool = True, n_boot: int = 500, features_dir: Path = FEATURES_DIR,
        results_dir: Path = RESULTS_DIR) -> dict:
    """compress_topo: whitened PCA of the topography. by_body: validate each target only with the
    analogs of its type (`analog_of`). With both False the earlier version is reproduced."""
    earth = load_features("earth", features_dir)
    known = load_known()
    earth_sites = load_earth_sites(features_dir / "earth_sites.parquet")
    topo_model = fit_topo_model(earth) if compress_topo else None
    results_dir.mkdir(parents=True, exist_ok=True)

    all_scores, metrics, cands, cands_viable, cands_short = [], {}, [], [], []
    for body in ("moon", "mars"):
        profiles = site_profiles(load_features(body, features_dir))
        known_b = known_for_body(known, body) if by_body else known
        sites_b = None
        if earth_sites is not None:
            sites_b = earth_sites[earth_sites["name"].isin(known_b["name"])].reset_index(drop=True)
        for site, profile in profiles.iterrows():
            ranked = rank_cells(earth, profile, weights, topo_model)
            m = evaluate(ranked, known_b, n_boot=n_boot)
            if sites_b is not None and len(sites_b):
                sc = score_cells(sites_b, profile, weights, topo_model, ref=earth)
                m["sites"] = evaluate_sites(ranked["score"], sc.set_index("name")["score"])
            metrics[f"{body}/{site}"] = m  # the validation uses `ranked` WITHOUT filtering by viability
            ranked_v = attach_viability(ranked, earth)
            all_scores.append(ranked_v.head(top_n).assign(site=site, body=body))
            cands.append(novel_candidates(ranked_v, known_b).assign(site=site, body=body))
            cands_viable.append(novel_candidates(ranked_v, known_b, viable_only=True).assign(site=site, body=body))
            cands_short.append(novel_candidates(ranked_v, known_b, viable_only=True, unvegetated_only=True)
                               .assign(site=site, body=body))

    pd.concat(all_scores).to_parquet(results_dir / "scores.parquet", index=False)
    pd.concat(cands).to_csv(results_dir / "candidates.csv", index=False)  # with the `viable` column
    pd.concat(cands_viable).to_csv(results_dir / "candidates_viable.csv", index=False)  # only the viable ones
    pd.concat(cands_short).to_csv(results_dir / "candidates_shortlist.csv", index=False)  # viable and non-vegetated
    cluster_cells(earth).to_parquet(results_dir / "clusters.parquet", index=False)
    (results_dir / "metrics.json").write_text(json.dumps(metrics, indent=2, ensure_ascii=False))
    summary = {"config": {"compress_topo": compress_topo, "by_body": by_body, "n_boot": n_boot,
                          "topo_components": topo_model.n_components if topo_model else None,
                          "topo_variance": float(topo_model.cum_variance[-1]) if topo_model else None},
               **summarize(metrics)}
    (results_dir / "validation_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False))
    return metrics


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-pca", action="store_true", help="do not compress the topography")
    ap.add_argument("--all-analogs", action="store_true", help="validate with all analogs, without filtering by type")
    ap.add_argument("--boot", type=int, default=500)
    ap.add_argument("--out", type=Path, default=RESULTS_DIR)
    a = ap.parse_args()
    m = run(compress_topo=not a.no_pca, by_body=not a.all_analogs, n_boot=a.boot, results_dir=a.out)
    for k, v in m.items():
        s = v.get("sites", {})
        print(f"{k:35s} celdas AUC={v['auc']:.2f}  sitios AUC={s.get('auc', float('nan')):.2f} (n={s.get('n', 0)})")
    print(json.dumps(json.loads((a.out / "validation_summary.json").read_text())["all"], indent=1)[:900])
