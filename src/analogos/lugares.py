"""Nombres de lugar para las celdas de la Tierra (país y región), sin servicios externos.

Los límites salen de Natural Earth (dominio público, escala 1:110 millones): países (`ne_110m_admin_0_countries`) y regiones
geográficas (`ne_110m_geography_regions_polys`). Se simplifican y se guardan en `data/lugares.json` (versionado, para que la app
no necesite los datos crudos). Un nombre curado manda sobre el de la región (`NOMBRES_CURADOS`).

    python -m analogos.lugares --build     # regenera data/lugares.json desde data/raw/naturalearth/
"""
import argparse
import json
from functools import lru_cache
from pathlib import Path

import numpy as np

from .config import RAW_DIR

JSON_PATH = Path(__file__).parent / "data" / "lugares.json"
RAW = RAW_DIR / "naturalearth"

# Regiones que sirven como nombre de lugar, por orden de preferencia (los continentes y los países ya dicen poco).
CLASES = ["Desert", "Plateau", "Range/mtn", "Tundra", "Plain", "Basin", "Island", "Island group", "Geoarea", "Pen/cape", "Peninsula"]

# Nombres propios de lugares que citan los documentos del proyecto: (nombre, lat, lon, radio en km). Mandan sobre la región.
NOMBRES_CURADOS = [
    ("Harrat ash-Shamah", 32.5, 37.5, 250.0, "Siria / Jordania"),
    ("Haruj", 27.5, 17.5, 200.0, "Libia"),
]


def _round_ring(ring, nd: int = 2) -> list:
    return [[round(x, nd), round(y, nd)] for x, y in ring]


def _polys(geom: dict) -> list:
    """Lista de anillos exteriores (los huecos se ignoran: a esta escala no importan)."""
    if geom["type"] == "Polygon":
        return [_round_ring(geom["coordinates"][0])]
    return [_round_ring(p[0]) for p in geom["coordinates"]]


def _title(name: str) -> str:
    return name.capitalize() if name.isupper() else name[:1].upper() + name[1:]


def build() -> dict:
    c = json.loads((RAW / "ne_110m_admin_0_countries.geojson").read_text(encoding="utf-8"))
    r = json.loads((RAW / "ne_110m_geography_regions_polys.geojson").read_text(encoding="utf-8"))
    paises = [{"nombre": f["properties"].get("NAME_ES") or f["properties"]["NAME"], "polys": _polys(f["geometry"])}
              for f in c["features"] if f["geometry"]]
    regiones = [{"nombre": _title(f["properties"].get("NAME_ES") or f["properties"]["NAME"]), "clase": f["properties"]["FEATURECLA"],
                 "polys": _polys(f["geometry"])} for f in r["features"] if f["properties"]["FEATURECLA"] in CLASES]
    out = {"paises": paises, "regiones": regiones, "fuente": "Natural Earth 1:110m (dominio público)"}
    JSON_PATH.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    return out


@lru_cache(maxsize=1)
def _data() -> dict:
    d = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    for grupo in ("paises", "regiones"):
        for item in d[grupo]:
            item["_p"] = [np.asarray(p, dtype=float) for p in item["polys"]]
            item["_bb"] = [(p[:, 0].min(), p[:, 0].max(), p[:, 1].min(), p[:, 1].max()) for p in item["_p"]]
    return d


def _inside(ring: np.ndarray, x: float, y: float) -> bool:
    """Punto en polígono por trazado de rayos (los anillos de Natural Earth no cruzan el antimeridiano a 1:110m)."""
    xs, ys = ring[:, 0], ring[:, 1]
    x2, y2 = np.roll(xs, -1), np.roll(ys, -1)
    cruza = (ys > y) != (y2 > y)
    with np.errstate(divide="ignore", invalid="ignore"):
        xi = xs + (y - ys) * (x2 - xs) / (y2 - ys)
    return bool(np.count_nonzero(cruza & (x < xi)) % 2)


def _contiene(item: dict, lat: float, lon: float) -> bool:
    return any(b[0] <= lon <= b[1] and b[2] <= lat <= b[3] and _inside(p, lon, lat) for p, b in zip(item["_p"], item["_bb"]))


def _km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    p = np.pi / 180
    a = np.sin((lat2 - lat1) * p / 2) ** 2 + np.cos(lat1 * p) * np.cos(lat2 * p) * np.sin((lon2 - lon1) * p / 2) ** 2
    return float(12742 * np.arcsin(np.sqrt(a)))


@lru_cache(maxsize=4096)
def etiqueta(lat: float, lon: float) -> tuple[str, str]:
    """(lugar, país) de un punto. `lon` en -180..180 o 0..360. Sin país conocido (mar, hielo) devuelve «Sin país»."""
    lon = ((lon + 180.0) % 360.0) - 180.0
    d = _data()
    pais = next((p["nombre"] for p in d["paises"] if _contiene(p, lat, lon)), None)
    if pais is None:  # costa o hielo marino que el mapa a 1:110m deja fuera: país con el vértice más cercano, si está a < 700 km
        best = min(((_km(lat, lon, y, x), p["nombre"]) for p in d["paises"] for r in p["_p"] for x, y in r[::3]), default=(1e9, None))
        pais = best[1] if best[0] < 700 else None
    for nombre, la, lo, radio, pais_curado in NOMBRES_CURADOS:
        if _km(lat, lon, la, lo) <= radio:
            return nombre, pais_curado
    region = None
    for clase in CLASES:  # entre las de la mejor clase, la más pequeña (Hawái antes que Polinesia)
        dentro = [r for r in d["regiones"] if r["clase"] == clase and _contiene(r, lat, lon)]
        if dentro:
            region = min(dentro, key=lambda r: sum((b[1] - b[0]) * (b[3] - b[2]) for b in r["_bb"]))["nombre"]
            break
    lugar = region or (f"Zona de {pais}" if pais else "Zona sin nombre")
    return lugar, pais or "Sin país"


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--build", action="store_true")
    if ap.parse_args().build:
        o = build()
        print(f"{len(o['paises'])} países y {len(o['regiones'])} regiones -> {JSON_PATH} ({JSON_PATH.stat().st_size / 1e3:.0f} kB)")
