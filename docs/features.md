# Features (contrato de datos)

Cada cuerpo entrega `data/features/{earth,moon,mars}.parquet` con estas columnas.

**Obligatorias:** `cell_id` (único por cuerpo), `body` (`earth|moon|mars`), `lat`, `lon` (grados, centro de celda).
**Solo Luna/Marte:** `site` (nombre en `docs/sitios_objetivo.csv`); varias celdas por sitio forman su perfil.
**NaN** = sin dato. No se imputa en silencio.

Las features deben ser **comparables entre cuerpos**: misma definición, misma unidad, misma base de medición.

| Dimensión | Feature | Unidad | Definición | Fuente Tierra / Luna / Marte |
|---|---|---|---|---|
| topo | `topo__slope_mean_deg` | ° | pendiente media (base ~500 m) | DEM / LOLA / MOLA |
| topo | `topo__slope_p90_deg` | ° | percentil 90 de la pendiente | idem |
| topo | `topo__frac_slope_lt5deg` | 0-1 | fracción del área con pendiente < 5° (umbral a confirmar con fuente) | idem |
| topo | `topo__frac_slope_gt15deg` | 0-1 | fracción del área con pendiente > 15° (umbral a confirmar con fuente) | idem |
| topo | `topo__flat_patch_km2` | km² | mayor parche continuo con pendiente < 5° | idem |
| topo | `topo__relief_m` | m | relieve local: percentil 98 − percentil 2 de la elevación | idem |
| topo | `topo__elev_std_m` | m | desviación estándar de la elevación en la ventana | idem |
| topo | `topo__rough_1km_m` | m | media de la desviación estándar de la elevación en bloques de ~1 km | idem |
| topo | `topo__rough_2km_m` | m | ídem con bloques de ~2 km | idem |
| topo | `topo__rough_5km_m` | m | ídem con bloques de ~5 km | idem |
| topo | `topo__tri_m` | m | índice de rugosidad del terreno (media de \|centro − vecino\|, 8 vecinos) | idem |
| topo | `topo__tpi_std_m` | m | desviación estándar del índice de posición topográfica (vecindad 5×5) | idem |
| topo | `topo__curv_profile_abs_per_km` | 1/km | media de \|curvatura de perfil\| (Zevenbergen-Thorne; 0 si pendiente < 1°) | idem |
| topo | `topo__curv_plan_abs_per_km` | 1/km | media de \|curvatura en planta\| | idem |
| topo | `topo__aspect_concentration` | 0-1 | cuánto apuntan las laderas en la misma dirección (1 = todas igual); **0 si la pendiente media < 0.1°** (sin laderas no hay orientación; antes era NaN y dejaba sin puntuar a las celdas más llanas) | idem |
| topo | `topo__aspect_equatorward` | -1 a 1 | componente de las laderas hacia el ecuador del hemisferio (ponderada por pendiente) | idem |
| thermal | `thermal__t_max_k` | K | temperatura superficial máxima | MODIS LST / Diviner / TES-THEMIS |
| thermal | `thermal__t_range_k` | K | amplitud térmica diaria (max-min) | MODIS LST / Diviner / TES-THEMIS |
| ice | `ice__water_frac` | 0-1 | indicador normalizado de agua/hielo (precipitación o humedad en la Tierra; H/hielo en Luna y Marte) | por definir |
| geo | `geo__basalt_frac` | 0-1 | fracción de superficie de composición basáltica | litología / LROC-M3 / CRISM |

**Convención de coordenadas (decidir y respetar):** longitud este-positiva, 0..360 en los datos de entrada de Luna y Marte; la Tierra usa -180..180. Las fuentes mezclan rangos (Apolo en -180..180, Surveyor y Marte en 0..360) y no declaran si la latitud es planetocéntrica o planetográfica. Para Marte, el USGS indica que adoptó latitud planetocéntrica con longitud este-positiva (https://planetarynames.wr.usgs.gov/Page/MARS/system); los datos de aterrizaje de la NSSDC para Viking también son planetocéntricos. `docs/aterrizajes_conocidos.csv` trae `lon_east_0_360` ya normalizada.

**Altitud absoluta:** no es una feature, porque los datums de elevación de la Tierra, la Luna y Marte no son comparables. Se guarda `elev_mean_m` solo como diagnóstico (no entra al modelo). Todas las `topo__*` se calculan sobre la misma base de ~500 m y una ventana de 50 × 50 km.

Agregar una feature: añadirla a `DIMENSIONS` en `src/analogos/config.py` y a esta tabla.
Pendientes (extras): polvo/viento, subsuelo (cuevas, tubos de lava), iluminación.
