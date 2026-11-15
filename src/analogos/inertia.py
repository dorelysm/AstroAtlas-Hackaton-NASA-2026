"""Experimento: dimensión de inercia térmica (docs/PREREGISTRO_INERCIA.md).

Marte: mapa nocturno de inercia térmica de MGS-TES (PDS mgs-m-tes-5-timap-v1, Putzig y Mellon 2007), mediana en una ventana de ±25 km,
convertida a PERCENTIL frente a Marte. Tierra: proxy aparente sin albedo 1/(T_día − T_noche) de MODIS (rango diurno ya calculado),
convertido a percentil frente a las 951 celdas. Se comparan percentiles DENTRO de cada cuerpo (analogía relativa, no valores absolutos).
La Luna no tiene la dimensión.

Es un EXPERIMENTO: la dimensión se añade solo dentro del contexto `extra_dimension` y NO modifica el modelo del proyecto salvo que el
criterio preregistrado se cumpla y se decida adoptarla.

    python -m analogos.inertia
"""
import contextlib
import shutil
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd

from . import ablation, config
from .config import FEATURES_DIR, RAW_DIR, RESULTS_DIR
from .validation_ext import boot_mean, extended_known, extended_sites

TES_DIR = RAW_DIR / "tes_ti" / "x" / "mgst_9001" / "data"
PPD = 20.0          # píxeles por grado
KM_PER_PX = 2.96    # km por píxel en el ecuador
HALF_KM = 25.0
MAX_ABS_LAT = 80.0
FEATURE = "inertia__ti_pct"


def load_tes_night(directory: Path = TES_DIR) -> tuple[np.ndarray, np.ndarray]:
    """(TI nocturna, máscara de píxeles no interpolados). Valores 0 = sin dato."""
    ti = np.fromfile(directory / "global_ti_night_2007.img", dtype=">i2").reshape(3600, 7200).astype("float32")
    msk = np.fromfile(directory / "global_ti_msk_night_2007.img", dtype="u1").reshape(3600, 7200)
    ti[(msk != 1) | (ti <= 0)] = np.nan
    return ti, msk


def window_median(ti: np.ndarray, lat: float, lon: float, half_km: float = HALF_KM) -> float:
    """Mediana de los píxeles válidos a ±half_km (longitud 0-360 este o -180..180)."""
    lon = ((lon + 180.0) % 360.0) - 180.0
    i0 = (90.0 - lat) * PPD
    j0 = (lon + 180.0) * PPD
    di = half_km / KM_PER_PX
    dj = di / max(np.cos(np.radians(lat)), 0.05)
    ii = np.clip(np.arange(int(np.floor(i0 - di)), int(np.ceil(i0 + di)) + 1), 0, ti.shape[0] - 1)
    jj = np.arange(int(np.floor(j0 - dj)), int(np.ceil(j0 + dj)) + 1) % ti.shape[1]
    v = ti[np.ix_(ii, jj)]
    v = v[np.isfinite(v)]
    return float(np.median(v)) if v.size else float("nan")


def mars_reference(ti: np.ndarray) -> np.ndarray:
    """Valores válidos ordenados de todo Marte con |latitud| <= 80° (referencia de los percentiles)."""
    lat = 90.0 - (np.arange(ti.shape[0]) + 0.5) / PPD
    rows = np.abs(lat) <= MAX_ABS_LAT
    v = ti[rows].ravel()
    return np.sort(v[np.isfinite(v)])


def percentile(value, sorted_ref: np.ndarray) -> np.ndarray:
    """Fracción de la referencia por debajo de `value` (0-1); NaN se queda NaN."""
    v = np.asarray(value, dtype=float)
    out = np.searchsorted(sorted_ref, v, side="left") / len(sorted_ref)
    return np.where(np.isfinite(v), out, np.nan)


def earth_proxy(t_range_k) -> np.ndarray:
    """Proxy aparente sin albedo: 1/(T_día − T_noche). Rango no positivo o ausente = NaN."""
    r = np.asarray(t_range_k, dtype=float)
    return np.where(np.isfinite(r) & (r > 0), 1.0 / np.where(r > 0, r, np.nan), np.nan)


def add_earth_inertia(df: pd.DataFrame, ref_cells: pd.DataFrame) -> pd.DataFrame:
    ref = np.sort(earth_proxy(ref_cells["thermal__t_range_k"])[np.isfinite(earth_proxy(ref_cells["thermal__t_range_k"]))])
    out = df.copy()
    out[FEATURE] = percentile(earth_proxy(df["thermal__t_range_k"]), ref)
    return out


def add_mars_inertia(mars: pd.DataFrame, ti: np.ndarray) -> pd.DataFrame:
    ref = mars_reference(ti)
    out = mars.copy()
    vals = [window_median(ti, r.lat, r.lon) for r in out.itertuples()]
    out["ti_night_median"] = vals
    out[FEATURE] = percentile(vals, ref)
    return out


@contextlib.contextmanager
def extra_dimension(name: str = "inertia", features: tuple[str, ...] = (FEATURE,)):
    """Añade temporalmente una dimensión al modelo (se restaura al salir). Los módulos comparten estos objetos, así que se muta en sitio."""
    config.DIMENSIONS[name] = list(features)
    added = [f for f in features if f not in config.FEATURES]
    config.FEATURES.extend(added)
    config.DEFAULT_WEIGHTS[name] = 1.0
    old_dims = ablation.DIMS
    ablation.DIMS = list(config.DIMENSIONS)
    try:
        yield
    finally:
        ablation.DIMS = old_dims
        config.DEFAULT_WEIGHTS.pop(name, None)
        for f in added:
            config.FEATURES.remove(f)
        config.DIMENSIONS.pop(name, None)


def build_experiment_dir() -> tuple[Path, pd.DataFrame, pd.DataFrame]:
    """Carpeta temporal con las características + la dimensión de inercia. Devuelve (carpeta, sitios ampliados, conocidos ampliados)."""
    ti, _ = load_tes_night()
    earth = pd.read_parquet(FEATURES_DIR / "earth.parquet")
    sites = add_earth_inertia(extended_sites(), earth)
    tmp = Path(tempfile.mkdtemp())
    add_earth_inertia(earth, earth).to_parquet(tmp / "earth.parquet", index=False)
    add_mars_inertia(pd.read_parquet(FEATURES_DIR / "mars.parquet"), ti).to_parquet(tmp / "mars.parquet", index=False)
    pd.read_parquet(FEATURES_DIR / "moon.parquet").assign(**{FEATURE: np.nan}).to_parquet(tmp / "moon.parquet", index=False)
    sites.to_parquet(tmp / "earth_sites.parquet", index=False)
    return tmp, sites, extended_known()


def paired_diff(raw: pd.DataFrame, body: str, a: str, b: str, n_boot: int = 4000, seed: int = 0) -> dict:
    """Diferencia pareada por análogo de u medio entre las configuraciones a y b, con IC por bootstrap sobre los análogos."""
    g = raw[raw["body"] == body].groupby(["config", "analog"])["u"].mean().unstack("config")
    d = (g[a] - g[b]).dropna().to_numpy()
    m, lo, hi = boot_mean(d, n_boot, seed)
    return {"n": len(d), "diff": m, "lo": lo, "hi": hi}


def main() -> None:
    tmp, sites, known = build_experiment_dir()
    try:
        original = ablation.load_known
        ablation.load_known = lambda: known
        try:
            with extra_dimension():
                raw = ablation.run(features_dir=tmp)
        finally:
            ablation.load_known = original
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    raw.to_csv(RESULTS_DIR / "inertia_raw.csv", index=False)
    pd.set_option("display.width", 220)
    m = raw[raw["body"] == "mars"].groupby(["config", "analog"])["u"].mean().unstack("config")
    print("u medio de Marte por configuración (media sobre análogos), con IC 95 % por bootstrap:")
    rows = []
    for cfg in ("todas", "sin inertia", "solo inertia", "solo topo", "solo geo", "solo ice"):
        mean, lo, hi = boot_mean(m[cfg].dropna().to_numpy())
        rows.append({"config": cfg, "n": int(m[cfg].notna().sum()), "u_medio": mean, "ic_lo": lo, "ic_hi": hi})
    res = pd.DataFrame(rows)
    print(res.round(3).to_string(index=False))
    pdiff = paired_diff(raw, "mars", "todas", "sin inertia")
    print(f"\nDiferencia pareada 'todas + inercia' - 'sin inercia': {pdiff['diff']:+.3f} (IC {pdiff['lo']:+.3f} a {pdiff['hi']:+.3f}, n={pdiff['n']})")
    cold = ["Dry Valleys (Antartida)", "Axel Heiberg (McGill Arctic Research Station)", "Svalbard", "Eureka (Ellesmere)"]
    c = m.loc[[x for x in cold if x in m.index], ["sin inertia", "todas", "solo inertia"]]
    print("\nAnálogos fríos (u):")
    print(c.round(2).to_string())
    print("\nTodos los análogos (u, Marte):")
    print(m[["sin inertia", "todas", "solo inertia"]].round(2).sort_values("solo inertia", ascending=False).to_string())
    res.to_csv(RESULTS_DIR / "inertia_resumen.csv", index=False)
    pd.DataFrame([pdiff]).to_csv(RESULTS_DIR / "inertia_diff_pareada.csv", index=False)


if __name__ == "__main__":
    main()
