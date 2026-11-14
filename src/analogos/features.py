"""Carga y validación del contrato de features."""
import pandas as pd

from .config import BODIES, FEATURES, FEATURES_DIR, REQUIRED_COLS


def validate_features(df: pd.DataFrame, body: str) -> pd.DataFrame:
    """Comprueba que `df` cumple el contrato. Lanza ValueError si no."""
    missing = [c for c in REQUIRED_COLS if c not in df.columns]
    if missing:
        raise ValueError(f"[{body}] faltan columnas obligatorias: {missing}")
    if not (df["body"] == body).all():
        raise ValueError(f"[{body}] la columna 'body' debe valer '{body}'")
    if df["cell_id"].duplicated().any():
        raise ValueError(f"[{body}] cell_id duplicados")
    if not df["lat"].between(-90, 90).all() or not df["lon"].between(-180, 360).all():
        raise ValueError(f"[{body}] lat/lon fuera de rango")
    if body != "earth" and "site" not in df.columns:
        raise ValueError(f"[{body}] falta la columna 'site'")
    unknown = [c for c in df.columns if "__" in c and c not in FEATURES]
    if unknown:
        raise ValueError(f"[{body}] features no declaradas en config.DIMENSIONS: {unknown}")
    return df


def load_features(body: str, directory=FEATURES_DIR) -> pd.DataFrame:
    if body not in BODIES:
        raise ValueError(f"body desconocido: {body}")
    path = directory / f"{body}.parquet"
    if not path.exists():
        raise FileNotFoundError(
            f"No existe {path}. Genera datos de prueba con: python -m analogos.synthetic"
        )
    return validate_features(pd.read_parquet(path), body)
