"""Similitud entre celdas terrestres y el perfil de un sitio objetivo.

  - Se estandariza con media/desviación de la Tierra.
  - Distancia por dimensión = RMS de las diferencias z de sus features (ignora NaN).
  - Topografía (opcional, recomendado): sus 16 variables están muy correlacionadas (|r| medio ~0.74,
    3 componentes explican ~90 % de la varianza), así que contarían doble. `fit_topo_model` las resume
    en pocas componentes principales BLANQUEADAS (varianza 1 cada una) y la distancia se mide ahí.
    Equivale a una distancia de Mahalanobis restringida al subespacio principal.
  - Score por dimensión = exp(-distancia)  -> 1 = idéntico, ~0 = muy distinto.
  - Score global = media ponderada de las dimensiones disponibles.
"""
from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA

from .config import DEFAULT_WEIGHTS, DIMENSIONS, FEATURES


@dataclass
class TopoModel:
    """PCA blanqueada de la topografía, ajustada SOLO con celdas de la Tierra."""
    features: list[str]
    mu: pd.Series
    sd: pd.Series
    components: np.ndarray  # (k, p)
    scale: np.ndarray       # desviación estándar de cada componente (para blanquear)
    cum_variance: np.ndarray

    @property
    def n_components(self) -> int:
        return len(self.scale)

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Componentes blanqueadas; NaN en las filas con alguna variable topográfica sin dato
        (no se imputa en silencio)."""
        z = ((df[self.features] - self.mu) / self.sd).to_numpy(dtype=float)
        with np.errstate(invalid="ignore"):
            pcs = (z @ self.components.T) / self.scale
        pcs[np.isnan(z).any(axis=1)] = np.nan
        return pd.DataFrame(pcs, index=df.index, columns=[f"pc{i + 1}" for i in range(self.n_components)])


def fit_topo_model(ref: pd.DataFrame, variance: float = 0.90, max_components: int = 6,
                   features: list[str] | None = None) -> TopoModel:
    """Ajusta la PCA con las filas de `ref` que tienen toda la topografía; guarda las componentes
    mínimas que explican `variance` de la varianza (máx. `max_components`)."""
    feats = list(features or DIMENSIONS["topo"])
    X = ref[feats].dropna()
    if len(X) < len(feats) + 2:
        raise ValueError(f"Hay {len(X)} filas con topografía completa; se necesitan más de {len(feats) + 1}")
    mu, sd = X.mean(), X.std().replace(0, 1).fillna(1)
    pca = PCA().fit((X - mu) / sd)
    cum = np.cumsum(pca.explained_variance_ratio_)
    k = int(min(np.searchsorted(cum, variance) + 1, max_components, len(feats)))
    return TopoModel(feats, mu, sd, pca.components_[:k], np.sqrt(pca.explained_variance_[:k]), cum[:k])


def earth_stats(earth: pd.DataFrame) -> tuple[pd.Series, pd.Series]:
    mu = earth[FEATURES].mean()
    sd = earth[FEATURES].std().replace(0, 1).fillna(1)
    return mu, sd


def site_profiles(target: pd.DataFrame) -> pd.DataFrame:
    """Perfil (media de sus celdas) por sitio. Índice = nombre del sitio."""
    return target.groupby("site")[FEATURES].mean()


def dimension_scores(cells: pd.DataFrame, profile: pd.Series, topo_model: TopoModel | None = None,
                     ref: pd.DataFrame | None = None) -> pd.DataFrame:
    """Score 0-1 por dimensión para cada fila de `cells`.

    `ref` (por defecto `cells`) fija la media/desviación de la estandarización: usa la malla de la
    Tierra cuando puntúas otras tablas (p. ej. los sitios análogos conocidos).
    """
    mu, sd = earth_stats(cells if ref is None else ref)
    z_cells = (cells[FEATURES] - mu) / sd
    z_site = (profile[FEATURES].astype(float) - mu) / sd
    out = {}
    for dim, feats in DIMENSIONS.items():
        if dim == "topo" and topo_model is not None:
            diff = topo_model.transform(cells) - topo_model.transform(profile.to_frame().T).iloc[0]
        else:
            diff = z_cells[feats] - z_site[feats]
        out[dim] = np.exp(-np.sqrt(diff.pow(2).mean(axis=1, skipna=True)))
    return pd.DataFrame(out, index=cells.index)


def global_score(dim_scores: pd.DataFrame, weights: dict[str, float] | None = None) -> pd.Series:
    w = pd.Series({**DEFAULT_WEIGHTS, **(weights or {})})[dim_scores.columns]
    valid = dim_scores.notna()
    num = (dim_scores.fillna(0) * w).sum(axis=1)
    den = (valid * w).sum(axis=1)
    return (num / den.where(den > 0)).rename("score")


def score_cells(cells: pd.DataFrame, profile: pd.Series, weights: dict[str, float] | None = None,
                topo_model: TopoModel | None = None, ref: pd.DataFrame | None = None) -> pd.DataFrame:
    """Scores por dimensión y global, en el orden de `cells` (sin ordenar ni rankear)."""
    dims = dimension_scores(cells, profile, topo_model, ref)
    keep = [c for c in ("cell_id", "lat", "lon", "name") if c in cells.columns]
    return pd.concat([cells[keep], dims, global_score(dims, weights)], axis=1)


def rank_cells(earth: pd.DataFrame, profile: pd.Series, weights: dict[str, float] | None = None,
               topo_model: TopoModel | None = None) -> pd.DataFrame:
    """Devuelve las celdas con scores por dimensión, score global y ranking (1 = mejor)."""
    out = score_cells(earth, profile, weights, topo_model)
    out["rank"] = out["score"].rank(ascending=False, method="min")
    return out.sort_values("rank").reset_index(drop=True)
