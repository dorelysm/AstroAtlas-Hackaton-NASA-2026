"""Place names for Earth cells (country and region), in Spanish and English, without external services.

The boundaries come from Natural Earth (public domain, 1:110 million scale): countries (`ne_110m_admin_0_countries`) and geographic
regions (`ne_110m_geography_regions_polys`), with their names in Spanish (`NAME_ES`) and English (`NAME_EN`). They are simplified and
stored in `data/places.json` (versioned, so the app does not need the raw data). A curated name overrides the region name
(`CURATED_NAMES`).

    python -m astroatlas.places --build     # regenerates data/places.json from data/raw/naturalearth/
"""
import argparse
import json
from functools import lru_cache
from pathlib import Path

import numpy as np

from .config import RAW_DIR

JSON_PATH = Path(__file__).parent / "data" / "places.json"
RAW = RAW_DIR / "naturalearth"
LANGS = ("es", "en")

# Regions that work as a place name, in order of preference (continents and countries already say little).
CLASES = ["Desert", "Plateau", "Range/mtn", "Tundra", "Plain", "Basin", "Island", "Island group", "Geoarea", "Pen/cape", "Peninsula"]

# Proper names of places cited by the project documents: (name, lat, lon, radius in km, country in each language).
CURATED_NAMES = [
    ("Harrat ash-Shamah", 32.5, 37.5, 250.0, {"es": "Siria / Jordania", "en": "Syria / Jordan"}),
    ("Haruj", 27.5, 17.5, 200.0, {"es": "Libia", "en": "Libya"}),
]

# Fallback texts when there is no named region or country
NO_COUNTRY = {"es": "Sin país", "en": "No country"}
ZONA_DE = {"es": "Zona de {pais}", "en": "Area of {pais}"}
NO_NAME = {"es": "Zona sin nombre", "en": "Unnamed area"}


def _round_ring(ring, nd: int = 2) -> list:
    return [[round(x, nd), round(y, nd)] for x, y in ring]


def _polys(geom: dict) -> list:
    """List of outer rings (holes are ignored: at this scale they do not matter)."""
    if geom["type"] == "Polygon":
        return [_round_ring(geom["coordinates"][0])]
    return [_round_ring(p[0]) for p in geom["coordinates"]]


def _title(name: str) -> str:
    return name.capitalize() if name.isupper() else name[:1].upper() + name[1:]


def build() -> dict:
    c = json.loads((RAW / "ne_110m_admin_0_countries.geojson").read_text(encoding="utf-8"))
    r = json.loads((RAW / "ne_110m_geography_regions_polys.geojson").read_text(encoding="utf-8"))
    paises = []
    for f in c["features"]:
        if not f["geometry"]:
            continue
        p = f["properties"]
        paises.append({"nombre": {"es": p.get("NAME_ES") or p["NAME"], "en": p.get("NAME_EN") or p["NAME"]}, "polys": _polys(f["geometry"])})
    regiones = []
    for f in r["features"]:
        p = f["properties"]
        if p["FEATURECLA"] not in CLASES:
            continue
        regiones.append({"nombre": {"es": _title(p.get("NAME_ES") or p["NAME"]), "en": _title(p.get("NAME_EN") or p["NAME"])},
                         "clase": p["FEATURECLA"], "polys": _polys(f["geometry"])})
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
    """Point in polygon by ray casting (the Natural Earth rings do not cross the antimeridian at 1:110m)."""
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
def label(lat: float, lon: float, lang: str = "en") -> tuple[str, str]:
    """(place, country) of a point in language `lang` ("es" or "en"). `lon` in -180..180 or 0..360."""
    lang = lang if lang in LANGS else "en"
    lon = ((lon + 180.0) % 360.0) - 180.0
    d = _data()
    pais = next((p["nombre"] for p in d["paises"] if _contiene(p, lat, lon)), None)
    if pais is None:  # coast or sea ice that the 1:110m map leaves out: country with the nearest vertex, if within < 700 km
        best = min(((_km(lat, lon, y, x), p["nombre"]) for p in d["paises"] for r in p["_p"] for x, y in r[::3]), default=(1e9, None))
        pais = best[1] if best[0] < 700 else None
    pais_t = pais[lang] if pais else None
    for nombre, la, lo, radio, curated_country in CURATED_NAMES:
        if _km(lat, lon, la, lo) <= radio:
            return nombre, curated_country[lang]
    region = None
    for clase in CLASES:  # among those of the best class, the smallest (Hawaii before Polynesia)
        dentro = [r for r in d["regiones"] if r["clase"] == clase and _contiene(r, lat, lon)]
        if dentro:
            region = min(dentro, key=lambda r: sum((b[1] - b[0]) * (b[3] - b[2]) for b in r["_bb"]))["nombre"][lang]
            break
    lugar = region or (ZONA_DE[lang].format(pais=pais_t) if pais_t else NO_NAME[lang])
    return lugar, pais_t or NO_COUNTRY[lang]


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--build", action="store_true")
    if ap.parse_args().build:
        o = build()
        print(f"{len(o['paises'])} países y {len(o['regiones'])} regiones -> {JSON_PATH} ({JSON_PATH.stat().st_size / 1e3:.0f} kB)")
