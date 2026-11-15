"""Experiment A: calibrate the distance with the target's variability (docs/preregistrations/variability.md).

Each Moon and Mars target is measured on a 3 x 3 grid of 50 km windows shifted -25, 0 and +25 km (the polar ones, |lat| >= 85°,
north-south only). The standard deviation `s_k` of each whitened principal component across the target's valid windows is used to
divide the difference by sqrt(1 + s_k^2): a heterogeneous site tolerates more difference than a uniform one. Only the topography changes.

    python -m astroatlas.variability --build      # reads the additional windows from the DEMs (network)
    python -m astroatlas.variability              # evaluates
"""
import argparse
import dataclasses
import math
import time

import numpy as np
import pandas as pd

from .config import FEATURES_DIR, FEATURES_WRITE_DIR, RESULTS_DIR
from .data.dem import _enter, site_topography
from .data.mars import DEM as MARS_DEM
from .data.moon import DEM as MOON_DEM
from .features import load_features
from .similarity import TopoModel, fit_topo_model
from .validation_ext import extended_known, extended_sites
from .variants import evaluate, paired, profiles_with, usgs_stratified, verdict

OFFSETS_KM = (-25.0, 0.0, 25.0)
POLAR_LAT = 85.0
MIN_WINDOWS, MIN_WINDOWS_POLAR = 5, 3
MIN_VALID_FRAC = 0.5
DEMS = {"moon": MOON_DEM, "mars": MARS_DEM}


def offset_point(lat: float, lon: float, dy_km: float, dx_km: float, radius_km: float) -> tuple[float, float]:
    """Point dy_km north and dx_km east of (lat, lon) on a sphere; crossing a pole mirrors the latitude and rotates the longitude 180°."""
    km_deg = radius_km * math.pi / 180.0
    lat2 = lat + dy_km / km_deg
    lon2 = lon + (dx_km / (km_deg * max(math.cos(math.radians(lat)), 0.05)) if dx_km else 0.0)
    if lat2 > 90.0:
        lat2, lon2 = 180.0 - lat2, lon2 + 180.0
    elif lat2 < -90.0:
        lat2, lon2 = -180.0 - lat2, lon2 + 180.0
    return lat2, ((lon2 + 180.0) % 360.0) - 180.0


def window_offsets(lat: float) -> list[tuple[float, float]]:
    """(dy, dx) in km of the target's windows: 3 x 3, or only 3 north-south for the polar ones."""
    if abs(lat) >= POLAR_LAT:
        return [(dy, 0.0) for dy in OFFSETS_KM]
    return [(dy, dx) for dy in OFFSETS_KM for dx in OFFSETS_KM]


def build_windows(body: str, targets: pd.DataFrame, retries: int = 3) -> pd.DataFrame:
    """Topographic features of all the windows of the body's targets (one row per target and offset)."""
    dem = _enter(DEMS[body]())
    rows = []
    try:
        for t in targets.itertuples():
            for dy, dx in window_offsets(t.lat):
                lat2, lon2 = offset_point(t.lat, t.lon, dy, dx, dem.radius_m / 1000.0)
                f = None
                for attempt in range(retries):
                    try:
                        f = site_topography(dem, lat2, lon2)
                        break
                    except OSError as e:  # network cut: the DEM is reopened and retried
                        print(f"  retry {attempt + 1}/{retries} at {t.site} ({dy},{dx}): {str(e)[:70]}", flush=True)
                        dem.__exit__(None, None, None)
                        time.sleep(5 * (attempt + 1))
                        dem = _enter(DEMS[body]())
                rows.append({"body": body, "site": t.site, "dy_km": dy, "dx_km": dx, "lat": lat2, "lon": lon2 % 360, **(f or {})})
            print(f"  {body} · {t.site}", flush=True)
    finally:
        dem.__exit__(None, None, None)
    return pd.DataFrame(rows)


def target_spread(windows: pd.DataFrame, model: TopoModel) -> pd.DataFrame:
    """Standard deviation (n - 1) of each whitened component across the valid windows of each target; targets with few windows, s = 0."""
    out = []
    pcs = model.transform(windows)
    ok = windows.get("valid_frac", pd.Series(1.0, index=windows.index)).fillna(0) >= MIN_VALID_FRAC
    for site, g in windows.groupby("site"):
        idx = g.index[ok.loc[g.index] & pcs.loc[g.index].notna().all(axis=1)]
        polar = abs(g["lat"].iloc[len(g) // 2]) >= POLAR_LAT
        need = MIN_WINDOWS_POLAR if polar or len(g) <= 3 else MIN_WINDOWS
        s = pcs.loc[idx].std(ddof=1).to_numpy() if len(idx) >= need else np.zeros(model.n_components)
        out.append({"site": site, "n_valid": len(idx), "calibrado": len(idx) >= need,
                    **{f"s{k + 1}": float(v) for k, v in enumerate(s)}})
    return pd.DataFrame(out).set_index("site")


def calibrated_model(model: TopoModel, s: np.ndarray) -> TopoModel:
    """Model whose scale is multiplied by sqrt(1 + s^2): the whitened difference ends up divided by that root."""
    return dataclasses.replace(model, scale=model.scale * np.sqrt(1.0 + np.asarray(s, dtype=float) ** 2))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--build", action="store_true")
    a = ap.parse_args()
    if a.build:
        FEATURES_WRITE_DIR.mkdir(parents=True, exist_ok=True)
        for body in ("moon", "mars"):
            targets = load_features(body, FEATURES_DIR)[["site", "lat", "lon"]]
            w = build_windows(body, targets)
            w.to_parquet(FEATURES_WRITE_DIR / f"target_windows_{body}.parquet", index=False)
            print(f"{body}: {len(w)} ventanas, {int(w['topo__slope_mean_deg'].notna().sum())} with data", flush=True)
        return
    earth = load_features("earth", FEATURES_DIR)
    base = fit_topo_model(earth)
    profiles = {b: profiles_with(load_features(b, FEATURES_DIR)) for b in ("moon", "mars")}
    spread = {b: target_spread(pd.read_parquet(FEATURES_DIR / f"target_windows_{b}.parquet"), base) for b in ("moon", "mars")}
    models = {(b, s): calibrated_model(base, [r[f"s{k + 1}"] for k in range(base.n_components)])
              for b, sp in spread.items() for s, r in sp.iterrows()}
    sites, known = extended_sites(), extended_known()
    usgs = pd.read_parquet(FEATURES_DIR / "earth_usgs.parquet")
    raw_b = evaluate(earth, profiles, sites, known, lambda b, t: base)
    raw_v = evaluate(earth, profiles, sites, known, lambda b, t: models[(b, t)])
    rows = [paired(raw_b, raw_v, body, cfg) for body in ("moon", "mars") for cfg in ("all", "only topo")]
    res = pd.DataFrame(rows)
    pd.set_option("display.width", 200)
    for b, sp in spread.items():
        print(f"\n{b}: objetivos calibrados {int(sp['calibrado'].sum())}/{len(sp)}; mean s per component: "
              + ", ".join(f"{c}={sp[c].mean():.2f}" for c in sp.columns if c.startswith("s") and c[1:].isdigit()))
    print(res.round(3).to_string(index=False))
    print("\nPREREGISTERED CRITERION (lower bound of 'all' > 0 in one body and no upper bound < 0):", verdict(rows))
    us = pd.concat([usgs_stratified(earth, profiles, usgs, lambda b, t: base).assign(modelo="base"),
                    usgs_stratified(earth, profiles, usgs, lambda b, t: models[(b, t)]).assign(modelo="variabilidad")])
    print("\nUSGS, AUC stratified by slope:")
    print(us[["modelo", "body", "n_strata", "auc_estratificado", "ci_lo", "ci_hi", "senal"]].round(3).to_string(index=False))
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    res.to_csv(RESULTS_DIR / "variability_paired.csv", index=False)
    us.to_csv(RESULTS_DIR / "variability_usgs.csv", index=False)
    pd.concat([sp.assign(body=b) for b, sp in spread.items()]).to_csv(RESULTS_DIR / "variability_s_per_target.csv")


if __name__ == "__main__":
    main()
