"""Selection and data of the candidate profiles (docs/results/candidate-profiles.md).

Selection rule FIXED BEFORE LOOKING at the candidates (15 Nov 2026), per body:
  1. Start from `candidates_shortlist.csv` (viable cells, non-vegetated and > 500 km from any known analog).
  2. Count in how many of the body's targets each cell appears in the top 10; break ties by mean score.
  3. Keep the first 2 cells that are >= 500 km apart (so two neighbouring cells do not come out).

    python -m astroatlas.profiles
"""
import argparse
from pathlib import Path

import pandas as pd

from .config import DIMENSIONS, FEATURES_DIR, RESULTS_DIR
from .features import load_features
from .validate import haversine_km, load_known


def select(short: pd.DataFrame, body: str, n: int = 2, min_sep_km: float = 500) -> pd.DataFrame:
    g = (short[short["body"] == body].groupby(["cell_id", "lat", "lon"])
         .agg(n_targets=("site", "nunique"), score=("score", "mean"), targets=("site", lambda s: ", ".join(sorted(set(s)))))
         .reset_index().sort_values(["n_targets", "score"], ascending=False))
    chosen = []
    for _, r in g.iterrows():
        if all(haversine_km(r["lat"], r["lon"], c["lat"], c["lon"]) >= min_sep_km for c in chosen):
            chosen.append(r)
        if len(chosen) == n:
            break
    return pd.DataFrame(chosen).reset_index(drop=True)


def details(short: pd.DataFrame, picks: pd.DataFrame, body: str, earth: pd.DataFrame, known: pd.DataFrame) -> list[dict]:
    out = []
    for _, p in picks.iterrows():
        rows = short[(short["body"] == body) & (short["cell_id"] == p["cell_id"])]
        e = earth[earth["cell_id"] == p["cell_id"]].iloc[0]
        d = haversine_km(p["lat"], p["lon"], known["lat"].to_numpy(), known["lon"].to_numpy())
        near = int(d.argmin())
        out.append({
            "cell_id": p["cell_id"], "lat": p["lat"], "lon": p["lon"], "body": body, "n_targets": int(p["n_targets"]),
            "targets": p["targets"], "score_mean": float(p["score"]),
            "dims": {k: (float(rows[k].mean()) if rows[k].notna().any() else None) for k in DIMENSIONS},
            "ndvi_max": float(e["veg_ndvi_max"]) if pd.notna(e.get("veg_ndvi_max")) else None,
            "dist_settlement_km": float(e["dist_settlement_km"]), "settlement": e["settlement_name"],
            "nearest_known": known["name"].iloc[near], "nearest_known_km": float(d[near]),
            "slope_mean_deg": float(e["topo__slope_mean_deg"]), "relief_m": float(e["topo__relief_m"]),
            "t_max_k": float(e["thermal__t_max_k"]) if pd.notna(e.get("thermal__t_max_k")) else None,
            "t_range_k": float(e["thermal__t_range_k"]) if pd.notna(e.get("thermal__t_range_k")) else None,
            "basalt_frac": float(e["geo__basalt_frac"]) if pd.notna(e.get("geo__basalt_frac")) else None,
            "dust_surface_ugm3": float(e["dust_surface_ugm3"]) if pd.notna(e.get("dust_surface_ugm3")) else None,
            "wind10m_ms": float(e["wind10m_ms"]) if pd.notna(e.get("wind10m_ms")) else None,
            "snow_mean": float(e["ice__water_frac"]) if pd.notna(e.get("ice__water_frac")) else None,
        })
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", type=Path, default=RESULTS_DIR)
    a = ap.parse_args()
    short = pd.read_csv(a.results / "candidates_shortlist.csv")
    earth, known = load_features("earth", FEATURES_DIR), load_known()
    res = []
    for body in ("moon", "mars"):
        res += details(short, select(short, body), body, earth, known)
    pd.set_option("display.width", 250)
    pd.DataFrame(res).drop(columns=["dims"]).round(2).to_csv(a.results / "candidate_profiles.csv", index=False)
    import json
    (a.results / "candidate_profiles.json").write_text(json.dumps(res, indent=2, ensure_ascii=False))
    for r in res:
        print(json.dumps(r, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
