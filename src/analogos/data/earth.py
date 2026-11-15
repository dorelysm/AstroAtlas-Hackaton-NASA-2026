"""Datos de la Tierra (responsable: persona 2).

  - Topografía (`topo__*`): Copernicus GLO-90 (ESA, AWS Open Data, sin login), ver copernicus.py.
  - Térmica e hielo: POWER (temperatura del AIRE y precipitación, PROXY; ver docs/APIS.md).
  - CMR: búsqueda de granulos (MODIS LST, NASADEM...) para cuando haya login de Earthdata.
Faltan `geo__*` (NaN) y una temperatura de SUPERFICIE (MODIS LST).

    python -m analogos.data.earth                  # malla de 5°, solo tierra firme
    python -m analogos.data.earth --step 10 --no-power
"""
import argparse
import math
import urllib.parse
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import pandas as pd

from ..config import FEATURES, FEATURES_WRITE_DIR, KNOWN_CSV
from ..grid import make_grid
from .copernicus import CopernicusDem
from .dem import site_topography
from .http import get_json

POWER_URL = "https://power.larc.nasa.gov/api/temporal/climatology/point"
POWER_PARAMS = "T2M_MAX,T2M_MIN,PRECTOTCORR"
CMR_URL = "https://cmr.earthdata.nasa.gov/search"
POWER_MISSING = -999.0
PRECIP_FULL_MM_DAY = 5.0  # a 5 mm/día o más, ice__water_frac = 1 (proxy provisional)
DIAGNOSTICS = ["elev_mean_m", "valid_frac", "baseline_m"]  # no son features del modelo


# --- POWER: clima por punto ---
def power_url(lat: float, lon: float) -> str:
    q = {"parameters": POWER_PARAMS, "community": "RE", "latitude": lat, "longitude": lon, "format": "JSON"}
    return f"{POWER_URL}?{urllib.parse.urlencode(q)}"


def _val(params: dict, name: str) -> float:
    v = params.get(name, {}).get("ANN")
    return math.nan if v is None or v == POWER_MISSING else float(v)


def parse_power(payload: dict) -> dict:
    """Respuesta de POWER -> features del contrato.

    OJO: T2M es temperatura del AIRE a 2 m, no de la superficie (Diviner/MODIS LST sí lo son).
    ANN de T2M_MAX/T2M_MIN es el extremo de las medias mensuales.
    """
    p = payload["properties"]["parameter"]
    tmax, tmin, precip = _val(p, "T2M_MAX"), _val(p, "T2M_MIN"), _val(p, "PRECTOTCORR")
    return {
        "thermal__t_max_k": tmax + 273.15,
        "thermal__t_range_k": tmax - tmin,
        "ice__water_frac": float(np.clip(precip / PRECIP_FULL_MM_DAY, 0, 1)) if not math.isnan(precip) else math.nan,
    }


def fetch_power_point(lat: float, lon: float) -> dict:
    return parse_power(get_json(power_url(lat, lon)))


def add_power(cells: pd.DataFrame, workers: int = 4) -> pd.DataFrame:
    def one(row):
        try:
            return fetch_power_point(row.lat, row.lon)
        except RuntimeError:  # punto sin dato: NaN, no se imputa
            return {}

    with ThreadPoolExecutor(max_workers=workers) as ex:
        results = list(ex.map(one, cells.itertuples()))
    vals = pd.DataFrame(results, index=cells.index).reindex(columns=["thermal__t_max_k", "thermal__t_range_k",
                                                                    "ice__water_frac"])
    return cells.assign(**{c: vals[c] for c in vals})


# --- Topografía: Copernicus DEM ---
def build_topography(cells: pd.DataFrame, half_km: float = 25.0, baseline_m: float = 500.0,
                     workers: int = 8) -> pd.DataFrame:
    """Features topo__* (+ diagnósticos) para cada celda. Una celda que falla queda en NaN y se avisa."""
    dem, failures = CopernicusDem(), []

    def one(row):
        try:
            return site_topography(dem, row.lat, row.lon, half_km, baseline_m)
        except Exception as e:  # noqa: BLE001  red, GDAL...: no tumbar todo el lote
            failures.append((row.cell_id, repr(e)))
            return {}

    with ThreadPoolExecutor(max_workers=workers) as ex:
        results = list(ex.map(one, cells.itertuples()))
    if failures:  # segunda pasada, con menos hilos, solo de las celdas que fallaron (las teselas ya leídas están en caché)
        print(f"{len(failures)} celdas fallaron; reintentando con 2 hilos...")
        retry_ids = {cid for cid, _ in failures}
        failures.clear()
        todo = [(i, row) for i, row in enumerate(cells.itertuples()) if row.cell_id in retry_ids]
        with ThreadPoolExecutor(max_workers=2) as ex:
            for (i, _), res in zip(todo, ex.map(lambda t: one(t[1]), todo)):
                results[i] = res
    if failures:
        print(f"AVISO: {len(failures)} celdas sin topografía por error, p. ej. {failures[0]}")
    return pd.DataFrame(results, index=cells.index)


def is_flat_water(df: pd.DataFrame) -> pd.Series:
    """Celdas cuya ventana es AGUA (mar, lagos, mares interiores): Copernicus aplana las masas de agua a una cota
    constante, así que sin este filtro salen como 'llanuras perfectas'. Criterio: relieve local < 1 m a CUALQUIER
    altitud (antes solo a ~0 m, y dejaba pasar lagos como el Michigan o el Caspio). Con los datos de la malla de 5°,
    el terreno llano real más plano (hielo antártico, llanuras, humedales) tiene relieve >= 4 m, así que hay margen."""
    return df["topo__relief_m"] < 1.0


is_flat_ocean = is_flat_water  # nombre anterior, conservado por compatibilidad


def build_features(step_deg: float = 5.0, workers: int = 8, topo: bool = True, power: bool = True,
                   min_valid: float = 0.5, cells: pd.DataFrame | None = None) -> pd.DataFrame:
    """Tabla del contrato para la Tierra.

    Con topo=True se descartan las celdas con menos de `min_valid` de DEM válido (océano, sin tesela).
    POWER solo se consulta para las celdas que quedan. `cells` permite pasar puntos propios.
    """
    df = make_grid(step_deg, "earth") if cells is None else cells.copy()
    if topo:
        df = pd.concat([df, build_topography(df, workers=workers)], axis=1)
        df = df[(df["valid_frac"].fillna(0) >= min_valid) & ~is_flat_water(df)]
    if power:
        df = add_power(df, workers=min(workers, 4))  # POWER limita con 429: pocas conexiones
    for col in FEATURES:  # dimensiones aún sin extraer quedan como NaN
        if col not in df:
            df[col] = np.nan
    return df.reset_index(drop=True)


def known_analog_cells(path=KNOWN_CSV) -> pd.DataFrame:
    k = pd.read_csv(path)
    return pd.DataFrame({"cell_id": [f"earth_known_{i}" for i in range(len(k))], "body": "earth",
                         "lat": k["lat"], "lon": k["lon"], "name": k["name"]})


def download() -> None:
    """Pendiente: MODIS LST con earthaccess (necesita login Earthdata)."""
    raise NotImplementedError


# --- CMR: localizar datasets y granulos (sin login para buscar) ---
def cmr_collections(short_name: str, page_size: int = 5) -> list[dict]:
    q = urllib.parse.urlencode({"short_name": short_name, "page_size": page_size})
    entries = get_json(f"{CMR_URL}/collections.json?{q}")["feed"]["entry"]
    return [{"entry_id": e["entry_id"], "title": e["dataset_id"], "cloud_hosted": e.get("cloud_hosted")} for e in entries]


def cmr_granules(short_name: str, bbox: tuple[float, float, float, float], page_size: int = 5) -> list[dict]:
    """bbox = (oeste, sur, este, norte). Devuelve título y enlaces de descarga de cada granulo."""
    q = urllib.parse.urlencode(
        {"short_name": short_name, "bounding_box": ",".join(map(str, bbox)), "page_size": page_size}
    )
    entries = get_json(f"{CMR_URL}/granules.json?{q}")["feed"]["entry"]
    return [
        {"title": e["title"], "links": [l["href"] for l in e.get("links", []) if "data#" in l.get("rel", "")]}
        for e in entries
    ]


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--step", type=float, default=5.0, help="paso de la malla en grados")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--no-topo", action="store_true")
    ap.add_argument("--no-power", action="store_true")
    ap.add_argument("--no-sites", action="store_true", help="no calcular los análogos conocidos")
    a = ap.parse_args()
    FEATURES_WRITE_DIR.mkdir(parents=True, exist_ok=True)

    out = build_features(a.step, a.workers, topo=not a.no_topo, power=not a.no_power)
    out.to_parquet(FEATURES_WRITE_DIR / "earth.parquet", index=False)
    print(f"earth.parquet: {len(out)} celdas (malla {a.step}°)")

    if not a.no_sites:  # análogos conocidos: SOLO para comparar/validar, no se mezclan con la malla
        sites = build_features(cells=known_analog_cells(), workers=a.workers, topo=not a.no_topo,
                               power=not a.no_power, min_valid=0.0)
        sites.to_parquet(FEATURES_WRITE_DIR / "earth_sites.parquet", index=False)
        print(f"earth_sites.parquet: {len(sites)} análogos conocidos")
