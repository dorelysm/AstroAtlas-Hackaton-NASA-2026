"""Similitud entre celdas terrestres y el perfil de un sitio objetivo.

Versión inicial (simple y explicable):
  - Se estandariza con media/desviación de la Tierra.
  - Distancia por dimensión = RMS de las diferencias z de sus features (ignora NaN).
  - Score por dimensión = exp(-distancia)  -> 1 = idéntico, ~0 = muy distinto.
  - Score global = media ponderada de las dimensiones disponibles.
Mejora prevista: Mahalanobis/Gower (PLAN.md, sección 3).
"""
import numpy as np
import pandas as pd

from .config import DEFAULT_WEIGHTS, DIMENSIONS, FEATURES


def earth_stats(earth: pd.DataFrame) -> tuple[pd.Series, pd.Series]:
    mu = earth[FEATURES].mean()
    sd = earth[FEATURES].std().replace(0, 1).fillna(1)
    return mu, sd


def site_profiles(target: pd.DataFrame) -> pd.DataFrame:
    """Perfil (media de sus celdas) por sitio. Índice = nombre del sitio."""
    return target.groupby("site")[FEATURES].mean()


def dimension_scores(earth: pd.DataFrame, profile: pd.Series) -> pd.DataFrame:
    """Score 0-1 por dimensión para cada celda de la Tierra."""
    mu, sd = earth_stats(earth)
    z_earth = (earth[FEATURES] - mu) / sd
    z_site = (profile[FEATURES].astype(float) - mu) / sd
    out = {}
    for dim, feats in DIMENSIONS.items():
        diff = z_earth[feats] - z_site[feats]
        dist = np.sqrt(diff.pow(2).mean(axis=1, skipna=True))
        out[dim] = np.exp(-dist)
    return pd.DataFrame(out, index=earth.index)


def global_score(dim_scores: pd.DataFrame, weights: dict[str, float] | None = None) -> pd.Series:
    w = pd.Series({**DEFAULT_WEIGHTS, **(weights or {})})[dim_scores.columns]
    valid = dim_scores.notna()
    num = (dim_scores.fillna(0) * w).sum(axis=1)
    den = (valid * w).sum(axis=1)
    return (num / den.where(den > 0)).rename("score")


def rank_cells(
    earth: pd.DataFrame, profile: pd.Series, weights: dict[str, float] | None = None
) -> pd.DataFrame:
    """Devuelve las celdas con scores por dimensión, score global y ranking (1 = mejor)."""
    dims = dimension_scores(earth, profile)
    score = global_score(dims, weights)
    out = pd.concat([earth[["cell_id", "lat", "lon"]], dims, score], axis=1)
    out["rank"] = out["score"].rank(ascending=False, method="min")
    return out.sort_values("rank").reset_index(drop=True)
