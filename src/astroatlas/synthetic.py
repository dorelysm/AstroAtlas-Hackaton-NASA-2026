"""SYNTHETIC data that respects the contract, to develop the model and app without waiting for downloads.

    python -m astroatlas.synthetic        # writes data/features/{earth,moon,mars}.parquet

It has no scientific value. Replace it with the real data of each body.
"""
import numpy as np
import pandas as pd

from .config import FEATURES_WRITE_DIR, SITES_CSV
from .grid import make_grid

_RNG_SEED = 42


def _topo(rng, n: int) -> dict:
    """Random topo__* features that are coherent with each other (rough -> more relief, etc.)."""
    slope = np.clip(rng.gamma(2, 1.5, n), 0, 40)
    rough = np.clip(rng.gamma(2, 20, n) * (1 + slope / 5), 0, 2000)
    return {
        "topo__slope_mean_deg": slope, "topo__slope_p90_deg": slope * rng.uniform(1.5, 2.5, n),
        "topo__frac_slope_lt5deg": np.clip(1 - slope / 12 + rng.normal(0, 0.05, n), 0, 1),
        "topo__frac_slope_gt15deg": np.clip(slope / 40 + rng.normal(0, 0.03, n), 0, 1),
        "topo__flat_patch_km2": np.clip(rng.gamma(2, 150, n) * (1 - slope / 40), 0, 2500),
        "topo__relief_m": rough * rng.uniform(2, 6, n), "topo__elev_std_m": rough * rng.uniform(1, 3, n),
        "topo__rough_1km_m": rough, "topo__rough_2km_m": rough * 1.5, "topo__rough_5km_m": rough * 2.5,
        "topo__tri_m": rough * 0.4, "topo__tpi_std_m": rough * 0.25,
        "topo__curv_profile_abs_per_km": rng.gamma(2, 0.5, n), "topo__curv_plan_abs_per_km": rng.gamma(2, 0.5, n),
        "topo__aspect_concentration": rng.beta(2, 3, n), "topo__aspect_equatorward": rng.uniform(-1, 1, n),
    }


def synthetic_earth(step_deg: float = 2.0, seed: int = _RNG_SEED) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    df = make_grid(step_deg, "earth")
    n, lat = len(df), df["lat"].abs()
    for k, v in _topo(rng, n).items():
        df[k] = v
    df["thermal__t_max_k"] = 315 - 0.6 * lat + rng.normal(0, 4, n)
    df["thermal__t_range_k"] = np.clip(10 + rng.gamma(2, 4, n), 2, 60)
    df["ice__water_frac"] = np.clip(rng.beta(1, 3, n) + (lat > 70) * 0.3, 0, 1)
    df["geo__basalt_frac"] = np.clip(rng.beta(1, 6, n), 0, 1)
    return df


def synthetic_target(body: str, sites: pd.DataFrame, cells_per_site: int = 25, seed: int = _RNG_SEED) -> pd.DataFrame:
    rng = np.random.default_rng(seed + (1 if body == "moon" else 2))
    rows = []
    for _, s in sites[sites["body"] == body].iterrows():
        base = {
            **{k: float(v[0]) for k, v in _topo(rng, 1).items()},
            "thermal__t_max_k": rng.uniform(150, 300), "thermal__t_range_k": rng.uniform(20, 150),
            "ice__water_frac": rng.uniform(0, 0.5), "geo__basalt_frac": rng.uniform(0.2, 0.9),
        }
        for k in range(cells_per_site):
            row = {"cell_id": f"{body}_{s['site']}_{k}", "body": body, "site": s["site"],
                   "lat": float(np.clip(s["lat"] + rng.normal(0, 0.2), -90, 90)),
                   "lon": s["lon"] + rng.normal(0, 0.2)}
            row.update({f: v * rng.normal(1, 0.05) for f, v in base.items()})
            rows.append(row)
    return pd.DataFrame(rows)


def main() -> None:
    sites = pd.read_csv(SITES_CSV)
    FEATURES_WRITE_DIR.mkdir(parents=True, exist_ok=True)
    synthetic_earth().to_parquet(FEATURES_WRITE_DIR / "earth.parquet", index=False)
    for body in ("moon", "mars"):
        synthetic_target(body, sites).to_parquet(FEATURES_WRITE_DIR / f"{body}.parquet", index=False)
    print(f"Synthetic data written to {FEATURES_WRITE_DIR}")


if __name__ == "__main__":
    main()
