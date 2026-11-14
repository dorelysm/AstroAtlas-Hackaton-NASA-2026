"""Validación contra análogos conocidos y búsqueda de candidatos nuevos.

OJO: la lista de conocidos solo se usa para VALIDAR, nunca para ajustar pesos/features
(evita validación circular).
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
    """Matriz celdas x análogos con distancia en km."""
    d = haversine_km(
        cells["lat"].to_numpy()[:, None], cells["lon"].to_numpy()[:, None],
        known["lat"].to_numpy()[None, :], known["lon"].to_numpy()[None, :],
    )
    return pd.DataFrame(d, index=cells.index, columns=known["name"])


def evaluate(ranked: pd.DataFrame, known: pd.DataFrame, radius_km: float = 300, top_pct: float = 5) -> dict:
    """AUC (celdas cerca de un conocido vs resto) y recall@top_pct.

    recall@top_pct = fracción de análogos conocidos con alguna celda (a < radius_km)
    dentro del top `top_pct`% del ranking. Solo cuentan los conocidos cubiertos por la malla.
    """
    ranked = ranked.dropna(subset=["score"]).reset_index(drop=True)
    dist = dist_to_known_km(ranked, known)
    near = dist < radius_km
    is_known = near.any(axis=1)
    auc = roc_auc_score(is_known, ranked["score"]) if 0 < is_known.sum() < len(ranked) else float("nan")

    pct = ranked["rank"] / len(ranked) * 100
    covered = near.any(axis=0)
    hits = {name: float(pct[near[name]].min()) for name in near.columns[covered]}
    recall = float(np.mean([p <= top_pct for p in hits.values()])) if hits else float("nan")
    return {
        "auc": float(auc),
        "recall_at_top_pct": recall,
        "top_pct": top_pct,
        "radius_km": radius_km,
        "n_known_covered": int(covered.sum()),
        "best_percentile_per_known": hits,
    }


def novel_candidates(ranked: pd.DataFrame, known: pd.DataFrame, min_km: float = 500, n: int = 10) -> pd.DataFrame:
    """Top-n celdas a más de `min_km` de cualquier análogo conocido."""
    ranked = ranked.dropna(subset=["score"])
    far = dist_to_known_km(ranked, known).min(axis=1) > min_km
    return ranked[far].head(n).reset_index(drop=True)
