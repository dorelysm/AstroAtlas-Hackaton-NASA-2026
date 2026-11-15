"""Sensitivity of a place's rank to the model's aspects: what happens to the ranking if one aspect is ignored?

For a chosen Earth cell the ranking is recomputed with the current weights and, one at a time, with each aspect switched off.
It shows whether a place is a good analog because of everything together or because of a single aspect. The model itself does
not change: only the weights of the scenario do.
"""
import numpy as np
import pandas as pd

from .config import DIMENSIONS
from .similarity import rank_cells


def aspect_scenarios(weights: dict[str, float]) -> list[tuple[str, dict[str, float]]]:
    """[("all", weights), (dim, weights without dim), ...] for every aspect that currently counts (needs at least two)."""
    on = [d for d in DIMENSIONS if weights.get(d, 0.0) > 0]
    out = [("all", dict(weights))]
    if len(on) > 1:
        out += [(d, {**weights, d: 0.0}) for d in on]
    return out


def sensitivity(earth: pd.DataFrame, profile: pd.Series, weights: dict[str, float], topo_model, cell_id: str,
                visible_ids: set[str] | None = None) -> pd.DataFrame:
    """One row per scenario: rank of `cell_id` among the visible cells, its score, how many cells are ranked and the top cell.

    `visible_ids` restricts the ranking to the cells the user can see (after the town and vegetation filters), so the rank
    matches the one shown in the app.
    """
    rows = []
    for key, w in aspect_scenarios(weights):
        ranked = rank_cells(earth, profile, w, topo_model)
        ranked = ranked[ranked["score"].notna()]
        if visible_ids is not None:
            ranked = ranked[ranked["cell_id"].astype(str).isin(visible_ids)]
        ranked = ranked.sort_values("score", ascending=False).reset_index(drop=True)
        hit = ranked.index[ranked["cell_id"].astype(str) == str(cell_id)]
        top = ranked.iloc[0] if len(ranked) else None
        rows.append({
            "scenario": key,
            "rank": int(hit[0]) + 1 if len(hit) else np.nan,
            "score": float(ranked.loc[hit[0], "score"]) if len(hit) else np.nan,
            "n": len(ranked),
            "top_cell": str(top["cell_id"]) if top is not None else None,
            "top_lat": float(top["lat"]) if top is not None else np.nan,
            "top_lon": float(top["lon"]) if top is not None else np.nan,
        })
    return pd.DataFrame(rows)


def rank_span(table: pd.DataFrame) -> tuple[int, int]:
    """(best rank, worst rank) over all scenarios; (0, 0) if the place has no rank."""
    r = table["rank"].dropna()
    return (int(r.min()), int(r.max())) if len(r) else (0, 0)
