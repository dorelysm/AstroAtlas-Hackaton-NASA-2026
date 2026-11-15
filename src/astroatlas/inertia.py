"""Experiment: thermal-inertia dimension (docs/preregistrations/thermal-inertia.md).

Mars: MGS-TES night-time thermal-inertia map (PDS mgs-m-tes-5-timap-v1, Putzig and Mellon 2007), median in a ±25 km window,
converted to a PERCENTILE against Mars. Earth: albedo-free apparent proxy 1/(T_day − T_night) from MODIS (diurnal range already computed),
converted to a percentile against the 951 cells. Percentiles are compared WITHIN each body (relative analogy, not absolute values).
The Moon does not have the dimension.

It is an EXPERIMENT: the dimension is added only inside the `extra_dimension` context and does NOT modify the project's model unless the
preregistered criterion is met and adopting it is decided.

    python -m astroatlas.inertia
"""
import contextlib
import shutil
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd

from . import ablation, config
from .config import FEATURES_DIR, RAW_DIR, RESULTS_DIR
from .validation_ext import boot_mean, extended_known, extended_sites

TES_DIR = RAW_DIR / "tes_ti" / "x" / "mgst_9001" / "data"
PPD = 20.0          # pixels per degree
KM_PER_PX = 2.96    # km per pixel at the equator
HALF_KM = 25.0
MAX_ABS_LAT = 80.0
FEATURE = "inertia__ti_pct"


def load_tes_night(directory: Path = TES_DIR) -> tuple[np.ndarray, np.ndarray]:
    """(night-time TI, mask of non-interpolated pixels). Values 0 = no data."""
    ti = np.fromfile(directory / "global_ti_night_2007.img", dtype=">i2").reshape(3600, 7200).astype("float32")
    msk = np.fromfile(directory / "global_ti_msk_night_2007.img", dtype="u1").reshape(3600, 7200)
    ti[(msk != 1) | (ti <= 0)] = np.nan
    return ti, msk


def window_median(ti: np.ndarray, lat: float, lon: float, half_km: float = HALF_KM) -> float:
    """Median of the valid pixels within ±half_km (longitude 0-360 east or -180..180)."""
    lon = ((lon + 180.0) % 360.0) - 180.0
    i0 = (90.0 - lat) * PPD
    j0 = (lon + 180.0) * PPD
    di = half_km / KM_PER_PX
    dj = di / max(np.cos(np.radians(lat)), 0.05)
    ii = np.clip(np.arange(int(np.floor(i0 - di)), int(np.ceil(i0 + di)) + 1), 0, ti.shape[0] - 1)
    jj = np.arange(int(np.floor(j0 - dj)), int(np.ceil(j0 + dj)) + 1) % ti.shape[1]
    v = ti[np.ix_(ii, jj)]
    v = v[np.isfinite(v)]
    return float(np.median(v)) if v.size else float("nan")


def mars_reference(ti: np.ndarray) -> np.ndarray:
    """Sorted valid values over all of Mars with |latitude| <= 80° (reference for the percentiles)."""
    lat = 90.0 - (np.arange(ti.shape[0]) + 0.5) / PPD
    rows = np.abs(lat) <= MAX_ABS_LAT
    v = ti[rows].ravel()
    return np.sort(v[np.isfinite(v)])


def percentile(value, sorted_ref: np.ndarray) -> np.ndarray:
    """Fraction of the reference below `value` (0-1); NaN stays NaN."""
    v = np.asarray(value, dtype=float)
    out = np.searchsorted(sorted_ref, v, side="left") / len(sorted_ref)
    return np.where(np.isfinite(v), out, np.nan)


def earth_proxy(t_range_k) -> np.ndarray:
    """Albedo-free apparent proxy: 1/(T_day − T_night). Non-positive or missing range = NaN."""
    r = np.asarray(t_range_k, dtype=float)
    return np.where(np.isfinite(r) & (r > 0), 1.0 / np.where(r > 0, r, np.nan), np.nan)


def add_earth_inertia(df: pd.DataFrame, ref_cells: pd.DataFrame) -> pd.DataFrame:
    ref = np.sort(earth_proxy(ref_cells["thermal__t_range_k"])[np.isfinite(earth_proxy(ref_cells["thermal__t_range_k"]))])
    out = df.copy()
    out[FEATURE] = percentile(earth_proxy(df["thermal__t_range_k"]), ref)
    return out


def add_mars_inertia(mars: pd.DataFrame, ti: np.ndarray) -> pd.DataFrame:
    ref = mars_reference(ti)
    out = mars.copy()
    vals = [window_median(ti, r.lat, r.lon) for r in out.itertuples()]
    out["ti_night_median"] = vals
    out[FEATURE] = percentile(vals, ref)
    return out


@contextlib.contextmanager
def extra_dimension(name: str = "inertia", features: tuple[str, ...] = (FEATURE,)):
    """Temporarily adds a dimension to the model (restored on exit). The modules share these objects, so it is mutated in place."""
    config.DIMENSIONS[name] = list(features)
    added = [f for f in features if f not in config.FEATURES]
    config.FEATURES.extend(added)
    config.DEFAULT_WEIGHTS[name] = 1.0
    old_dims = ablation.DIMS
    ablation.DIMS = list(config.DIMENSIONS)
    try:
        yield
    finally:
        ablation.DIMS = old_dims
        config.DEFAULT_WEIGHTS.pop(name, None)
        for f in added:
            config.FEATURES.remove(f)
        config.DIMENSIONS.pop(name, None)


def build_experiment_dir() -> tuple[Path, pd.DataFrame, pd.DataFrame]:
    """Temporary folder with the features + the inertia dimension. Returns (folder, extended sites, extended known analogs)."""
    ti, _ = load_tes_night()
    earth = pd.read_parquet(FEATURES_DIR / "earth.parquet")
    sites = add_earth_inertia(extended_sites(), earth)
    tmp = Path(tempfile.mkdtemp())
    add_earth_inertia(earth, earth).to_parquet(tmp / "earth.parquet", index=False)
    add_mars_inertia(pd.read_parquet(FEATURES_DIR / "mars.parquet"), ti).to_parquet(tmp / "mars.parquet", index=False)
    pd.read_parquet(FEATURES_DIR / "moon.parquet").assign(**{FEATURE: np.nan}).to_parquet(tmp / "moon.parquet", index=False)
    sites.to_parquet(tmp / "earth_sites.parquet", index=False)
    return tmp, sites, extended_known()


def paired_diff(raw: pd.DataFrame, body: str, a: str, b: str, n_boot: int = 4000, seed: int = 0) -> dict:
    """Paired difference per analog of mean u between configurations a and b, with a bootstrap CI over the analogs."""
    g = raw[raw["body"] == body].groupby(["config", "analog"])["u"].mean().unstack("config")
    d = (g[a] - g[b]).dropna().to_numpy()
    m, lo, hi = boot_mean(d, n_boot, seed)
    return {"n": len(d), "diff": m, "lo": lo, "hi": hi}


def main() -> None:
    tmp, sites, known = build_experiment_dir()
    try:
        original = ablation.load_known
        ablation.load_known = lambda: known
        try:
            with extra_dimension():
                raw = ablation.run(features_dir=tmp)
        finally:
            ablation.load_known = original
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    raw.to_csv(RESULTS_DIR / "inertia_raw.csv", index=False)
    pd.set_option("display.width", 220)
    m = raw[raw["body"] == "mars"].groupby(["config", "analog"])["u"].mean().unstack("config")
    print("Mars mean u per configuration (mean over analogs), with a 95 % bootstrap CI:")
    rows = []
    for cfg in ("all", "without inertia", "only inertia", "only topo", "only geo", "only ice"):
        mean, lo, hi = boot_mean(m[cfg].dropna().to_numpy())
        rows.append({"config": cfg, "n": int(m[cfg].notna().sum()), "u_medio": mean, "ci_lo": lo, "ci_hi": hi})
    res = pd.DataFrame(rows)
    print(res.round(3).to_string(index=False))
    pdiff = paired_diff(raw, "mars", "all", "without inertia")
    print(f"\nPaired difference 'all + inertia' - 'without inertia': {pdiff['diff']:+.3f} (IC {pdiff['lo']:+.3f} a {pdiff['hi']:+.3f}, n={pdiff['n']})")
    cold = ["Dry Valleys (Antartida)", "Axel Heiberg (McGill Arctic Research Station)", "Svalbard", "Eureka (Ellesmere)"]
    c = m.loc[[x for x in cold if x in m.index], ["without inertia", "all", "only inertia"]]
    print("\nCold analogs (u):")
    print(c.round(2).to_string())
    print("\nAll analogs (u, Mars):")
    print(m[["without inertia", "all", "only inertia"]].round(2).sort_values("only inertia", ascending=False).to_string())
    res.to_csv(RESULTS_DIR / "inertia_summary.csv", index=False)
    pd.DataFrame([pdiff]).to_csv(RESULTS_DIR / "inertia_paired_diff.csv", index=False)


if __name__ == "__main__":
    main()
