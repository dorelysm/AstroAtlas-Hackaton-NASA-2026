"""Common evaluator for variants of the topography dimension (docs/preregistrations/multiscale.md and docs/preregistrations/variability.md).

It replicates the measure of the extended validation (u per analog with 50 km windows, `validate.evaluate_sites`) but lets each target
use its OWN topography model (`topo_provider(body, target) -> TopoModel`) and lets the profiles include extra columns. With the base
provider it reproduces `validation_ext.raw_ablation` exactly (checked in the tests and in the run).
"""
from collections.abc import Callable

import numpy as np
import pandas as pd

from . import aspect_usgs
from .ablation import weights_only
from .aspect_usgs import compare_stratified
from .config import DIMENSIONS, FEATURES
from .similarity import TopoModel, rank_cells, score_cells
from .validate import evaluate_sites, known_for_body

CONFIGS = {"all": {d: 1.0 for d in DIMENSIONS}, "only topo": weights_only("topo")}
TopoProvider = Callable[[str, str], TopoModel]


def profiles_with(target: pd.DataFrame, extra: list[str] | None = None) -> pd.DataFrame:
    """Profile per site (mean of its rows) with the FEATURES columns and the `extra` ones."""
    cols = list(FEATURES) + [c for c in (extra or []) if c in target.columns and c not in FEATURES]
    return target.groupby("site")[cols].mean()


def evaluate(earth: pd.DataFrame, profiles: dict[str, pd.DataFrame], sites: pd.DataFrame, known: pd.DataFrame,
             provider: TopoProvider, configs: dict[str, dict[str, float]] | None = None) -> pd.DataFrame:
    """One row per (body, target, configuration, analog) with u = 1 - percentile/100."""
    rows = []
    for body, prof in profiles.items():
        known_b = known_for_body(known, body)
        sites_b = sites[sites["name"].isin(known_b["name"])].reset_index(drop=True)
        for target, profile in prof.iterrows():
            topo = provider(body, target)
            for cfg, w in (configs or CONFIGS).items():
                ranked = rank_cells(earth, profile, w, topo)
                sc = score_cells(sites_b, profile, w, topo, ref=earth).set_index("name")["score"]
                for name, pct in evaluate_sites(ranked["score"], sc)["percentile_per_known"].items():
                    rows.append({"body": body, "target": target, "config": cfg, "analog": name, "u": 1 - pct / 100})
    return pd.DataFrame(rows)


def usgs_stratified(earth: pd.DataFrame, profiles: dict[str, pd.DataFrame], usgs: pd.DataFrame, provider: TopoProvider,
                    n_boot: int = 2000) -> pd.DataFrame:
    """AUC stratified by slope (craters and dunes against controls) with the topography alone; one topography model per target."""
    pos = usgs["group"].isin(["crater", "dunes"]).to_numpy()
    ctrl = (usgs["group"] == "control").to_numpy()
    rows = []
    for body, prof in profiles.items():
        cols = [aspect_usgs.u_of_sites(usgs, earth, profile, provider(body, target)) for target, profile in prof.iterrows()]
        u = np.nanmean(np.vstack(cols), axis=0)
        rows.append({"body": body, **compare_stratified(u, pos, ctrl, usgs["topo__slope_mean_deg"].to_numpy(), n_boot=n_boot)})
    return pd.DataFrame(rows)


def paired(raw_base: pd.DataFrame, raw_var: pd.DataFrame, body: str, cfg: str, n_boot: int = 4000, seed: int = 0) -> dict:
    """Paired difference per analog of the mean u (variant - base) for one configuration, with a 95 % bootstrap CI over the analogs."""
    from .validation_ext import boot_mean

    a = raw_var[(raw_var["body"] == body) & (raw_var["config"] == cfg)].groupby("analog")["u"].mean()
    b = raw_base[(raw_base["body"] == body) & (raw_base["config"] == cfg)].groupby("analog")["u"].mean()
    d = (a - b).dropna().to_numpy()
    m, lo, hi = boot_mean(d, n_boot, seed)
    return {"body": body, "config": cfg, "n": len(d), "u_base": float(b.mean()), "u_variant": float(a.mean()),
            "diff": m, "ci_lo": lo, "ci_hi": hi}


def verdict(rows: list[dict]) -> bool:
    """Preregistered criterion: lower bound of "all" > 0 in at least one body and no upper bound < 0."""
    t = [r for r in rows if r["config"] == "all"]
    return any(r["ci_lo"] > 0 for r in t) and not any(r["ci_hi"] < 0 for r in t)
