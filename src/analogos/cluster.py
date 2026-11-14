"""Agrupamiento de celdas terrestres en el espacio de features (PCA + HDBSCAN).

UMAP es opcional (`pip install -e .[ml]`): se usa solo para visualizar.
"""
import pandas as pd
from sklearn.cluster import HDBSCAN
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

from .config import FEATURES


def cluster_cells(earth: pd.DataFrame, n_components: int = 3, min_cluster_size: int = 20) -> pd.DataFrame:
    """Devuelve cell_id, pc1.., cluster (-1 = ruido). Los NaN se imputan con la mediana
    SOLO para este paso (no se guardan)."""
    X = earth[FEATURES].fillna(earth[FEATURES].median())
    X = StandardScaler().fit_transform(X)
    pcs = PCA(n_components=min(n_components, X.shape[1])).fit_transform(X)
    labels = HDBSCAN(min_cluster_size=min_cluster_size, copy=True).fit_predict(pcs)
    out = pd.DataFrame(pcs, columns=[f"pc{i + 1}" for i in range(pcs.shape[1])], index=earth.index)
    out.insert(0, "cell_id", earth["cell_id"])
    out["cluster"] = labels
    return out


def umap_embedding(earth: pd.DataFrame, **kwargs) -> pd.DataFrame:
    try:
        import umap
    except ImportError as e:  # pragma: no cover
        raise ImportError("Instala UMAP con: pip install -e .[ml]") from e
    X = StandardScaler().fit_transform(earth[FEATURES].fillna(earth[FEATURES].median()))
    emb = umap.UMAP(**kwargs).fit_transform(X)
    return pd.DataFrame(emb, columns=["umap1", "umap2"], index=earth.index)
