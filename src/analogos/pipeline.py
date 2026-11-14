"""Pipeline de punta a punta: features -> scores -> validación -> resultados.

    python -m analogos.pipeline
Escribe data/results/{scores.parquet, clusters.parquet, metrics.json, candidates.csv}.
"""
import json

import pandas as pd

from .cluster import cluster_cells
from .config import RESULTS_DIR
from .features import load_features
from .similarity import rank_cells, site_profiles
from .validate import evaluate, load_known, novel_candidates


def run(top_n: int = 500, weights: dict[str, float] | None = None) -> dict:
    earth = load_features("earth")
    known = load_known()
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    all_scores, metrics, cands = [], {}, []
    for body in ("moon", "mars"):
        profiles = site_profiles(load_features(body))
        for site, profile in profiles.iterrows():
            ranked = rank_cells(earth, profile, weights)
            metrics[f"{body}/{site}"] = evaluate(ranked, known)
            top = ranked.head(top_n).assign(site=site, body=body)
            all_scores.append(top)
            cands.append(novel_candidates(ranked, known).assign(site=site, body=body))

    pd.concat(all_scores).to_parquet(RESULTS_DIR / "scores.parquet", index=False)
    pd.concat(cands).to_csv(RESULTS_DIR / "candidates.csv", index=False)
    cluster_cells(earth).to_parquet(RESULTS_DIR / "clusters.parquet", index=False)
    (RESULTS_DIR / "metrics.json").write_text(json.dumps(metrics, indent=2, ensure_ascii=False))
    return metrics


if __name__ == "__main__":
    m = run()
    for k, v in m.items():
        print(f"{k:35s} AUC={v['auc']:.2f}  recall@{v['top_pct']:.0f}%={v['recall_at_top_pct']:.2f}")
