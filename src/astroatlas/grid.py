"""Common lat-lon grid. (The H3 option is still open; see docs/archive/project-plan.md.)"""
import numpy as np
import pandas as pd


def make_grid(step_deg: float, body: str) -> pd.DataFrame:
    """Regular grid with cell centres. `cell_id` = '<body>_<i>_<j>'."""
    lats = np.arange(-90 + step_deg / 2, 90, step_deg)
    lons = np.arange(-180 + step_deg / 2, 180, step_deg)
    lat, lon = np.meshgrid(lats, lons, indexing="ij")
    ii, jj = np.meshgrid(np.arange(len(lats)), np.arange(len(lons)), indexing="ij")
    ids = [f"{body}_{i}_{j}" for i, j in zip(ii.ravel(), jj.ravel())]
    return pd.DataFrame(
        {"cell_id": ids, "body": body, "lat": lat.ravel(), "lon": lon.ravel()}
    )
