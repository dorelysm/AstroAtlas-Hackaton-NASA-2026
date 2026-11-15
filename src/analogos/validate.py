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


def known_for_body(known: pd.DataFrame, body: str | None) -> pd.DataFrame:
    """Análogos conocidos que sirven para `body` ('moon' o 'mars') según la columna `analog_of`
    ('moon', 'mars' o 'moon+mars'). Un objetivo de Marte no debe puntuar a Mauna Kea.
    Sin `body` o sin la columna, devuelve todos."""
    if body is None or "analog_of" not in known.columns:
        return known
    return known[known["analog_of"].fillna("").str.contains(body)].reset_index(drop=True)


def load_earth_sites(path=None) -> pd.DataFrame | None:
    """Features de los análogos conocidos calculadas con las MISMAS ventanas de 50 km que los
    objetivos (data/features/earth_sites.parquet). None si no existe."""
    from .config import FEATURES_DIR

    path = path or FEATURES_DIR / "earth_sites.parquet"
    return pd.read_parquet(path) if path.exists() else None


def evaluate(ranked: pd.DataFrame, known: pd.DataFrame, radius_km: float = 300, top_pct: float = 5,
             body: str | None = None, n_boot: int = 0, seed: int = 0) -> dict:
    """AUC (celdas cerca de un conocido vs resto) y recall@top_pct.

    recall@top_pct = fracción de análogos conocidos con alguna celda (a < radius_km)
    dentro del top `top_pct`% del ranking. Solo cuentan los conocidos cubiertos por la malla.

    body: si se indica ('moon'/'mars'), solo cuentan los análogos de ese tipo (`analog_of`).
    n_boot > 0: intervalo de confianza al 95 % remuestreando los análogos conocidos (hay muy pocos).
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
    """Validación sin la malla gruesa: ¿puntúan los propios sitios análogos más que una celda típica?

    cell_scores: score de todas las celdas de la Tierra. site_scores: score de cada análogo conocido
    (índice = nombre), calculado con ventanas de 50 km. auc = P(score del análogo > score de una celda)
    promediado sobre los análogos; percentil = % de celdas que puntúan igual o más que el análogo.
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
                     viable_only: bool = False) -> pd.DataFrame:
    """Top-n celdas a más de `min_km` de cualquier análogo conocido.

    viable_only: descarta las celdas marcadas como inviables por cercanía a población (columna `viable`, ver
    data/settlements.py). Solo es para buscar candidatos nuevos; la VALIDACIÓN no se filtra."""
    ranked = ranked.dropna(subset=["score"])
    if viable_only and "viable" in ranked:
        ranked = ranked[ranked["viable"].fillna(True).astype(bool)]
    far = dist_to_known_km(ranked, known).min(axis=1) > min_km
    return ranked[far].head(n).reset_index(drop=True)
