"""Similarity between Earth cells and the profile of a target site.

  - Standardised with the Earth's mean/standard deviation.
  - Distance per dimension = RMS of the z differences of its features (ignores NaN).
  - Topography (optional, recommended): its 16 variables are highly correlated (mean |r| ~0.74,
    3 components explain ~90 % of the variance), so they would count double. `fit_topo_model` summarises them
    into a few WHITENED principal components (variance 1 each) and the distance is measured there.
    It is equivalent to a Mahalanobis distance restricted to the principal subspace.
  - Score per dimension = exp(-distance)  -> 1 = identical, ~0 = very different.
  - Global score = weighted mean of the available dimensions.
"""
from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA

from .config import DEFAULT_WEIGHTS, DIMENSIONS, FEATURES


@dataclass
class TopoModel:
    """Whitened PCA of the topography, fitted ONLY with Earth cells."""
    features: list[str]
    mu: pd.Series
    sd: pd.Series
    components: np.ndarray  # (k, p)
    scale: np.ndarray       # standard deviation of each component (to whiten)
    cum_variance: np.ndarray

    @property
    def n_components(self) -> int:
        return len(self.scale)

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Whitened components; NaN in the rows with any topographic variable missing
        (it is not silently imputed)."""
        z = ((df[self.features] - self.mu) / self.sd).to_numpy(dtype=float)
        with np.errstate(invalid="ignore"):
            pcs = (z @ self.components.T) / self.scale
        pcs[np.isnan(z).any(axis=1)] = np.nan
        return pd.DataFrame(pcs, index=df.index, columns=[f"pc{i + 1}" for i in range(self.n_components)])


def fit_topo_model(ref: pd.DataFrame, variance: float = 0.90, max_components: int = 6,
                   features: list[str] | None = None) -> TopoModel:
    """Fits the PCA with the rows of `ref` that have all the topography; keeps the minimum
    components that explain `variance` of the variance (max. `max_components`)."""
    feats = list(features or DIMENSIONS["topo"])
    X = ref[feats].dropna()
    if len(X) < len(feats) + 2:
        raise ValueError(f"Hay {len(X)} rows with complete topography; more than {len(feats) + 1}")
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
    """Profile (mean of its cells) per site. Index = site name."""
    return target.groupby("site")[FEATURES].mean()


def dimension_scores(cells: pd.DataFrame, profile: pd.Series, topo_model: TopoModel | None = None,
                     ref: pd.DataFrame | None = None) -> pd.DataFrame:
    """Score 0-1 per dimension for every row of `cells`.

    `ref` (default `cells`) fixes the mean/deviation of the standardisation: use the Earth grid when
    scoring other tables (e.g. the known analog sites).
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


MISSING_MODES = ("renormalize", "zero")


def global_score(dim_scores: pd.DataFrame, weights: dict[str, float] | None = None,
                 missing: str = "renormalize", expected: list[str] | None = None) -> pd.Series:
    """Weighted mean of the per-dimension scores.

    missing="renormalize" (default, the published model): each cell is averaged over the dimensions IT has data for,
        so a cell with a gap is not penalised for it (and is compared with cells that were).
    missing="zero" (experimental, docs/preregistrations/missing-dimensions.md): every dimension the target can be
        compared on (`expected`, by default those with at least one score) counts for every cell, and a gap scores 0.
        A cell with no score at all stays NaN.
    """
    if missing not in MISSING_MODES:
        raise ValueError(f"missing must be one of {MISSING_MODES}, not {missing!r}")
    w = pd.Series({**DEFAULT_WEIGHTS, **(weights or {})})[dim_scores.columns]
    if missing == "zero":
        cols = [c for c in dim_scores.columns if (c in expected if expected is not None else dim_scores[c].notna().any())]
        x, wx = dim_scores[cols], w[cols]
        den = wx.sum()
        if not cols or den <= 0:
            return pd.Series(np.nan, index=dim_scores.index, name="score")
        return ((x.fillna(0) * wx).sum(axis=1) / den).where(x.notna().any(axis=1)).rename("score")
    valid = dim_scores.notna()
    num = (dim_scores.fillna(0) * w).sum(axis=1)
    den = (valid * w).sum(axis=1)
    return (num / den.where(den > 0)).rename("score")


def _profile_dims(profile: pd.Series) -> list[str]:
    """Dimensions in which the target has at least one feature with data."""
    return [d for d, feats in DIMENSIONS.items() if profile.reindex(feats).notna().any()]


def score_cells(cells: pd.DataFrame, profile: pd.Series, weights: dict[str, float] | None = None,
                topo_model: TopoModel | None = None, ref: pd.DataFrame | None = None,
                missing: str = "renormalize") -> pd.DataFrame:
    """Scores per dimension and global, in the order of `cells` (not sorted nor ranked).

    `missing`: how a cell without data in a dimension is treated, see `global_score` (default: unchanged model)."""
    dims = dimension_scores(cells, profile, topo_model, ref)
    keep = [c for c in ("cell_id", "lat", "lon", "name") if c in cells.columns]
    expected = _profile_dims(profile) if missing == "zero" else None
    return pd.concat([cells[keep], dims, global_score(dims, weights, missing, expected)], axis=1)


def rank_cells(earth: pd.DataFrame, profile: pd.Series, weights: dict[str, float] | None = None,
               topo_model: TopoModel | None = None, missing: str = "renormalize") -> pd.DataFrame:
    """Returns the cells with scores per dimension, global score and ranking (1 = best)."""
    out = score_cells(earth, profile, weights, topo_model, missing=missing)
    out["rank"] = out["score"].rank(ascending=False, method="min")
    return out.sort_values("rank").reset_index(drop=True)
