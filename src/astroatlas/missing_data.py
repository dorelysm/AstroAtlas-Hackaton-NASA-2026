"""Experiment: how should a cell WITHOUT data in a dimension be scored?

The published model averages each cell over the dimensions it has data for, so a gap is never penalised
(`missing="renormalize"`). The alternative scores a gap as 0 in every dimension the target can be compared on
(`missing="zero"`). Protocol and criterion: docs/preregistrations/missing-dimensions.md (DRAFT).

Two tables:
  * gap_share: how many of the top-N cells have a gap, against how many would be expected by chance.
  * compare:   how well each variant recovers the known analogs, u = P(analog > typical Earth cell), 0.5 = chance,
               computed exactly like ablation.run (the same code path and the same analog windows).

    python -m astroatlas.missing_data                 # the 10 original analogs (demo_data is enough)
    python -m astroatlas.missing_data --extended      # original + 13 new analogs (needs data/features/ from validation_ext)
    python -m astroatlas.missing_data --sites PATH --known PATH   # any other frozen set (parquet / csv)
"""
import argparse

import numpy as np
import pandas as pd

from .config import DIMENSIONS, FEATURES_DIR, RESULTS_DIR
from .features import load_features
from .similarity import MISSING_MODES, fit_topo_model, rank_cells, score_cells, site_profiles
from .validate import evaluate_sites, known_for_body, load_earth_sites, load_known

DIMS = list(DIMENSIONS)


def cells_with_gaps(earth: pd.DataFrame) -> pd.Series:
    """True for the Earth cells that lack at least one dimension (a whole dimension with no feature at all)."""
    return pd.concat([earth[feats].isna().all(axis=1) for feats in DIMENSIONS.values()], axis=1).any(axis=1)


def gap_share(earth: pd.DataFrame, profiles: pd.DataFrame, topo, n: int = 50, mode: str = "renormalize") -> pd.DataFrame:
    """Per target: gaps among the top-n cells, against the expected number if gaps did not matter."""
    gap = cells_with_gaps(earth).set_axis(earth["cell_id"])
    rows = []
    for target, profile in profiles.iterrows():
        top = rank_cells(earth, profile, None, topo, missing=mode).head(n)
        rows.append({"target": target, "mode": mode, f"gaps_in_top{n}": int(gap.reindex(top["cell_id"]).sum()),
                     "expected": round(n * float(gap.mean()), 1)})
    return pd.DataFrame(rows)


def compare(sites: pd.DataFrame, known: pd.DataFrame, features_dir=FEATURES_DIR, modes=MISSING_MODES) -> pd.DataFrame:
    """One row per (body, mode, target, analog): u = P(analog scores higher than a typical Earth cell)."""
    earth = load_features("earth", features_dir)
    topo = fit_topo_model(earth)
    rows = []
    for body in ("moon", "mars"):
        profiles = site_profiles(load_features(body, features_dir))
        known_b = known_for_body(known, body)
        sites_b = sites[sites["name"].isin(known_b["name"])].reset_index(drop=True)
        for target, profile in profiles.iterrows():
            for mode in modes:
                ranked = rank_cells(earth, profile, None, topo, missing=mode)
                sc = score_cells(sites_b, profile, None, topo, ref=earth, missing=mode).set_index("name")["score"]
                for name, pct in evaluate_sites(ranked["score"], sc)["percentile_per_known"].items():
                    rows.append({"body": body, "mode": mode, "target": target, "analog": name, "u": 1 - pct / 100})
    return pd.DataFrame(rows)


def boot_ci(v: np.ndarray, n_boot: int = 4000, seed: int = 0) -> tuple[float, float]:
    rng = np.random.default_rng(seed)
    m = [rng.choice(v, len(v)).mean() for _ in range(n_boot)]
    return float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))


def summarize(raw: pd.DataFrame, baseline: str = "renormalize") -> pd.DataFrame:
    """Mean u per mode and body (the analog is the independent unit) and the paired change against the baseline."""
    rows = []
    for body, g in raw.groupby("body"):
        per = g.groupby(["mode", "analog"])["u"].mean().unstack("mode")
        for mode in per.columns:
            v = per[mode].dropna().to_numpy()
            lo, hi = boot_ci(v)
            row = {"body": body, "mode": mode, "n_analogs": len(v), "mean_u": float(v.mean()), "ci_lo": lo, "ci_hi": hi}
            if mode != baseline and baseline in per:
                d = (per[mode] - per[baseline]).dropna().to_numpy()
                dlo, dhi = boot_ci(d)
                row |= {"change_vs_baseline": float(d.mean()), "change_ci_lo": dlo, "change_ci_hi": dhi}
            rows.append(row)
    return pd.DataFrame(rows)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--extended", action="store_true", help="use validation_ext's extended analog set")
    ap.add_argument("--sites", help="parquet with the analog windows (column `name`)")
    ap.add_argument("--known", help="csv with the analogs (columns `name`, `analog_of`)")
    a = ap.parse_args()
    if a.extended:
        from .validation_ext import extended_known, extended_sites
        sites, known = extended_sites(), extended_known()
    elif a.sites and a.known:
        sites, known = pd.read_parquet(a.sites), pd.read_csv(a.known)
    else:
        sites, known = load_earth_sites(FEATURES_DIR / "earth_sites.parquet"), load_known()

    earth = load_features("earth")
    topo = fit_topo_model(earth)
    print("Gaps among the 50 best cells (expected if gaps did not matter: "
          f"{50 * float(cells_with_gaps(earth).mean()):.1f})")
    gaps = pd.concat([gap_share(earth, site_profiles(load_features(b)), topo, mode=m) for b in ("moon", "mars")
                      for m in MISSING_MODES])
    print(gaps.pivot(index="target", columns="mode", values="gaps_in_top50").to_string())

    raw = compare(sites, known)
    out = summarize(raw)
    print("\nRecovery of the known analogs (u, 0.5 = chance)")
    print(out.round(3).to_string(index=False))
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    raw.to_csv(RESULTS_DIR / "missing_data_raw.csv", index=False)
    out.to_csv(RESULTS_DIR / "missing_data_summary.csv", index=False)
    gaps.to_csv(RESULTS_DIR / "missing_data_gaps.csv", index=False)


if __name__ == "__main__":
    main()
