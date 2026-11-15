"""Evaluador común para variantes de la dimensión de topografía (docs/PREREGISTRO_MULTIESCALA.md y PREREGISTRO_VARIABILIDAD.md).

Replica la medida de la validación ampliada (u por análogo con ventanas de 50 km, `validate.evaluate_sites`) pero permite que cada objetivo
use su PROPIO modelo de topografía (`topo_provider(body, target) -> TopoModel`) y que los perfiles incluyan columnas extra. Con el proveedor
base reproduce exactamente `validation_ext.raw_ablation` (se comprueba en los tests y en la ejecución).
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

CONFIGS = {"todas": {d: 1.0 for d in DIMENSIONS}, "solo topo": weights_only("topo")}
TopoProvider = Callable[[str, str], TopoModel]


def profiles_with(target: pd.DataFrame, extra: list[str] | None = None) -> pd.DataFrame:
    """Perfil por sitio (media de sus filas) con las columnas FEATURES y las `extra`."""
    cols = list(FEATURES) + [c for c in (extra or []) if c in target.columns and c not in FEATURES]
    return target.groupby("site")[cols].mean()


def evaluate(earth: pd.DataFrame, profiles: dict[str, pd.DataFrame], sites: pd.DataFrame, known: pd.DataFrame,
             provider: TopoProvider, configs: dict[str, dict[str, float]] | None = None) -> pd.DataFrame:
    """Una fila por (cuerpo, objetivo, configuración, análogo) con u = 1 - percentil/100."""
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
    """AUC estratificado por pendiente (cráteres y dunas frente a controles) con la topografía sola; un modelo de topografía por objetivo."""
    pos = usgs["group"].isin(["crater", "dunes"]).to_numpy()
    ctrl = (usgs["group"] == "control").to_numpy()
    rows = []
    for body, prof in profiles.items():
        cols = [aspect_usgs.u_of_sites(usgs, earth, profile, provider(body, target)) for target, profile in prof.iterrows()]
        u = np.nanmean(np.vstack(cols), axis=0)
        rows.append({"body": body, **compare_stratified(u, pos, ctrl, usgs["topo__slope_mean_deg"].to_numpy(), n_boot=n_boot)})
    return pd.DataFrame(rows)


def paired(raw_base: pd.DataFrame, raw_var: pd.DataFrame, body: str, cfg: str, n_boot: int = 4000, seed: int = 0) -> dict:
    """Diferencia pareada por análogo del u medio (variante - base) para una configuración, con IC 95 % por bootstrap sobre los análogos."""
    from .validation_ext import boot_mean

    a = raw_var[(raw_var["body"] == body) & (raw_var["config"] == cfg)].groupby("analog")["u"].mean()
    b = raw_base[(raw_base["body"] == body) & (raw_base["config"] == cfg)].groupby("analog")["u"].mean()
    d = (a - b).dropna().to_numpy()
    m, lo, hi = boot_mean(d, n_boot, seed)
    return {"body": body, "config": cfg, "n": len(d), "u_base": float(b.mean()), "u_variante": float(a.mean()),
            "diff": m, "ic_lo": lo, "ic_hi": hi}


def verdict(rows: list[dict]) -> bool:
    """Criterio preregistrado: límite inferior de «todas» > 0 en al menos un cuerpo y ningún límite superior < 0."""
    t = [r for r in rows if r["config"] == "todas"]
    return any(r["ic_lo"] > 0 for r in t) and not any(r["ic_hi"] < 0 for r in t)
