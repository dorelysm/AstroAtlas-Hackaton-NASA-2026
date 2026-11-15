# NASA (and partner) APIs used to extract the data

Investigated on 14 November 2026. **Verified with curl** means we made a real request and it answered with data. **Documentation only** means we read it on a page but did not test it. **NOT VERIFIED** means we saw it only in search results.

> **Status note:** this page records the API exploration of the first day. The final pipeline reads the Moon and Mars DEMs directly from the NASA PDS (`src/astroatlas/data/pds_dem.py`), uses Copernicus GLO-90 for Earth topography, and MODIS products through Earthdata for thermal, snow and vegetation; see [data-sources.md](data-sources.md). The sections "Prototype in the repo" and "Topography of the Moon and Mars (implemented)" describe the first prototype and are kept for traceability.

## Summary by dimension

| Dimension | Earth | Moon | Mars |
|---|---|---|---|
| Topography | CMR + earthaccess (NASADEM), AppEEARS (SRTM) | USGS WMS (LOLA), USGS STAC | USGS WMS (MOLA), ODE (MOLA) |
| Thermal | AppEEARS or earthaccess (MODIS LST), POWER (T2M) | ODE (Diviner) | ODE (TES/THEMIS), USGS STAC (THEMIS mosaics) |
| Water/ice | POWER (precipitation), CMR (GPM/IMERG) | ODE (LEND, Mini-RF) | ODE (SHARAD, GRS) |
| Geology | CMR (ASTER) | ODE (M3, LROC) | ODE (CRISM) |

## Earth

### CMR (Common Metadata Repository): search datasets and granules
- **Base:** `https://cmr.earthdata.nasa.gov/search` (`/collections`, `/granules`). No credentials to search.
- **Verified with curl:** `collections.json?short_name=MOD11A1` returns daily MODIS/Terra LST V061 (global, 1 km, since 2000). `short_name=NASADEM_HGT` returns NASADEM 1 arcsec V001 (coverage from -56° to 60° latitude, note: **it does not cover the poles**).
- Formats: `.json`, `.umm_json`, `.stac`, `.csv`... Pages of up to 2,000 results. Accepts a spatial box and a temporal filter.
- Docs: https://cmr.earthdata.nasa.gov/search/site/docs/search/api.html

### earthaccess (Python library): search and download
- Wraps CMR and authenticated downloads. Typical flow: `earthaccess.login()` → `search_data(short_name=..., bounding_box=...)` → `download()`. Requires a free Earthdata account (https://urs.earthdata.nasa.gov), credentials in `.env`.
- Documentation only (search results): https://earthaccess.readthedocs.io/ and https://github.com/nsidc/earthaccess.
- Harmony (`harmony-py`) allows clipping by area and variable on the server, useful to avoid downloading whole global tiles. Documentation only.

### AppEEARS: extract values by point or area
- **Base:** `https://appeears.earthdatacloud.nasa.gov/api`. Earthdata login (`POST /login`, token of ~48 h).
- Products from the documentation: MODIS LST (`MOD11A1.061`, layers `LST_Day_1km` and `LST_Night_1km`), SRTM (`SRTMGL1_NC.003`), ASTER GDEM (`ASTGTM_NC.003`), MCD12Q1 land cover, MOD16A2GF evapotranspiration.
- Flow: `POST /task` → `GET /status/{id}` → `GET /bundle/{id}`. Points come out as CSV, areas as GeoTIFF/NetCDF4. Geographic projection EPSG:4326.
- It is **asynchronous**: a task takes minutes. It fits a grid of points, not tiles of millions of cells. **Documentation only** (we did not test the login).
- Docs: https://appeears.earthdatacloud.nasa.gov/api/

### POWER (NASA Langley): climate at a point, no login
- **Verified with curl:** `https://power.larc.nasa.gov/api/temporal/climatology/point?parameters=T2M_MAX,T2M_MIN,PRECTOTCORR&community=RE&longitude=-69.25&latitude=-24.5&format=JSON` returned the monthly climatology of Atacama: annual T2M_MAX 32.75 °C, annual T2M_MIN -4.33 °C, precipitation ~0.03 mm/day.
- 422 responses if validation fails, 429 if you ask too fast. Other services: daily, monthly, hourly, OPeNDAP, AWS.
- Useful for the `thermal` dimension (air temperature, not surface) and `ice` (precipitation). Useless for topography.
- Docs: https://power.larc.nasa.gov/docs/services/api/

### GIBS / Worldview
Tiled imagery for visualisation. Not a source of numerical values for the model; it is used in the app only for the orbital-view comparison (see [../app/interface.md](../app/interface.md)).

## Moon and Mars

### ODE REST (Orbital Data Explorer, PDS Geosciences): search products by instrument and area
- **Base:** `https://oderest.rsl.wustl.edu/live2/` (with the trailing slash; without it, it redirects). No authentication. XML or JSON output. Covers Mars, Phobos, Deimos, the Moon, Mercury and Venus.
- Requires `ihid` (spacecraft) + `iid` (instrument) + `pt` (product type), or an identifier. Area parameters: `minlat`, `maxlat`, `westernlon`, `easternlon`, or polygon. `results=c` counts, `results=m` returns metadata.
- **Verified with curl:**
  - Diviner: `target=moon&ihid=LRO&iid=DLRE&pt=RDR` returned 391,437 products.
  - MOLA: `target=mars&ihid=MGS&iid=MOLA&pt=MEGDR` returned 89 products (elevation grids).
  - `LRO + LOLA + RDR` gave an invalid-combination error: the ODE web page must be consulted to see which `pt` exists for LOLA.
- **What it returns:** metadata and download links of products, **not** already-extracted values. The product must be downloaded and read (GeoTIFF/IMG with GDAL or rasterio).
- Docs: https://oderest.rsl.wustl.edu/

### USGS Astrogeology: maps, DEMs and STAC
- **STAC verified with curl:** `https://stac.astrogeology.usgs.gov/api/collections` returned 18 collections. Relevant ones: `lunar_orbiter_laser_altimeter` (LOLA points in COPC format, queryable with PDAL), `kaguya_terrain_camera_usgs_dtms_v2` (+ `northpolar` and `southpolar` variants), `mro_hirise_socet_dtms`, `mro_ctx_controlled_usgs_dtms`, `mo_themis_controlled_mosaics`.
- **Moon WMS:** `https://planetarymaps.usgs.gov/cgi-bin/mapserv?map=/maps/earth/moon_simp_cyl.map&service=WMS&request=GetCapabilities` answered HTTP 200 (only the response was tested, not the content). According to third-party guides, there is also an elevation service for LOLA (Moon) and MOLA (Mars) on `wms.wr.usgs.gov`. **NOT VERIFIED**: confirm the layers with GetCapabilities.
- With GDAL a WMS area can be clipped to GeoTIFF (`gdal_translate`) and slope computed with `gdaldem`. That was the shortest route to `topo__*` on the Moon and Mars.
- Gazetteer (names and coordinates): https://planetarynames.wr.usgs.gov/. The search gave HTTP 500; only ZIP/KML can be downloaded.

### PDS Search API (Planetary Data System registry)
- **Base:** `https://pds.mcp.nasa.gov/api/search/1/` (the URL `pds.nasa.gov/api/search/1/` redirects there). No authentication.
- **Verified with curl:** `/products?q=...&limit=1` answered with well-formed JSON, but the test query (`lidvid like "urn:nasa:pds:*lola*"`) returned 0 results, so **the search syntax is not validated**. The documentation page only showed the title "PDS Registry".
- It only covers PDS4 products; older files (PDS3) are in ODE.

### NASA Trek (Moon Trek, Mars Trek)
- WMTS tile services (equirectangular, north pole, south pole). The URL template is `https://{endpoint}/1.0.0/{Style}/{TileMatrixSet}/{TileMatrix}/{TileRow}/{TileCol}.png`; the values come from each product's GetCapabilities. Mars catalogue: https://api.nasa.gov/mars-wmts/catalog (seen in search).
- **We found no** REST endpoints for slope or elevation profiles; those analyses seem to be portal tools. Used in the app for the orbital-view comparison (Viking MDIM 2.1 for Mars, LRO WAC for the Moon), not to extract features.

## Prototype in the repo (first day)

Code in `src/astroatlas/data/` (standard library only, with a cache in `data/raw/cache/`):

| Module | What it does | Tested live (14 Nov 2026) |
|---|---|---|
| `http.py` | GET JSON with retries (429/5xx) and cache | yes |
| `earth.py` | `build_features()` with POWER: `thermal__*` and `ice__water_frac`; `cmr_collections()` and `cmr_granules()` | 72 points (30° grid) in ~11 s, all with data; CMR returned MODIS LST and 2 NASADEM granules over Atacama with a download link |
| `ode.py` | `count()`, `products()`, `bbox_around()` for ODE | Diviner: 5,230 products near Malapert; MOLA: 2 products with download links |

**Limitations of the prototype (superseded later):**
- `topo__*` and `geo__*` came out NaN: NASADEM/Copernicus DEM and lithology had to be processed. The NASADEM download requires an Earthdata login.
- POWER `thermal__*` is **air** temperature at 2 m, and the 15° grid is very coarse. It is not comparable with the **surface** temperature of Diviner. It was replaced by MODIS LST.
- `ice__water_frac` was a **provisional proxy** (precipitation / 5 mm/day, clipped to 0–1). It came out high in Antarctica (0.2–0.65 in the 75° S strip), because the product counts snow as precipitation; it is neither a measure of liquid water nor of ground ice. It was replaced by MODIS snow cover.

## Topography of the Moon and Mars (first implementation)

**Source:** two global USGS GeoTIFFs, open and downloadable by HTTP ranges (`Accept-Ranges: bytes`, verified with a HEAD request on 14 Nov 2026):

| Body | URL | Size | Pixel | Notes |
|---|---|---|---|---|
| Moon (LOLA) | https://planetarymaps.usgs.gov/mosaic/Lunar_LRO_LOLA_Global_LDEM_118m_Mar2014.tif | 8.5 GB | 118.45 m | int16, **scale 0.5** (value × 0.5 = metres), nodata -32768 |
| Mars (MOLA) | https://planetarymaps.usgs.gov/mosaic/Mars_MGS_MOLA_DEM_mosaic_global_463m.tif | 2.1 GB | 463.09 m | int16, scale 1, nodata -32768 |

Both are simple cylindrical, longitude -180 to 180 east-positive, without tiles or overviews (one row per block). The USGS Moon WMS **only serves coloured shaded reliefs**, not elevation, so it cannot be used to compute slopes. (The final pipeline reads the same LOLA and MOLA data from the NASA PDS instead of these mosaics.)

**Code:** `src/astroatlas/topography.py` (pure numpy functions) and `src/astroatlas/data/dem.py` (windowed reading with rasterio and `/vsicurl/`). `python -m astroatlas.data.moon` and `python -m astroatlas.data.mars` write the parquet files. Requires `pip install -e ".[data]"`.

**Variables (16, defined in [feature-contract.md](feature-contract.md)):** mean slope and 90th percentile, fraction of area with slope < 5° and > 15°, largest flat patch, local relief, elevation deviation, roughness at 1, 2 and 5 km, TRI, TPI, profile and plan curvature, slope-aspect concentration and equatorward component. The 5° and 15° thresholds are provisional and have to be confirmed with a source. Absolute altitude is not used, because the datums are not comparable.

**Method:** 50 × 50 km window centred on the site, sampled on a local azimuthal-equidistant grid (isotropic pixel in metres, also near the poles); slope and roughness are computed over the same baseline (~500 m); roughness = mean of the standard deviation of elevation in ~1 km blocks.

**Check with known elevations (real reading):**

| Point | Elevation read | Expected |
|---|---|---|
| Olympus Mons, summit | 20,015 m | ~+21 km |
| Hellas floor | -6,015 m | ~-7 km |
| Jezero | -2,630 m | ~-2.5 km |
| Gale | -4,499 m | ~-4.5 km |
| Apollo 11 | -1,927 m | ~-2 km |

The longitude convention, sign and scale are confirmed. The tests (`tests/test_topography.py`) check that a plane with slope 0.1 gives 5.71° and that the poles do not break the grid.

**Limitations:**
- A single window per site, not several cells, so the site profile is a single row.
- Slope depends on scale. With the ~470 m baseline fine detail is lost; LOLA's 118 m and MOLA's 463 m do not resolve rocks or local slopes.
- Near the poles this mosaic is of lower quality than LOLA's polar products (~20 m), which we do not use. Shackleton is the least reliable row.
- Roughness uses 2 × 2-pixel blocks on Mars and 2 × 2 pixels of ~470 m on the Moon (~1 km), and mixes in some slope.
- Each window reads full rows of the remote file: ~2–6 s per site, but a polar site can read tens of MB.

## Recommendation for the pipeline (first day; what was finally done is in [data-sources.md](data-sources.md))

1. **Earth, topography:** NASADEM through `earthaccess` (note: no poles) or Copernicus DEM (ESA source, to cover high latitudes).
2. **Earth, thermal and water:** MODIS LST through `earthaccess` + Harmony for areas, or AppEEARS for points; POWER for a quick first version of temperature and precipitation.
3. **Moon and Mars, topography:** USGS WMS/STAC with GDAL, clipping around each site of `docs/catalog/known_landings.csv` and `docs/catalog/target_sites.csv`.
4. **Moon and Mars, thermal, ice and minerals:** ODE REST to locate products (Diviner, TES/THEMIS, SHARAD, CRISM) and download them from the PDS.
5. **Heavy downloads:** cache in `data/raw/` and test first with one site and one small area.

## Pending verification (day one)
- Earthdata login and a real download with `earthaccess`/AppEEARS (needs credentials from someone on the team) — done later for MODIS, MERRA-2, GLDAS and SEDAC.
- Exact layers and URL of the USGS elevation WMS (LOLA and MOLA) — superseded by the PDS readers.
- Valid `pt` value for LOLA in ODE, and the query syntax of the PDS Search API.
- Real spatial resolution of each product versus our grid (POWER is usually low resolution; **confirm it**).
