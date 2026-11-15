"""Minimal ODE REST client (PDS Geosciences) to locate Moon and Mars products.

Returns metadata and download links, NOT values. The product has to be downloaded and read
(GDAL/rasterio). See docs/reference/nasa-apis.md. East-positive longitudes 0..360.
"""
import urllib.parse

import pandas as pd

from .http import get_json

ODE_URL = "https://oderest.rsl.wustl.edu/live2/"  # the trailing slash is required
KEEP = ["Product_name", "Map_resolution", "Center_latitude", "Center_longitude",
        "ProductURL", "LabelURL", "FilesURL"]

# (ihid, iid, pt) combinations checked with results=c (14 Nov 2026)
PRODUCTS = {
    "moon_diviner_rdr": ("moon", "LRO", "DLRE", "RDR"),
    "mars_mola_megdr": ("mars", "MGS", "MOLA", "MEGDR"),
}


def _query(params: dict) -> dict:
    res = get_json(f"{ODE_URL}?{urllib.parse.urlencode(params)}")["ODEResults"]
    if res.get("Status") != "Success":
        raise RuntimeError(f"ODE: {res.get('Error', res.get('Status'))}")
    return res


def _params(target, ihid, iid, pt, bbox, results, limit) -> dict:
    p = {"target": target, "query": "product", "results": results, "output": "JSON",
         "ihid": ihid, "iid": iid, "pt": pt}
    if bbox:
        p.update(zip(("minlat", "maxlat", "westernlon", "easternlon"), bbox))
    if limit:
        p["limit"] = limit
    return p


def count(target, ihid, iid, pt, bbox=None) -> int:
    """bbox = (minlat, maxlat, west, east) with longitudes 0..360."""
    return int(_query(_params(target, ihid, iid, pt, bbox, "c", None))["Count"])


def products(target, ihid, iid, pt, bbox=None, limit: int = 10) -> pd.DataFrame:
    res = _query(_params(target, ihid, iid, pt, bbox, "m", limit))
    prods = res.get("Products", {}).get("Product", [])
    if isinstance(prods, dict):  # with a single ODE result it returns a dict
        prods = [prods]
    return pd.DataFrame([{k: p.get(k) for k in KEEP} for p in prods], columns=KEEP)


def bbox_around(lat: float, lon_east: float, half_deg: float = 1.0) -> tuple[float, float, float, float]:
    return (max(lat - half_deg, -90), min(lat + half_deg, 90),
            (lon_east - half_deg) % 360, (lon_east + half_deg) % 360)
