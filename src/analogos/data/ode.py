"""Cliente mínimo de ODE REST (PDS Geosciences) para localizar productos de Luna y Marte.

Devuelve metadatos y enlaces de descarga, NO valores. Hay que bajar el producto y leerlo
(GDAL/rasterio). Ver docs/APIS.md. Longitudes este-positivas 0..360.
"""
import urllib.parse

import pandas as pd

from .http import get_json

ODE_URL = "https://oderest.rsl.wustl.edu/live2/"  # la barra final es necesaria
KEEP = ["Product_name", "Map_resolution", "Center_latitude", "Center_longitude",
        "ProductURL", "LabelURL", "FilesURL"]

# Combinaciones (ihid, iid, pt) comprobadas con results=c (14-nov-2026)
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
    """bbox = (minlat, maxlat, oeste, este) con longitudes 0..360."""
    return int(_query(_params(target, ihid, iid, pt, bbox, "c", None))["Count"])


def products(target, ihid, iid, pt, bbox=None, limit: int = 10) -> pd.DataFrame:
    res = _query(_params(target, ihid, iid, pt, bbox, "m", limit))
    prods = res.get("Products", {}).get("Product", [])
    if isinstance(prods, dict):  # con un solo resultado ODE devuelve un dict
        prods = [prods]
    return pd.DataFrame([{k: p.get(k) for k in KEEP} for p in prods], columns=KEEP)


def bbox_around(lat: float, lon_east: float, half_deg: float = 1.0) -> tuple[float, float, float, float]:
    return (max(lat - half_deg, -90), min(lat + half_deg, 90),
            (lon_east - half_deg) % 360, (lon_east + half_deg) % 360)
