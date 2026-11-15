"""Paths and definition of dimensions/features (see docs/reference/feature-contract.md)."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
DEMO_DIR = ROOT / "demo_data"  # reduced, versioned copy of the features so the app runs without regenerating anything
# If there is no own data (data/ is not versioned) demo_data/ is used. Own data takes priority.
FEATURES_WRITE_DIR = DATA / "features"  # where the data modules WRITE; never demo_data/
FEATURES_DIR = DATA / "features" if (DATA / "features" / "earth.parquet").exists() else DEMO_DIR / "features"
RESULTS_DIR = DATA / "results"
RAW_DIR = DATA / "raw"
PROCESSED_DIR = DATA / "processed"
DOCS = ROOT / "docs"
SITES_CSV = DOCS / "catalog/target_sites.csv"
KNOWN_CSV = DOCS / "catalog/known_analogs.csv"
LANDINGS_CSV = DOCS / "catalog/known_landings.csv"

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

# Limits of the analogy: always shown in the profiles.
LIMITS = {
    "moon": ["gravedad ~1/6 g", "vacío (sin atmósfera)", "radiación sin protección", "regolito/polvo abrasivo"],
    "mars": ["gravedad ~0.38 g", "atmósfera ~0.6% de la terrestre", "radiación elevada", "percloratos en el suelo"],
}
