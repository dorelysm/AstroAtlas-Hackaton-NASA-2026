# Features (data contract)

Each body delivers `data/features/{earth,moon,mars}.parquet` with these columns.

**Required:** `cell_id` (unique per body), `body` (`earth|moon|mars`), `lat`, `lon` (degrees, cell centre).
**Moon/Mars only:** `site` (name in `docs/catalog/target_sites.csv`); several cells per site form its profile.
**NaN** = no data. It is never imputed silently.

Features must be **comparable between bodies**: same definition, same unit, same measurement baseline.

| Dimension | Feature | Unit | Definition | Source Earth / Moon / Mars |
|---|---|---|---|---|
| topo | `topo__slope_mean_deg` | ° | mean slope (baseline ~500 m) | DEM / LOLA / MOLA |
| topo | `topo__slope_p90_deg` | ° | 90th percentile of the slope | same |
| topo | `topo__frac_slope_lt5deg` | 0-1 | fraction of the area with slope < 5° (threshold to be confirmed with a source) | same |
| topo | `topo__frac_slope_gt15deg` | 0-1 | fraction of the area with slope > 15° (threshold to be confirmed with a source) | same |
| topo | `topo__flat_patch_km2` | km² | largest continuous patch with slope < 5° | same |
| topo | `topo__relief_m` | m | local relief: 98th − 2nd percentile of elevation | same |
| topo | `topo__elev_std_m` | m | standard deviation of elevation in the window | same |
| topo | `topo__rough_1km_m` | m | mean of the standard deviation of elevation in ~1 km blocks | same |
| topo | `topo__rough_2km_m` | m | same with ~2 km blocks | same |
| topo | `topo__rough_5km_m` | m | same with ~5 km blocks | same |
| topo | `topo__tri_m` | m | terrain ruggedness index (mean of \|centre − neighbour\|, 8 neighbours) | same |
| topo | `topo__tpi_std_m` | m | standard deviation of the topographic position index (5×5 neighbourhood) | same |
| topo | `topo__curv_profile_abs_per_km` | 1/km | mean of \|profile curvature\| (Zevenbergen-Thorne; 0 if slope < 1°) | same |
| topo | `topo__curv_plan_abs_per_km` | 1/km | mean of \|plan curvature\| | same |
| topo | `topo__aspect_concentration` | 0-1 | how much the slopes point in the same direction (1 = all alike); **0 if mean slope < 0.1°** (with no slopes there is no aspect; it used to be NaN and left the flattest cells unscored) | same |
| topo | `topo__aspect_equatorward` | -1 to 1 | component of the slopes towards the hemisphere's equator (slope-weighted) | same |
| thermal | `thermal__t_max_k` | K | maximum surface temperature | MODIS LST / Diviner / TES-THEMIS |
| thermal | `thermal__t_range_k` | K | daily temperature range (max-min) | MODIS LST / Diviner / TES-THEMIS |
| ice | `ice__water_frac` | 0-1 | normalised water/ice indicator (snow cover on Earth; ice/water fraction on the Moon and Mars) | see [data-sources.md](data-sources.md) |
| geo | `geo__basalt_frac` | 0-1 | fraction of the surface of basaltic composition | lithology / Lunar Prospector / Odyssey GRS |

**Coordinate convention (decide and respect):** east-positive longitude, 0..360 in the Moon and Mars input data; Earth uses -180..180. The sources mix ranges (Apollo in -180..180, Surveyor and Mars in 0..360) and do not declare whether latitude is planetocentric or planetographic. For Mars, the USGS states it adopted planetocentric latitude with east-positive longitude (https://planetarynames.wr.usgs.gov/Page/MARS/system); the NSSDC landing data for Viking are also planetocentric. `docs/catalog/known_landings.csv` carries `lon_east_0_360` already normalised.

**Absolute altitude:** it is not a feature, because the elevation datums of Earth, the Moon and Mars are not comparable. `elev_mean_m` is stored only as a diagnostic (it does not enter the model). All `topo__*` are computed over the same ~500 m baseline and a 50 × 50 km window.

**Population viability (Earth only, NOT a model variable):** columns `dist_settlement_km`, `settlement_name`, `viable` (not viable if there is a settlement of >= 1,000 inhabitants within 50 km). See [data-sources.md](data-sources.md). It enters neither the score nor the validation.

To add a feature: add it to `DIMENSIONS` in `src/astroatlas/config.py` and to this table.
Pending (extras): dust/wind, subsurface (caves, lava tubes), illumination.
