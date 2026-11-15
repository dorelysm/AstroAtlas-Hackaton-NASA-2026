"""Slope and roughness from a DEM resampled onto a local grid in metres.

Pure numpy functions (no network), common to Earth, Moon and Mars.

Decisions (see docs/reference/nasa-apis.md):
  - The window is sampled on a local azimuthal-equidistant grid centred on the site, so
    the pixel size is isotropic in metres even near the poles.
  - Slope and roughness are computed over the SAME baseline (~500 m), so that Moon (LOLA 118 m),
    Mars (MOLA 463 m) and Earth are comparable. Fine detail is lost.
  - rough_1km_m = mean of the standard deviation of elevation in ~1 km blocks
    (includes the contribution of the local slope; it correlates with slope).
"""
import warnings

import numpy as np


def local_grid(lat0: float, lon0: float, half_m: float, spacing_m: float, radius_m: float):
    """Grid (rows from north to south, columns from west to east) around (lat0, lon0).

    Returns (lat, lon) in degrees; lon not normalised. Inverse azimuthal-equidistant projection.
    """
    n = int(round(half_m / spacing_m))
    offs = np.arange(-n, n + 1) * spacing_m
    x, y = np.meshgrid(offs, offs[::-1])
    phi0 = np.radians(np.clip(lat0, -89.999999, 89.999999))
    rho = np.hypot(x, y)
    c = rho / radius_m
    sin_c, cos_c = np.sin(c), np.cos(c)
    safe_rho = np.where(rho > 0, rho, 1.0)
    lat = np.arcsin(np.clip(cos_c * np.sin(phi0) + (y * sin_c / safe_rho) * np.cos(phi0), -1, 1))
    lon = np.radians(lon0) + np.arctan2(x * sin_c, rho * np.cos(phi0) * cos_c - y * np.sin(phi0) * sin_c)
    return np.degrees(lat), np.degrees(lon)


def _blocks(z: np.ndarray, k: int) -> np.ndarray:
    r, c = (z.shape[0] // k) * k, (z.shape[1] // k) * k
    return z[:r, :c].reshape(r // k, k, c // k, k).swapaxes(1, 2).reshape(r // k, c // k, k * k)


def block_mean(z: np.ndarray, k: int, min_valid: float = 0.5) -> np.ndarray:
    """Block average k x k; NaN if there are fewer than `min_valid` valid pixels."""
    if k <= 1:
        return z
    b = _blocks(z, k)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        mean = np.nanmean(b, axis=2)
    mean[np.isfinite(b).mean(axis=2) < min_valid] = np.nan
    return mean


def slope_deg(z: np.ndarray, spacing_m: float) -> np.ndarray:
    gy, gx = np.gradient(z, spacing_m)
    return np.degrees(np.arctan(np.hypot(gx, gy)))


def roughness_m(z: np.ndarray, spacing_m: float, box_m: float = 1000.0) -> float:
    """Mean of the standard deviation of z in blocks of ~box_m (minimum 2 x 2 pixels)."""
    k = max(2, int(round(box_m / spacing_m)))
    b = _blocks(z, k)
    if b.size == 0:
        return float("nan")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        std = np.nanstd(b, axis=2)
    std[np.isfinite(b).sum(axis=2) < 3] = np.nan
    return float(np.nanmean(std)) if np.isfinite(std).any() else float("nan")


# Slope thresholds for the area fractions. TO BE CONFIRMED with a source (landing/mobility).
FLAT_DEG = 5.0
STEEP_DEG = 15.0
FLAT_MEAN_SLOPE_DEG = 0.1  # below this, the slope aspect is undefined (0 is taken)
ROUGHNESS_BOXES_M = {"topo__rough_1km_m": 1000.0, "topo__rough_2km_m": 2000.0, "topo__rough_5km_m": 5000.0}
_FLAT_GRADIENT2 = np.tan(np.radians(1.0)) ** 2  # below 1° the curvature is taken as 0


def _nanmean(a: np.ndarray) -> float:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        return float(np.nanmean(a)) if np.isfinite(a).any() else float("nan")


def tri_m(z: np.ndarray) -> float:
    """Terrain ruggedness index (Riley, simplified): mean of |centre - neighbour| over the 8 neighbours."""
    if min(z.shape) < 3:
        return float("nan")
    c = z[1:-1, 1:-1]
    diffs = [np.abs(c - z[1 + dy : z.shape[0] - 1 + dy, 1 + dx : z.shape[1] - 1 + dx])
             for dy in (-1, 0, 1) for dx in (-1, 0, 1) if (dy, dx) != (0, 0)]
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        return _nanmean(np.nanmean(np.stack(diffs), axis=0))


def tpi_std_m(z: np.ndarray, size: int = 5) -> float:
    """Standard deviation of the topographic position index (centre - mean of neighbours in size x size)."""
    from scipy.ndimage import uniform_filter

    if min(z.shape) < size:
        return float("nan")
    valid = np.isfinite(z)
    z0 = np.where(valid, z, 0.0)
    n = size * size
    total = uniform_filter(z0, size, mode="nearest") * n
    cnt = uniform_filter(valid.astype(float), size, mode="nearest") * n
    n_nb = cnt - valid
    tpi = z - (total - z0) / np.where(n_nb > 0, n_nb, np.nan)
    tpi[n_nb < n * 0.5] = np.nan
    m = size // 2
    inner = tpi[m:-m, m:-m]
    return float(np.nanstd(inner)) if np.isfinite(inner).any() else float("nan")


def curvatures_per_km(p, q, r, s, t) -> tuple[float, float]:
    """Mean of |profile curvature| and |plan curvature| (1/km), Zevenbergen-Thorne.

    p, q = dz/dx(east), dz/dy(north); r, s, t = d2z/dx2, d2z/dxdy, d2z/dy2. Where the slope
    is < 1° curvature 0 is taken (the formula is unstable over flat terrain).
    """
    g2 = p**2 + q**2
    ok = g2 > _FLAT_GRADIENT2
    safe = np.where(ok, g2, 1.0)
    prof = -(p**2 * r + 2 * p * q * s + q**2 * t) / (safe * (1 + safe) ** 1.5)
    plan = (q**2 * r - 2 * p * q * s + p**2 * t) / safe**1.5
    prof, plan = np.where(ok, prof, 0.0), np.where(ok, plan, 0.0)
    finite = np.isfinite(g2)
    if not finite.any():
        return float("nan"), float("nan")
    return float(np.mean(np.abs(prof[finite])) * 1000), float(np.mean(np.abs(plan[finite])) * 1000)


def largest_flat_patch_km2(slope: np.ndarray, spacing_m: float, flat_deg: float = FLAT_DEG) -> float:
    """Area (km²) of the largest continuous patch (4-neighbour connectivity) with slope < flat_deg."""
    from scipy.ndimage import label

    mask = slope < flat_deg  # NaN -> False
    if not np.isfinite(slope).any():
        return float("nan")
    labels, n = label(mask)
    if n == 0:
        return 0.0
    return float(np.bincount(labels.ravel())[1:].max() * spacing_m**2 / 1e6)


def window_features(z: np.ndarray, spacing_m: float, baseline_m: float = 500.0, lat: float = 0.0) -> dict:
    """Topography features of an elevation window (m) with pixel of `spacing_m`.

    `lat` is used only to orient `aspect_equatorward` (towards the hemisphere's equator).
    z has rows from north to south and columns from west to east (as returned by `local_grid`).
    """
    f = max(1, int(round(baseline_m / spacing_m)))
    zb = block_mean(z, f)
    b = spacing_m * f
    out = {k: float("nan") for k in (
        "topo__slope_mean_deg", "topo__slope_p90_deg", "topo__frac_slope_lt5deg", "topo__frac_slope_gt15deg",
        "topo__flat_patch_km2", "topo__relief_m", "topo__elev_std_m", *ROUGHNESS_BOXES_M, "topo__tri_m",
        "topo__tpi_std_m", "topo__curv_profile_abs_per_km", "topo__curv_plan_abs_per_km",
        "topo__aspect_concentration", "topo__aspect_equatorward")}
    out.update(elev_mean_m=_nanmean(z), valid_frac=float(np.isfinite(z).mean()), baseline_m=float(b))
    if min(zb.shape) < 5 or not np.isfinite(zb).any():
        return out

    gy_row, p = np.gradient(zb, b)  # p = dz/d(east); gy_row = dz/d(row) (south grows with the row)
    q = -gy_row  # dz/d(norte)
    slope = np.degrees(np.arctan(np.hypot(p, q)))
    inner = (slice(1, -1), slice(1, -1))
    s_in = slope[inner]
    valid = np.isfinite(s_in)
    if valid.any():
        out["topo__slope_mean_deg"] = float(s_in[valid].mean())
        out["topo__slope_p90_deg"] = float(np.percentile(s_in[valid], 90))
        out["topo__frac_slope_lt5deg"] = float((s_in[valid] < FLAT_DEG).mean())
        out["topo__frac_slope_gt15deg"] = float((s_in[valid] > STEEP_DEG).mean())
        out["topo__flat_patch_km2"] = largest_flat_patch_km2(s_in, b)

    fin = zb[np.isfinite(zb)]
    out["topo__relief_m"] = float(np.percentile(fin, 98) - np.percentile(fin, 2))
    out["topo__elev_std_m"] = float(fin.std())
    for name, box in ROUGHNESS_BOXES_M.items():
        out[name] = roughness_m(zb, b, box)
    out["topo__tri_m"] = tri_m(zb)
    out["topo__tpi_std_m"] = tpi_std_m(zb)

    r = np.gradient(p, b, axis=1)  # d2z/dx2
    s = np.gradient(q, b, axis=1)  # d2z/dxdy
    t = np.gradient(gy_row, b, axis=0)  # d2z/dy2 (two sign changes cancel out)
    c = (slice(2, -2), slice(2, -2))
    out["topo__curv_profile_abs_per_km"], out["topo__curv_plan_abs_per_km"] = curvatures_per_km(
        p[c], q[c], r[c], s[c], t[c])

    w = np.hypot(p[inner], q[inner])
    w = np.where(valid, w, np.nan)
    if np.isfinite(w).any():
        if _nanmean(slope[inner]) >= FLAT_MEAN_SLOPE_DEG and np.nansum(w) > 0:
            pe, qn = np.nansum(-p[inner][valid]), np.nansum(-q[inner][valid])  # vector cuesta abajo
            out["topo__aspect_concentration"] = float(np.hypot(pe, qn) / np.nansum(w))
            hemi = 1.0 if lat >= 0 else -1.0  # equator = south in the north, north in the south
            out["topo__aspect_equatorward"] = float(hemi * np.nansum(q[inner][valid]) / np.nansum(w))
        else:
            # Flat terrain: with no slopes there is no preferred orientation. The neutral value is 0, NOT NaN: with NaN the PCA
            # of the topography does not score the row and the flattest cells (the most Mars-like) dropped out of the ranking.
            out["topo__aspect_concentration"] = 0.0
            out["topo__aspect_equatorward"] = 0.0
    return out
