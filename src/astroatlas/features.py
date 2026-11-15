"""Loading and validation of the feature contract."""
import pandas as pd
from typing import List, Optional

from .config import BODIES, FEATURES, FEATURES_DIR, REQUIRED_COLS

def validate_features(df: pd.DataFrame, body: str) -> pd.DataFrame:
    """Checks that `df` complies with the contract. Raises ValueError if not."""
    missing = [c for c in REQUIRED_COLS if c not in df.columns]
    if missing:
        raise ValueError(f"[{body}] faltan columnas obligatorias: {missing}")
    if not (df["body"] == body).all():
        raise ValueError(f"[{body}] column 'body' must be '{body}'")
    if df["cell_id"].duplicated().any():
        raise ValueError(f"[{body}] cell_id duplicados")
    if not df["lat"].between(-90, 90).all() or not df["lon"].between(-180, 360).all():
        raise ValueError(f"[{body}] lat/lon out of range")
    if body != "earth" and "site" not in df.columns:
        raise ValueError(f"[{body}] column 'site' is missing")
    unknown = [c for c in df.columns if "__" in c and c not in FEATURES]
    if unknown:
        raise ValueError(f"[{body}] features not declared in config.DIMENSIONS: {unknown}")
    return df

def load_features(body: str, directory=FEATURES_DIR, columns: Optional[List[str]] = None) -> pd.DataFrame:
    """
    Loads features for a given body.
    
    Args:
        body: The celestial body (earth, moon, mars).
        directory: Path to the data directory.
        columns: Optional list of columns to load. If None, all columns are loaded.
    """
    if body not in BODIES:
        raise ValueError(f"body desconocido: {body}")
    
    path = directory / f"{body}.parquet"
    if not path.exists():
        raise FileNotFoundError(
            f"No existe {path}. Generate test data with: python -m astroatlas.synthetic"
        )
    
    # Optimization: Load only required columns to save memory and IO
    if columns:
        # Ensure required columns are included in the selection
        full_cols = list(dict.fromkeys(REQUIRED_COLS + columns))
        df = pd.read_parquet(path, columns=full_cols)
    else:
        df = pd.read_parquet(path)
        
    return validate_features(df, body)
