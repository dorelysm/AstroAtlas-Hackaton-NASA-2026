"""Rutas y definición de dimensiones/features (ver docs/features.md)."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
FEATURES_DIR = DATA / "features"
RESULTS_DIR = DATA / "results"
RAW_DIR = DATA / "raw"
PROCESSED_DIR = DATA / "processed"
DOCS = ROOT / "docs"
SITES_CSV = DOCS / "sitios_objetivo.csv"
KNOWN_CSV = DOCS / "analogos_conocidos.csv"
LANDINGS_CSV = DOCS / "aterrizajes_conocidos.csv"

BODIES = ("earth", "moon", "mars")
REQUIRED_COLS = ["cell_id", "body", "lat", "lon"]

DIMENSIONS: dict[str, list[str]] = {
    "topo": [
        "topo__slope_mean_deg", "topo__slope_p90_deg",
        "topo__frac_slope_lt5deg", "topo__frac_slope_gt15deg", "topo__flat_patch_km2",
        "topo__relief_m", "topo__elev_std_m",
        "topo__rough_1km_m", "topo__rough_2km_m", "topo__rough_5km_m",
        "topo__tri_m", "topo__tpi_std_m",
        "topo__curv_profile_abs_per_km", "topo__curv_plan_abs_per_km",
        "topo__aspect_concentration", "topo__aspect_equatorward",
    ],
    "thermal": ["thermal__t_max_k", "thermal__t_range_k"],
    "ice": ["ice__water_frac"],
    "geo": ["geo__basalt_frac"],
}
FEATURES: list[str] = [f for fs in DIMENSIONS.values() for f in fs]
DEFAULT_WEIGHTS: dict[str, float] = {d: 1.0 for d in DIMENSIONS}

# Límites de la analogía: se muestran siempre en las fichas.
LIMITS = {
    "moon": ["gravedad ~1/6 g", "vacío (sin atmósfera)", "radiación sin protección", "regolito/polvo abrasivo"],
    "mars": ["gravedad ~0.38 g", "atmósfera ~0.6% de la terrestre", "radiación elevada", "percloratos en el suelo"],
}
