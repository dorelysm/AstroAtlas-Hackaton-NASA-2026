"""Validation against known analogs and search for new candidates.

NOTE: the list of known analogs is used only to VALIDATE, never to fit weights/features
(avoids circular validation).
"""
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

from .config import KNOWN_CSV


def haversine_km(lat1, lon1, lat2, lon2) -> np.ndarray:
    lat1, lon1, lat2, lon2 = map(np.radians, (lat1, lon1, lat2, lon2))
    a = np.sin((lat2 - lat1) / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin((lon2 - lon1) / 2) ** 2
    return 6371.0 * 2 * np.arcsin(np.sqrt(a))


def load_known(path=KNOWN_CSV) -> pd.DataFrame:
    return pd.read_csv(path)


def dist_to_known_km(cells: pd.DataFrame, known: pd.DataFrame) -> pd.DataFrame:
    """Cells x analogs matrix with the distance in km."""
    d = haversine_km(
        cells["lat"].to_numpy()[:, None], cells["lon"].to_numpy()[:, None],
        known["lat"].to_numpy()[None, :], known["lon"].to_numpy()[None, :],
    )
    return pd.DataFrame(d, index=cells.index, columns=known["name"])


def known_for_body(known: pd.DataFrame, body: str | None) -> pd.DataFrame:
    """Known analogs that serve `body` ('moon' or 'mars') according to the `analog_of` column
    ('moon', 'mars' or 'moon+mars'). A Mars target must not score Mauna Kea.
    Without `body` or without the column, returns all of them."""
    if body is None or "analog_of" not in known.columns:
        return known
    return known[known["analog_of"].fillna("").str.contains(body)].reset_index(drop=True)


def load_earth_sites(path=None) -> pd.DataFrame | None:
    """Features of the known analogs computed with the SAME 50 km windows as the
    targets (data/features/earth_sites.parquet). None if it does not exist."""
    from .config import FEATURES_DIR

    path = path or FEATURES_DIR / "earth_sites.parquet"
    return pd.read_parquet(path) if path.exists() else None


def evaluate(ranked: pd.DataFrame, known: pd.DataFrame, radius_km: float = 300, top_pct: float = 5,
             body: str | None = None, n_boot: int = 0, seed: int = 0) -> dict:
    """AUC (cells near a known analog vs the rest) and recall@top_pct.

    recall@top_pct = fraction of known analogs with some cell (within < radius_km)
    inside the top `top_pct`% of the ranking. Only known analogs covered by the grid count.

    body: if given ('moon'/'mars'), only the analogs of that type (`analog_of`) count.
    n_boot > 0: 95 % confidence interval resampling the known analogs (there are very few).
    """
    known = known_for_body(known, body)
    ranked = ranked.dropna(subset=["score"]).reset_index(drop=True)
    empty = {"auc": float("nan"), "recall_at_top_pct": float("nan"), "top_pct": top_pct, "radius_km": radius_km,
             "n_known_covered": 0, "n_known": len(known), "best_percentile_per_known": {}}
    if known.empty or ranked.empty:
        return empty
    near = dist_to_known_km(ranked, known) < radius_km
    is_known = near.any(axis=1)
    auc = roc_auc_score(is_known, ranked["score"]) if 0 < is_known.sum() < len(ranked) else float("nan")

    pct = ranked["rank"] / len(ranked) * 100
    covered = near.any(axis=0)
    hits = {name: float(pct[near[name]].min()) for name in near.columns[covered]}
    recall = float(np.mean([p <= top_pct for p in hits.values()])) if hits else float("nan")
    out = {**empty, "auc": float(auc), "recall_at_top_pct": recall,
           "n_known_covered": int(covered.sum()), "best_percentile_per_known": hits}

    if n_boot > 0:
        rng = np.random.default_rng(seed)
        nm, score = near.to_numpy(), ranked["score"].to_numpy()
        best = np.array([hits.get(n, np.nan) for n in near.columns])
        aucs, recalls = [], []
        for _ in range(n_boot):
            idx = rng.integers(0, nm.shape[1], nm.shape[1])
            y = nm[:, idx].any(axis=1)
            if 0 < y.sum() < len(y):
                aucs.append(roc_auc_score(y, score))
            b = best[idx][~np.isnan(best[idx])]
            if len(b):
                recalls.append(np.mean(b <= top_pct))
        ci = lambda v: [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))] if v else [float("nan")] * 2
        out.update(auc_ci=ci(aucs), recall_ci=ci(recalls), n_boot=n_boot)
    return out


def evaluate_sites(cell_scores, site_scores: pd.Series, top_pct: float = 5) -> dict:
    """Validation without the coarse grid: do the analog sites themselves score higher than a typical cell?

    cell_scores: score of all Earth cells. site_scores: score of each known analog
    (index = name), computed with 50 km windows. auc = P(analog score > cell score)
    averaged over the analogs; percentile = % of cells that score equal to or higher than the analog.
    """
    cells = np.asarray(pd.Series(cell_scores).dropna(), dtype=float)
    sites = site_scores.dropna()
    if len(cells) == 0 or sites.empty:
        return {"auc": float("nan"), "recall_at_top_pct": float("nan"), "top_pct": top_pct, "n": 0,
                "percentile_per_known": {}}
    auc = [float((cells < s).mean() + 0.5 * (cells == s).mean()) for s in sites]
    pct = {name: float((cells >= s).mean() * 100) for name, s in sites.items()}
    return {"auc": float(np.mean(auc)), "recall_at_top_pct": float(np.mean([p <= top_pct for p in pct.values()])),
            "top_pct": top_pct, "n": len(sites), "percentile_per_known": pct}


def novel_candidates(ranked: pd.DataFrame, known: pd.DataFrame, min_km: float = 500, n: int = 10,
                     viable_only: bool = False, unvegetated_only: bool = False) -> pd.DataFrame:
    """Top-n cells farther than `min_km` from any known analog.

    viable_only: drops cells flagged as not viable because of proximity to population (`viable` column, see
    data/settlements.py). unvegetated_only: drops cells with vegetation (`vegetated` column, maximum NDVI >= 0.2, see
    data/earth_vegetation.py); with no data it is not dropped. It is only for finding new candidates; the VALIDATION is not filtered."""
    ranked = ranked.dropna(subset=["score"])
    if viable_only and "viable" in ranked:
        ranked = ranked[ranked["viable"].fillna(True).astype(bool)]
    if unvegetated_only and "vegetated" in ranked:
        ranked = ranked[~ranked["vegetated"].fillna(False).astype(bool)]
    far = dist_to_known_km(ranked, known).min(axis=1) > min_km
    return ranked[far].head(n).reset_index(drop=True)
