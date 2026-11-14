"""Fichas "qué se parece / qué no / límites" por celda candidata."""
import pandas as pd

from .config import DIMENSIONS, LIMITS


def ficha(row: pd.Series, site: str, body: str, strong: float = 0.7, weak: float = 0.4) -> dict:
    scores = {d: float(row[d]) for d in DIMENSIONS if pd.notna(row.get(d))}
    return {
        "site": site,
        "body": body,
        "cell_id": row["cell_id"],
        "lat": float(row["lat"]),
        "lon": float(row["lon"]),
        "score": float(row["score"]),
        "rank": int(row["rank"]),
        "similar": sorted(d for d, s in scores.items() if s >= strong),
        "different": sorted(d for d, s in scores.items() if s < weak),
        "no_data": sorted(d for d in DIMENSIONS if d not in scores),
        "scores": scores,
        "limits": LIMITS.get(body, []),
        # TODO(equipo): uso para la exploración (instrumentos, ISRU, entrenamiento...)
    }
