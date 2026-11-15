import numpy as np
import pandas as pd
import pytest

from analogos.topography import block_mean, local_grid, roughness_m, slope_deg, window_features

R = 100_000.0  # radio de un cuerpo de juguete (m)


def test_plane_slope_and_flat_roughness():
    n, h = 101, 500.0
    y = np.arange(n)[::-1] * h
    z = np.tile((0.1 * y)[:, None], (1, n))  # sube hacia el norte: pendiente = atan(0.1)
    assert np.nanmean(slope_deg(z, h)) == pytest.approx(np.degrees(np.arctan(0.1)), abs=1e-6)
    f = window_features(z, h, baseline_m=500)
    assert f["topo__slope_mean_deg"] == pytest.approx(5.71, abs=0.05)
    assert f["valid_frac"] == 1.0


def test_flat_terrain_zero_slope_and_roughness():
    f = window_features(np.full((80, 80), 1234.0), 118.0)
    assert f["topo__slope_mean_deg"] == pytest.approx(0, abs=1e-9)
    assert f["topo__rough_1km_m"] == pytest.approx(0, abs=1e-9)


def test_baseline_is_common_across_resolutions():
    # misma superficie suave muestreada a 118 m y a 463 m: base efectiva ~500 m en ambos
    assert window_features(np.zeros((200, 200)), 118.45)["baseline_m"] == pytest.approx(473.8, abs=0.1)
    assert window_features(np.zeros((60, 60)), 463.09)["baseline_m"] == pytest.approx(463.09, abs=0.1)


def test_roughness_grows_with_noise():
    rng = np.random.default_rng(0)
    quiet = roughness_m(rng.normal(0, 1, (120, 120)), 500)
    loud = roughness_m(rng.normal(0, 20, (120, 120)), 500)
    assert loud > 10 * quiet


def test_nan_handling():
    z = np.full((40, 40), 5.0)
    z[:, :30] = np.nan
    assert np.isnan(block_mean(z, 4)[0, 0])
    f = window_features(z, 500)
    assert 0 < f["valid_frac"] < 0.5


def test_local_grid_center_and_offset():
    lat, lon = local_grid(10.0, 20.0, 5000, 1000, R)
    assert lat.shape == (11, 11)
    assert lat[5, 5] == pytest.approx(10.0) and lon[5, 5] == pytest.approx(20.0)
    assert lat[0, 5] > 10 > lat[-1, 5]  # fila 0 = norte
    assert lon[5, 0] < 20 < lon[5, -1]  # columna 0 = oeste
    dlat = np.radians(lat[0, 5] - 10.0) * R
    assert dlat == pytest.approx(5000, rel=1e-3)


@pytest.mark.parametrize("lat0", [90.0, -90.0, -89.9])
def test_local_grid_at_poles_is_valid(lat0):
    lat, lon = local_grid(lat0, 0.0, 20_000, 1000, R)
    assert np.isfinite(lat).all() and np.isfinite(lon).all()
    assert np.abs(lat).max() <= 90.0


def test_dem_roundtrip_with_geotiff(tmp_path):
    rasterio = pytest.importorskip("rasterio")
    from rasterio.transform import from_origin

    from analogos.data.dem import RasterDem, site_topography

    width, height = 628, 314
    res = 2 * np.pi * R / width  # ~1000 m; así width·res = 2πR exacto
    ys = (height / 2 - (np.arange(height) + 0.5)) * res  # y de cada fila (m)
    data = np.tile((0.1 * ys)[:, None], (1, width)).astype("int16")  # pendiente 0.1
    path = tmp_path / "toy.tif"
    with rasterio.open(path, "w", driver="GTiff", height=height, width=width, count=1, dtype="int16",
                       crs="+proj=eqc +R=100000 +units=m", nodata=-32768,
                       transform=from_origin(-np.pi * R, np.pi * R / 2, res, res)) as dst:
        dst.write(data, 1)

    with RasterDem(str(path)) as dem:
        assert dem.radius_m == pytest.approx(R, rel=1e-6)
        f = site_topography(dem, 10.0, 20.0, half_km=10, baseline_m=1000)
        assert f["topo__slope_mean_deg"] == pytest.approx(5.71, abs=0.15)
        pole = site_topography(dem, -89.9, 0.0, half_km=10, baseline_m=1000)  # cruza todas las longitudes
        assert np.isfinite(pole["topo__slope_mean_deg"])


# --- variables del primer bloque ---
def _plane(slope, n=101, h=500.0):
    y = np.arange(n)[::-1] * h
    return np.tile((slope * y)[:, None], (1, n)), h


def test_flat_terrain_new_features():
    f = window_features(np.full((101, 101), 10.0), 500.0)
    assert f["topo__frac_slope_lt5deg"] == 1.0 and f["topo__frac_slope_gt15deg"] == 0.0
    assert f["topo__slope_p90_deg"] == pytest.approx(0, abs=1e-9)
    assert f["topo__relief_m"] == pytest.approx(0, abs=1e-9)
    assert f["topo__tri_m"] == pytest.approx(0, abs=1e-9) and f["topo__tpi_std_m"] == pytest.approx(0, abs=1e-9)
    assert f["topo__curv_profile_abs_per_km"] == 0 and f["topo__curv_plan_abs_per_km"] == 0
    # sin laderas no hay orientación: valor neutro 0 (NO NaN: con NaN la PCA no puntuaba las celdas más llanas)
    assert f["topo__aspect_concentration"] == 0.0 and f["topo__aspect_equatorward"] == 0.0
    # parche llano = toda la ventana interior: (101-2)^2 píxeles de 0.25 km²
    assert f["topo__flat_patch_km2"] == pytest.approx(99 * 99 * 0.25, rel=1e-6)


def test_plane_new_features_and_aspect_by_hemisphere():
    z, h = _plane(0.1)  # 5.71°, sube hacia el norte
    north = window_features(z, h, lat=30.0)
    south = window_features(z, h, lat=-30.0)
    assert north["topo__slope_p90_deg"] == pytest.approx(5.71, abs=0.05)
    assert north["topo__frac_slope_lt5deg"] == 0.0 and north["topo__frac_slope_gt15deg"] == 0.0
    assert north["topo__aspect_concentration"] == pytest.approx(1.0, abs=1e-6)
    assert north["topo__aspect_equatorward"] == pytest.approx(1.0, abs=1e-6)  # cuesta abajo = sur = ecuador
    assert south["topo__aspect_equatorward"] == pytest.approx(-1.0, abs=1e-6)
    assert north["topo__tpi_std_m"] == pytest.approx(0, abs=1e-6)  # un plano no tiene crestas ni valles
    assert north["topo__tri_m"] > 0
    assert north["topo__curv_profile_abs_per_km"] == pytest.approx(0, abs=1e-6)
    assert north["topo__relief_m"] == pytest.approx(0.1 * 500 * 100 * 0.96, rel=0.02)  # p98-p2 de un plano


def test_steep_plane_fractions():
    z, h = _plane(0.6)  # 31°
    f = window_features(z, h)
    assert f["topo__frac_slope_gt15deg"] == 1.0 and f["topo__frac_slope_lt5deg"] == 0.0
    assert f["topo__flat_patch_km2"] == 0.0


def test_bowl_has_curvature_and_no_dominant_aspect():
    n, h = 101, 500.0
    x = (np.arange(n) - n // 2) * h
    a = 1e-4
    z = a * (x[None, :] ** 2 + x[:, None] ** 2)  # cuenco z = a·ρ²
    f = window_features(z, h)
    assert f["topo__aspect_concentration"] < 0.05  # laderas en todas direcciones
    assert f["topo__tpi_std_m"] > 0 and f["topo__relief_m"] > 0

    # Fórmulas exactas para z = aρ²: |plan| = 1/ρ y |perfil| = 2a/(1+(2aρ)²)^1.5.
    # (los píxeles con pendiente < 1° cuentan como 0; el análisis usa el interior [2:-2])
    rho = np.hypot(x[None, :], x[:, None])[2:-2, 2:-2]
    steep = (2 * a * rho) ** 2 > np.tan(np.radians(1.0)) ** 2
    plan = np.where(steep, 1 / np.where(rho > 0, rho, 1), 0).mean() * 1000
    prof = np.where(steep, 2 * a / (1 + (2 * a * rho) ** 2) ** 1.5, 0).mean() * 1000
    assert f["topo__curv_plan_abs_per_km"] == pytest.approx(plan, rel=0.02)
    assert f["topo__curv_profile_abs_per_km"] == pytest.approx(prof, rel=0.02)


def test_flat_patch_is_largest_contiguous_region():
    n, h = 101, 500.0
    z = np.zeros((n, n))
    z[:, 51:] = 0.5 * (np.arange(n - 51) * h)[None, :]  # mitad plana, mitad empinada (26.6°)
    f = window_features(z, h)
    total = (n - 2) ** 2 * 0.25
    assert 0.4 * total < f["topo__flat_patch_km2"] < 0.6 * total
    assert 0.3 < f["topo__frac_slope_gt15deg"] < 0.6


def test_roughness_scales_are_ordered_for_correlated_terrain():
    rng = np.random.default_rng(3)
    from scipy.ndimage import gaussian_filter
    z = gaussian_filter(rng.normal(0, 100, (101, 101)), 4)  # relieve suave con estructura de gran escala
    f = window_features(z, 500.0)
    assert f["topo__rough_1km_m"] < f["topo__rough_2km_m"] < f["topo__rough_5km_m"]


def test_all_declared_topo_features_are_returned():
    from analogos.config import DIMENSIONS

    f = window_features(np.random.default_rng(0).normal(0, 5, (101, 101)), 500.0)
    assert set(DIMENSIONS["topo"]) <= set(f)
    tiny = window_features(np.zeros((4, 4)), 500.0)  # ventana demasiado pequeña: NaN, no excepción
    assert set(DIMENSIONS["topo"]) <= set(tiny)


def test_flat_terrain_still_has_a_complete_topography_vector():
    """Regresión: el terreno llano debe tener TODAS las variables topográficas definidas (se puntúa en la PCA)."""
    from analogos.config import DIMENSIONS

    for z in (np.full((101, 101), 7.0), np.random.default_rng(1).normal(0, 0.2, (101, 101))):  # llano exacto y casi llano
        f = window_features(z, 500.0)
        assert all(np.isfinite(f[k]) for k in DIMENSIONS["topo"]), [k for k in DIMENSIONS["topo"] if not np.isfinite(f[k])]
    nodata = window_features(np.full((101, 101), np.nan), 500.0)  # sin dato sí sigue siendo NaN (no es "llano")
    assert np.isnan(nodata["topo__aspect_concentration"]) and np.isnan(nodata["topo__slope_mean_deg"])
