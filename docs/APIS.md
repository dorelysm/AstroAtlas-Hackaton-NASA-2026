# APIs de NASA (y socios) para extraer los datos

Investigado el 14 de noviembre de 2026. **Verificado con curl** significa que hicimos una petición real y respondió con datos. **Solo documentación** significa que lo leímos en una página pero no lo probamos. **NO VERIFICADO** significa que lo vimos solo en resultados de búsqueda.

## Resumen por dimensión

| Dimensión | Tierra | Luna | Marte |
|---|---|---|---|
| Topografía | CMR + earthaccess (NASADEM), AppEEARS (SRTM) | WMS del USGS (LOLA), STAC del USGS | WMS del USGS (MOLA), ODE (MOLA) |
| Térmica | AppEEARS o earthaccess (MODIS LST), POWER (T2M) | ODE (Diviner) | ODE (TES/THEMIS), STAC del USGS (mosaicos THEMIS) |
| Agua/hielo | POWER (precipitación), CMR (GPM/IMERG) | ODE (LEND, Mini-RF) | ODE (SHARAD, GRS) |
| Geología | CMR (ASTER) | ODE (M3, LROC) | ODE (CRISM) |

## Tierra

### CMR (Common Metadata Repository): buscar datasets y granulos
- **Base:** `https://cmr.earthdata.nasa.gov/search` (`/collections`, `/granules`). Sin credenciales para buscar.
- **Verificado con curl:** `collections.json?short_name=MOD11A1` devuelve MODIS/Terra LST diario V061 (global, 1 km, desde 2000). `short_name=NASADEM_HGT` devuelve NASADEM 1 arcsec V001 (cobertura de -56° a 60° de latitud, ojo: **no cubre los polos**).
- Formatos: `.json`, `.umm_json`, `.stac`, `.csv`... Páginas de hasta 2000 resultados. Acepta caja espacial y filtro temporal.
- Docs: https://cmr.earthdata.nasa.gov/search/site/docs/search/api.html

### earthaccess (librería Python): buscar y descargar
- Envuelve CMR y las descargas autenticadas. Flujo típico: `earthaccess.login()` → `search_data(short_name=..., bounding_box=...)` → `download()`. Requiere cuenta gratuita de Earthdata (https://urs.earthdata.nasa.gov), credenciales en `.env`.
- Solo documentación (resultados de búsqueda): https://earthaccess.readthedocs.io/ y https://github.com/nsidc/earthaccess.
- Harmony (`harmony-py`) permite recortar por zona y variable en el servidor, útil para no bajar tiles globales enteros. Solo documentación.

### AppEEARS: extraer valores por punto o área
- **Base:** `https://appeears.earthdatacloud.nasa.gov/api`. Login con Earthdata (`POST /login`, token de ~48 h).
- Productos de la documentación: MODIS LST (`MOD11A1.061`, capas `LST_Day_1km` y `LST_Night_1km`), SRTM (`SRTMGL1_NC.003`), ASTER GDEM (`ASTGTM_NC.003`), cobertura MCD12Q1, evapotranspiración MOD16A2GF.
- Flujo: `POST /task` → `GET /status/{id}` → `GET /bundle/{id}`. Puntos salen en CSV, áreas en GeoTIFF/NetCDF4. Proyección geográfica EPSG:4326.
- Es **asíncrono**: una tarea tarda minutos. Encaja para la malla de puntos, no para tiles de millones de celdas. **Solo documentación** (no probamos el login).
- Docs: https://appeears.earthdatacloud.nasa.gov/api/

### POWER (NASA Langley): clima en un punto, sin login
- **Verificado con curl:** `https://power.larc.nasa.gov/api/temporal/climatology/point?parameters=T2M_MAX,T2M_MIN,PRECTOTCORR&community=RE&longitude=-69.25&latitude=-24.5&format=JSON` devolvió la climatología mensual de Atacama: T2M_MAX anual 32.75 °C, T2M_MIN anual -4.33 °C, precipitación ~0.03 mm/día.
- Respuestas 422 si falla la validación, 429 si pides demasiado rápido. Otros servicios: diario, mensual, horario, OPeNDAP, AWS.
- Útil para la dimensión `thermal` (temperatura del aire, no de la superficie) y `ice` (precipitación). No sirve para topografía.
- Docs: https://power.larc.nasa.gov/docs/services/api/

### GIBS / Worldview
Imágenes en teselas para visualizar. No probado; no es una fuente de valores numéricos para el modelo.

## Luna y Marte

### ODE REST (Mars Orbital Data Explorer, PDS Geosciences): buscar productos por instrumento y zona
- **Base:** `https://oderest.rsl.wustl.edu/live2/` (con la barra final; sin ella redirige). Sin autenticación. Salida XML o JSON. Cubre Marte, Fobos, Deimos, Luna, Mercurio y Venus.
- Requiere `ihid` (nave) + `iid` (instrumento) + `pt` (tipo de producto), o un identificador. Parámetros de zona: `minlat`, `maxlat`, `westernlon`, `easternlon`, o polígono. `results=c` cuenta, `results=m` devuelve metadatos.
- **Verificado con curl:**
  - Diviner: `target=moon&ihid=LRO&iid=DLRE&pt=RDR` devolvió 391 437 productos.
  - MOLA: `target=mars&ihid=MGS&iid=MOLA&pt=MEGDR` devolvió 89 productos (rejillas de elevación).
  - `LRO + LOLA + RDR` dio error de combinación inválida: hay que consultar en la web de ODE qué `pt` existe para LOLA.
- **Qué devuelve:** metadatos y enlaces de descarga de productos, **no** valores ya extraídos. Hay que bajar el producto y leerlo (GeoTIFF/IMG con GDAL o rasterio).
- Docs: https://oderest.rsl.wustl.edu/

### USGS Astrogeology: mapas, DEMs y STAC
- **STAC verificado con curl:** `https://stac.astrogeology.usgs.gov/api/collections` devolvió 18 colecciones. Relevantes: `lunar_orbiter_laser_altimeter` (puntos de LOLA en formato COPC, consultables con PDAL), `kaguya_terrain_camera_usgs_dtms_v2` (+ variantes `northpolar` y `southpolar`), `mro_hirise_socet_dtms`, `mro_ctx_controlled_usgs_dtms`, `mo_themis_controlled_mosaics`.
- **WMS de la Luna:** `https://planetarymaps.usgs.gov/cgi-bin/mapserv?map=/maps/earth/moon_simp_cyl.map&service=WMS&request=GetCapabilities` respondió HTTP 200 (se probó solo la respuesta, no el contenido). Según guías de terceros, hay también servicio de elevación LOLA (Luna) y MOLA (Marte) en `wms.wr.usgs.gov`. **NO VERIFICADO**: confirmar las capas con GetCapabilities.
- Con GDAL se puede recortar una zona de un WMS a GeoTIFF (`gdal_translate`) y calcular pendiente con `gdaldem`. Esa es la ruta más corta para `topo__*` en Luna y Marte.
- Gazetteer (nombres y coordenadas): https://planetarynames.wr.usgs.gov/. La búsqueda dio HTTP 500; solo se descargan ZIP/KML.

### PDS Search API (registro del Planetary Data System)
- **Base:** `https://pds.mcp.nasa.gov/api/search/1/` (la URL `pds.nasa.gov/api/search/1/` redirige ahí). Sin autenticación.
- **Verificado con curl:** `/products?q=...&limit=1` respondió con JSON bien formado, pero la consulta de prueba (`lidvid like "urn:nasa:pds:*lola*"`) devolvió 0 resultados, así que **la sintaxis de búsqueda no está validada**. La página de documentación solo mostró el título "PDS Registry".
- Solo cubre productos PDS4; los archivos más antiguos (PDS3) están en ODE.

### NASA Trek (Moon Trek, Mars Trek)
- Servicios de teselas WMTS (equirectangular, polo norte, polo sur). La plantilla de URL es `https://{endpoint}/1.0.0/{Style}/{TileMatrixSet}/{TileMatrix}/{TileRow}/{TileCol}.png`; los valores salen del GetCapabilities de cada producto. Catálogo de Marte: https://api.nasa.gov/mars-wmts/catalog (visto en búsqueda).
- **No encontramos** endpoints REST de pendiente ni de perfiles de elevación; esos análisis parecen ser herramientas del portal. Sirve para mapas de fondo en la app, no para extraer features.

## Prototipo en el repo

Código en `src/analogos/data/` (solo biblioteca estándar, con caché en `data/raw/cache/`):

| Módulo | Qué hace | Probado en vivo (14-nov-2026) |
|---|---|---|
| `http.py` | GET JSON con reintentos (429/5xx) y caché | sí |
| `earth.py` | `build_features()` con POWER: `thermal__*` e `ice__water_frac`; `cmr_collections()` y `cmr_granules()` | 72 puntos (malla de 30°) en ~11 s, todos con dato; CMR devolvió MODIS LST y 2 granulos de NASADEM sobre Atacama con enlace de descarga |
| `ode.py` | `count()`, `products()`, `bbox_around()` para ODE | Diviner: 5 230 productos cerca de Malapert; MOLA: 2 productos con enlaces de descarga |

Comandos: `python -m analogos.data.earth` genera `data/features/earth.parquet` (malla de 15°, 288 puntos).

**Limitaciones del prototipo (no usar así en la entrega):**
- `topo__*` y `geo__*` salen como NaN: falta procesar NASADEM/Copernicus DEM y litología. La descarga de NASADEM exige login de Earthdata.
- `thermal__*` de POWER es temperatura del **aire** a 2 m, y la malla de 15° es muy gruesa. No es comparable con la temperatura de **superficie** de Diviner. Hay que sustituirla por MODIS LST.
- `ice__water_frac` es un **proxy provisional** (precipitación / 5 mm/día, recortado a 0–1). Sale alto en la Antártida (0.2–0.65 en la franja de 75° S), porque el producto cuenta nieve como precipitación; no es una medida de agua líquida ni de hielo en el suelo.
- `moon.py` y `mars.py` todavía no extraen features: ODE solo da enlaces; falta descargar y leer los archivos.

## Topografía de Luna y Marte (implementada)

**Fuente:** dos GeoTIFF globales del USGS, abiertos y con descarga por rangos HTTP (`Accept-Ranges: bytes`, verificado con una petición HEAD el 14-nov-2026):

| Cuerpo | URL | Tamaño | Píxel | Notas |
|---|---|---|---|---|
| Luna (LOLA) | https://planetarymaps.usgs.gov/mosaic/Lunar_LRO_LOLA_Global_LDEM_118m_Mar2014.tif | 8.5 GB | 118.45 m | int16, **escala 0.5** (valor × 0.5 = metros), nodata -32768 |
| Marte (MOLA) | https://planetarymaps.usgs.gov/mosaic/Mars_MGS_MOLA_DEM_mosaic_global_463m.tif | 2.1 GB | 463.09 m | int16, escala 1, nodata -32768 |

Ambos son cilíndricos simples, longitud -180 a 180 este-positiva, sin teselas ni overviews (una fila por bloque). El WMS de la Luna del USGS **solo sirve relieves sombreados coloreados**, no elevación, así que no sirve para calcular pendientes.

**Código:** `src/analogos/topography.py` (funciones puras de numpy) y `src/analogos/data/dem.py` (lectura por ventanas con rasterio y `/vsicurl/`). `python -m analogos.data.moon` y `python -m analogos.data.mars` escriben los parquet. Requiere `pip install -e ".[data]"` (rasterio tiene wheel para Python 3.14).

**Variables (16, definidas en `docs/features.md`):** pendiente media y percentil 90, fracción de área con pendiente < 5° y > 15°, mayor parche llano, relieve local, desviación de la elevación, rugosidad a 1, 2 y 5 km, TRI, TPI, curvatura de perfil y en planta, concentración de orientación de laderas y componente hacia el ecuador. Los umbrales de 5° y 15° son provisionales y hay que confirmarlos con una fuente. La altitud absoluta no se usa, porque los datums no son comparables.

**Método:** ventana de 50 × 50 km centrada en el sitio, muestreada en una rejilla local equidistante-azimutal (píxel isótropo en metros, también cerca de los polos); pendiente y rugosidad se calculan sobre la misma base (~470 m en la Luna, 463 m en Marte); rugosidad = media de la desviación estándar de la elevación en bloques de ~1 km.

**Comprobación con elevaciones conocidas (lectura real):**

| Punto | Elevación leída | Esperado |
|---|---|---|
| Olympus Mons, cumbre | 20 015 m | ~+21 km |
| Fondo de Hellas | -6 015 m | ~-7 km |
| Jezero | -2 630 m | ~-2.5 km |
| Gale | -4 499 m | ~-4.5 km |
| Apolo 11 | -1 927 m | ~-2 km |

La convención de longitud, el signo y la escala quedan confirmados. Los tests (`tests/test_topography.py`) comprueban que un plano con pendiente 0.1 da 5.71° y que los polos no rompen la rejilla.

**Resultados actuales** (`data/features/moon.parquet` y `mars.parquet`):

| Sitio | Pendiente media (°) | P90 (°) | Área con pendiente < 5° | Mayor parche llano (km²) | Relieve (m) | Rugosidad 1 km (m) |
|---|---|---|---|---|---|---|
| Shackleton (borde) | 11.6 | 26.1 | 23 % | 178 | 3 884 | 50.9 |
| Malapert | 13.1 | 22.7 | 12 % | 48 | 6 322 | 56.0 |
| Mare Tranquillitatis (pozo) | 0.75 | 1.1 | 98 % | 2 335 | 119 | 3.6 |
| Jezero | 2.8 | 7.0 | 84 % | 2 011 | 884 | 11.7 |
| Oxia Planum | 0.74 | 1.4 | 100 % | 2 449 | 250 | 3.1 |
| Arcadia Planitia | 0.31 | 0.6 | 100 % | 2 455 | 61 | 1.3 |

Los polares salen empinados y las llanuras salen planas, lo esperado. La ventana completa mide 2 500 km². Las 16 variables de cada sitio están en `data/features/moon.parquet` y `mars.parquet`.

**Limitaciones:**
- Una sola ventana por sitio, no varias celdas, así que el perfil del sitio es una única fila.
- La pendiente depende de la escala. Con la base de ~470 m se pierde detalle fino; los 118 m de LOLA y los 463 m de MOLA no resuelven rocas ni pendientes locales.
- Cerca de los polos este mosaico es de menor calidad que los productos polares de LOLA (~20 m), que no usamos. Shackleton es la fila menos fiable.
- La rugosidad usa bloques de 2 × 2 píxeles en Marte y de 2 × 2 píxeles de ~470 m en la Luna (~1 km), y mezcla algo de pendiente.
- Falta la **Tierra**: sigue sin `topo__*`, así que el modelo todavía no puede comparar topografía contra la Tierra real.
- Cada ventana lee filas completas del archivo remoto: ~2–6 s por sitio, pero un sitio polar puede leer decenas de MB.

## Recomendación para el pipeline

1. **Tierra, topografía:** NASADEM por `earthaccess` (ojo: sin polos) o Copernicus DEM (fuente ESA, para cubrir latitudes altas).
2. **Tierra, térmica y agua:** MODIS LST vía `earthaccess` + Harmony para zonas, o AppEEARS para puntos; POWER para una primera versión rápida de temperatura y precipitación.
3. **Luna y Marte, topografía:** WMS/STAC del USGS con GDAL, recortando alrededor de cada sitio de `docs/aterrizajes_conocidos.csv` y `docs/sitios_objetivo.csv`.
4. **Luna y Marte, térmica, hielo y minerales:** ODE REST para localizar los productos (Diviner, TES/THEMIS, SHARAD, CRISM) y descargarlos desde PDS.
5. **Descargas pesadas:** cachear en `data/raw/` y probar primero con un sitio y una zona pequeña.

## Pendiente de verificar
- Login de Earthdata y una descarga real con `earthaccess`/AppEEARS (necesita las credenciales de alguien del equipo).
- Capas y URL exactas de los WMS de elevación del USGS (LOLA y MOLA).
- Valor de `pt` válido para LOLA en ODE, y sintaxis de consulta del PDS Search API.
- Resolución espacial real de cada producto frente a nuestra malla (POWER suele ser de baja resolución; **confirmarlo**).
