"""Validation with the extended set of analogs (docs/preregistrations/analog-validation.md).

The model is FROZEN (commit 0b8a0a2). The features of the 13 new analogs are computed with the same 50 km windows
(Copernicus topography, MODIS thermal and snow, GLiM geology), joined to the original 10 (without recomputing them) and evaluated with the
fixed metrics: mean u per body with a bootstrap over the analogs, for original / new / all, and per aspect when there is data.

    python -m astroatlas.validation_ext --build      # downloads and computes the features of the new sites
    python -m astroatlas.validation_ext              # evaluates (uses the features already computed)
"""
import argparse
import json
import shutil
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd

from . import ablation, aspect
from .config import DOCS, FEATURES_DIR, FEATURES_WRITE_DIR, RESULTS_DIR
from .data import earth, earth_geology, earth_thermal, earth_water
from .features import load_features
from .validate import known_for_body

NEW_CSV = DOCS / "catalog/extended_analogs.csv"
NEW_TAGS = DOCS / "catalog/extended_analog_aspects.csv"
EXT_PARQUET = "earth_sites_ext.parquet"
YEAR = 2019


def build_new_sites() -> pd.DataFrame:
    """Features (topography, LST, snow, GLiM) of the new analogs, with the same computation as the original sites."""
    n = pd.read_csv(NEW_CSV)
    cells = pd.DataFrame({"cell_id": [f"earth_ext_{i}" for i in range(len(n))], "body": "earth",
                          "lat": n["lat"], "lon": n["lon"], "name": n["name"]})
    df = pd.concat([cells, earth.build_topography(cells)], axis=1)
    df = earth_thermal.apply_to_earth(df, earth_thermal.run_lst(df, YEAR))
    df = earth_water.apply_to_earth(df, earth_water.run_snow(df, YEAR))
    grid, names, lats, lons = earth_geology.load_glim()
    return earth_geology.apply_to_earth(df, earth_geology.geology_features(df, grid, names, lats, lons))


def extended_sites(path: Path | None = None) -> pd.DataFrame:
    base = pd.read_parquet(FEATURES_DIR / "earth_sites.parquet")
    new = pd.read_parquet(path or FEATURES_WRITE_DIR / EXT_PARQUET)
    cols = [c for c in base.columns if c in new.columns]
    return pd.concat([base[cols].assign(group="original"), new[cols].assign(group="nuevo")], ignore_index=True)


def extended_known() -> pd.DataFrame:
    o = pd.read_csv(DOCS / "catalog/known_analogs.csv").assign(group="original")
    n = pd.read_csv(NEW_CSV).assign(group="nuevo")
    return pd.concat([o, n], ignore_index=True)


def extended_tags() -> pd.DataFrame:
    return pd.concat([aspect.load_tags(aspect.TAGS_CSV), aspect.load_tags(NEW_TAGS)], ignore_index=True)


def raw_ablation(sites: pd.DataFrame, known: pd.DataFrame) -> pd.DataFrame:
    """Table (target, configuration, analog, u) like that of ablation.run, but with the extended set."""
    tmp = Path(tempfile.mkdtemp())
    try:
        for b in ("earth", "moon", "mars"):
            shutil.copy(FEATURES_DIR / f"{b}.parquet", tmp / f"{b}.parquet")
        sites.to_parquet(tmp / "earth_sites.parquet", index=False)
        original = ablation.load_known
        ablation.load_known = lambda: known
        try:
            return ablation.run(features_dir=tmp)
        finally:
            ablation.load_known = original
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def boot_mean(vals: np.ndarray, n_boot: int = 4000, seed: int = 0) -> tuple[float, float, float]:
    vals = vals[np.isfinite(vals)]
    if len(vals) < 2:
        return (float(vals.mean()) if len(vals) else float("nan"), float("nan"), float("nan"))
    rng = np.random.default_rng(seed)
    m = [rng.choice(vals, len(vals)).mean() for _ in range(n_boot)]
    return float(vals.mean()), float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))


def summarize_groups(raw: pd.DataFrame, known: pd.DataFrame) -> pd.DataFrame:
    """Mean u per analog (over the body's targets) and its bootstrap CI over the analogs, per group and configuration."""
    grp = known.set_index("name")["group"]
    rows = []
    for body in ("moon", "mars"):
        for cfg in ("all", "only topo", "only thermal", "only ice", "only geo"):
            g = raw[(raw["body"] == body) & (raw["config"] == cfg)].groupby("analog")["u"].mean()
            for label, sel in (("todos", g.index), ("originales", g.index[grp.reindex(g.index) == "original"]),
                               ("nuevos", g.index[grp.reindex(g.index) == "nuevo"])):
                v = g.reindex(sel).to_numpy()
                m, lo, hi = boot_mean(v)
                rows.append({"body": body, "config": cfg, "grupo": label, "n_analogs": int(np.isfinite(v).sum()),
                             "u_medio": m, "ci_lo": lo, "ci_hi": hi})
    return pd.DataFrame(rows)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--build", action="store_true")
    ap.add_argument("--out", type=Path, default=RESULTS_DIR)
    a = ap.parse_args()
    if a.build:
        FEATURES_WRITE_DIR.mkdir(parents=True, exist_ok=True)
        new = build_new_sites()
        new.to_parquet(FEATURES_WRITE_DIR / EXT_PARQUET, index=False)
        print(f"{len(new)} new sites computed; with thermal: {int(new['thermal__t_max_k'].notna().sum())}, "
              f"with geology: {int(new['geo__basalt_frac'].notna().sum())}")
        return
    sites, known, tags = extended_sites(), extended_known(), extended_tags()
    raw = raw_ablation(sites, known)
    a.out.mkdir(parents=True, exist_ok=True)
    raw.to_csv(a.out / "ext_ablation_raw.csv", index=False)
    groups = summarize_groups(raw, known)
    groups.to_csv(a.out / "ext_groups.csv", index=False)
    asp = aspect.run(df=raw, tags=tags, n_boot=2000)
    asp.drop(columns=["on", "off"]).to_csv(a.out / "ext_aspects.csv", index=False)
    per = (raw[raw["config"] == "all"].groupby(["body", "analog"])["u"].mean().round(3).reset_index()
           .merge(known[["name", "group"]], left_on="analog", right_on="name").drop(columns="name"))
    per.to_csv(a.out / "ext_u_per_analog.csv", index=False)
    pd.set_option("display.width", 220)
    print(groups[groups["config"] == "all"].round(3).to_string(index=False))
    print("\nPer aspect (source + note), body, with >= 2 in each group:")
    s = asp[(asp["nivel"] == 2) & (asp["estado"] == "ok")]
    print(s[["body", "aspect", "n_on", "n_off", "gap", "gap_lo", "gap_hi", "p_perm"]].round(2).to_string(index=False))
    print(json.dumps({"astroatlas": len(known), "nuevos": int((known['group'] == 'nuevo').sum())}))


if __name__ == "__main__":
    main()
