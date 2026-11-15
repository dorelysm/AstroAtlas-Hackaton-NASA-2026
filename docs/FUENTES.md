# Procedencia de los datos

Registro de dónde sale cada dato del repositorio y qué tan fiable es. Actualizar cada vez que se añada o cambie un dato.

**Fecha de las búsquedas:** 14 de noviembre de 2026.
**Cómo se obtuvieron:** tres búsquedas web hechas por agentes de IA (modelo Haiku) que abrieron las páginas con una herramienta de descarga de páginas. Un agente de IA puede equivocarse al transcribir, así que **antes de citar un dato en la entrega final hay que abrir la URL de la columna `source_url` y comprobarlo**.

## Niveles de confianza

| Nivel | Significado |
|---|---|
| **Verificado** | El agente abrió la página y copió el valor de ahí. Falta una segunda comprobación humana. |
| **Verificado (fuente secundaria)** | La página abierta no es de la agencia, pero cita un paper. |
| **NO VERIFICADO** | Valor visto solo en un resumen de búsqueda o en una fuente que no se pudo abrir. No usar sin confirmar. |
| **Sin comprobar** | Escrito por nosotros de memoria, sin fuente. |
| **Wikipedia** | Coordenada tomada de Wikipedia, que no cita fuente primaria. Orientativa, no oficial. |

## Archivos y su origen

### `docs/aterrizajes_conocidos.csv` (34 filas)
Coordenadas de sitios de aterrizaje en la Luna y Marte. Origen por bloque:

| Bloque | Fuente | Nivel |
|---|---|---|
| Apolo 11, 12, 14, 15, 16, 17 | NASA NSSDCA: https://nssdc.gsfc.nasa.gov/planetary/lunar/lunar_sites.html | Verificado |
| Surveyor 1, 3, 5, 6, 7 | NASA NSSDCA: https://nssdc.gsfc.nasa.gov/planetary/lunar/surveyor.html | Verificado |
| Chang'e 6 | NASA Goddard: https://www.nasa.gov/centers-and-facilities/goddard/nasas-lro-spots-chinas-change-6-spacecraft-on-lunar-far-side | Verificado (aproximado: ~42° S, ~206° E) |
| Chang'e 4 | LROC (Arizona State University): https://lroc.im-ldi.com/posts/1087 | Verificado (no es fuente de la agencia china) |
| Viking 1 y 2, Pathfinder, Spirit, Opportunity, Phoenix, Curiosity | Mars Orbital Data Explorer (Universidad de Washington en San Luis): https://ode.rsl.wustl.edu/mars/pagehelp/Content/Missions_Instruments/Landing_Sites.htm | Verificado |
| Candidatos MSL (Gale, Eberswalde, Holden, Mawrth) | misma página del Mars Orbital Data Explorer (Golombek 2011) | Verificado (candidatos, no aterrizajes) |
| InSight (4.502° N, 135.623° E) | planetary.org, que cita a Golombek 2019 | Verificado (fuente secundaria) |
| InSight, centro de elipse (4.5° N, 135.9° E) | NASA: https://science.nasa.gov/resource/insights-landing-site-elysium-planitia/ | Verificado, pero es el objetivo, no el punto real |
| Artemis III (nombres de regiones) | Comunicados de NASA de agosto de 2022 y octubre de 2024 (URLs en el CSV) | Verificado; **NASA no publica coordenadas** |
| Chandrayaan-3, SLIM, Oxia Planum | fuentes secundarias (Wikipedia, LROC, ISRO/JAXA sin abrir) | NO VERIFICADO |
| Perseverance (decimales), Zhurong | resúmenes de búsqueda (Nature Astronomy pide login) | NO VERIFICADO |
| Mars Polar Lander, Beagle 2 | planetary.org (fuente secundaria) | NO VERIFICADO |

Sin coordenadas por falta de fuente fiable: regiones de Artemis III, Mars 2, 3 y 6, Schiaparelli, Deep Space 2, NE Syrtis y Columbia Hills.

### `docs/analogos_conocidos.csv` (10 filas) y `docs/sitios_objetivo.csv` (6 filas)
Escritos de memoria al montar el esqueleto y **contrastados después con una cuarta búsqueda web** (agente Haiku, 14 nov 2026). Las columnas `coord_source`, `reason_source_url` y `status` dicen de dónde sale cada valor. Resultado:

**Coordenadas:** casi todas vienen de **Wikipedia**, que no cita fuente primaria para ellas (solo enlaza GeoHack). Sirven para ubicar el lugar pero **no son fuente oficial**. Las de Craters of the Moon, Death Valley, Haughton, Lanzarote y Askja cambiaron algo respecto a mi valor de memoria (hasta ~38 km); usamos las de Wikipedia. Para sitios que son regiones (Atacama, Dry Valleys, Svalbard) la coordenada es un punto representativo, no un centro.

**Por qué es análogo:**
- Verificado en NASA: Dry Valleys (Earth Observatory) y Rio Tinto (NASA Astrobiology).
- Verificado en ESA: Lanzarote (solo Marte).
- Verificado en fuentes que no son NASA/ESA: Atacama (artículo en Frontiers), Haughton (Mars Institute), Craters of the Moon y Death Valley (Servicio de Parques Nacionales de EE. UU.).
- **No verificado:** Mauna Kea, Askja y Svalbard.

**Sitios objetivo:**
- Verificado en USGS: Mons Malapert (-85.98°, -1.67°, es decir 358.33° E).
- Los demás usan Wikipedia, y el Gazetteer del USGS devolvió error 500 en las búsquedas.
- **Cambios respecto a la primera versión:**
  - Las longitudes pasaron a 0–360 este-positivas, igual que el resto del repo.
  - Arcadia Planitia pasó de 47°, -170° a 47.25°, 196° E, centro del estudio piloto de SWIM (NASA/USGS). Este valor sigue sin verificar en una página abierta.
  - Oxia Planum queda en 18.2°, 335.7° E (ESA 2018 según planetary.org); Wikipedia da 18.275°, 335.368°. ESA dio 404.
  - Shackleton (-89.9°) es prácticamente el polo sur, así que se describe como "borde / polo sur" y no como un punto central.

### `docs/features.md`
- La **tabla de features y sus fuentes** es una propuesta nuestra, no se ha comprobado que cada dataset exista en la resolución necesaria.
- La **convención de coordenadas** viene de la documentación del USGS: https://planetarynames.wr.usgs.gov/Page/MARS/system (Marte: latitud planetocéntrica y longitud este-positiva) y de la página de Viking de la NSSDC: https://nssdc.gsfc.nasa.gov/planetary/viking.html.

### `PLAN.md` y `recursos.md`
- `recursos.md` es el listado oficial del reto, salvo la sección "Sitios de aterrizaje conocidos", que añadimos nosotros con las URLs de arriba.
- La tabla de datasets de `PLAN.md` (MOLA, THEMIS, CRISM, GLiM, etc.) es una propuesta de trabajo escrita de memoria. No se han abierto esas fuentes.

### `data/features/*.parquet` (si existen)
Si se generaron con `python -m analogos.synthetic`, son **datos sintéticos**: aleatorios y sin valor científico, y cualquier métrica calculada con ellos (AUC, recall) no significa nada. `moon.parquet` y `mars.parquet` generados con `python -m analogos.data.moon` / `mars` sí son datos reales (sección siguiente).

### `data/features/moon.parquet` y `mars.parquet`: todas las variables desde el NASA PDS
**Regla del equipo:** todo dato que entra al modelo viene de la NASA. Para la Luna y Marte, todo sale del **NASA Planetary Data System, Geosciences Node** (`pds-geosciences.wustl.edu`). URLs comprobadas con HTTP 200 el 14 de noviembre de 2026. Código: `src/analogos/data/pds_dem.py` (topografía) y `src/analogos/data/planetary.py` (resto). Ventana: celdas con centro a ≤ 25 km del sitio; si el producto es más grueso, la celda más cercana.

| Variable | Cuerpo | Producto (misión NASA) | URL | Referencia | Nivel |
|---|---|---|---|---|---|
| `topo__*` | Luna | LRO LOLA LDEM_256 (256 px/°, ~118 m) | https://pds-geosciences.wustl.edu/lro/lro-l-lola-3-rdr-v1/lrolol_1xxx/data/lola_gdr/cylindrical/img/ | LOLA GDR | Verificado. Sustituye al mosaico del USGS (mismos datos); elevaciones comprobadas: Apolo 11 −1 935 m |
| `topo__*` | Marte | MGS MOLA MEGDR 128 px/° (~463 m) | https://pds-geosciences.wustl.edu/mgs/mgs-m-mola-5-megdr-l3-v1/mgsl_300x/meg128/ | MOLA MEGDR | Verificado. Sustituye al mosaico del USGS; Olympus Mons 20 018 m, Jezero −2 647 m, Gale −4 502 m |
| `thermal__t_max_k`, `thermal__t_range_k` | Luna | LRO Diviner, Global Cumulative Products, temperatura bolométrica, 0.5° × 0.25 h de hora local | https://pds-geosciences.wustl.edu/lro/urn-nasa-pds-lro_diviner_derived1/data_derived_gcp/ | Williams et al. (2017), Icarus 283, 300-325 | Verificado. Máxima y (máx − mín) de la curva diurna, media ponderada por área |
| `ice__water_frac` | Luna | LRO Diviner, Polar Resource Product sur | https://pds-geosciences.wustl.edu/lro/urn-nasa-pds-lro_diviner_derived1/data_derived_prp/ | Paige et al. (2010), Science 330, 479 | Verificado. Fracción del área con hielo estable a ≤ 1 m; es un modelo térmico ajustado a datos. Solo > 80° S; **fuera de esa zona queda NaN** (antes se ponía 0 por supuesto; corregido el 14 nov) |
| `geo__basalt_frac` | Luna | Lunar Prospector GRS, abundancias elementales (FeO), píxel de 5° | https://pds-geosciences.wustl.edu/lunar/lp-l-grs-5-elem-abundance-v1/lp_9001/data/ | Prettyman et al. (2006), JGR 111, E12007 | Verificado. **Proxy nuestro**: (FeO − 5) / 15, recortado a 0-1 |
| `ice__water_frac` | Marte | Mars Odyssey GRS, H2O_SR_5X5 (H2O en % en masa) | https://pds-geosciences.wustl.edu/ody/ody-m-grs-5-elements-v1/odgm_xxxx/data/smoothed/ | ODY-M-GRS-5-ELEMENTS-V1.0 | Verificado. % / 100. Sin dato más allá de ±57.5° y con huecos entre 45° y 60° (comprobado en la tabla: 94 de 216 celdas con dato entre 45° y 60° N/S). Arcadia (47.25° N) y Phoenix (68.2° N) quedan en NaN |
| `geo__basalt_frac` | Marte | Mars Odyssey GRS, FE_SR_5X5 (Fe en % en masa) | misma URL | ODY-M-GRS-5-ELEMENTS-V1.0 | Verificado. Mismo proxy que la Luna con FeO = Fe × 1.2865; satura en 1 en casi todo Marte |
| `thermal__*` | Marte | — | — | — | **SIN DATO**: no hay mapa de temperatura máxima/mínima en el PDS. Queda NaN |

**Comparabilidad:** `ice__water_frac` no mide lo mismo en cada cuerpo (Luna: área con hielo estable según un modelo; Marte: % de agua medido; Tierra: proxy de precipitación). Hay que decirlo en las fichas.

### `data/features/earth.parquet` y `earth_sites.parquet`: datos reales de la Tierra (14 nov 2026)
Malla de 5° (955 celdas de tierra firme; `earth_sites` = los 10 análogos conocidos, solo para comparar y validar). Ventana de 50 × 50 km por celda. Código: `src/analogos/data/{copernicus,earth,earth_water,edl}.py`. Plan y tamaños en `docs/PLAN_TIERRA.md`.

| Variable | Producto (agencia) | Detalle | Nivel |
|---|---|---|---|
| `topo__*` | Copernicus GLO-90 (ESA, AWS Open Data) | teselas 1° leídas decimadas a ~360 m; base común de 500 m con Luna y Marte | Verificado (Death Valley -85.5 m, Mar Muerto -427 m, Polo Sur 2 801 m; Everest sale en 8 605 m por la decimación) |
| `thermal__t_max_k`, `thermal__t_range_k` | MODIS/Terra LST Monthly `MOD11C3` v061 (NASA LP DAAC), año 2019 | **temperatura de superficie**. `t_max` = máximo de los 12 meses de la LST diurna media mensual; `t_range` = media de (día − noche). 886.7 MB descargados en 168 s, cada archivo borrado tras reducirlo | Verificado (Death Valley 323 K, Sahara 324 K, Valles Secos 263 K, Antártida interior 251 K). **Medias mensuales, no el pico instantáneo** |
| `thermal_air_*` (diagnóstico) | POWER (NASA Langley) | temperatura del aire a 2 m, el valor anterior. Su "rango" era la diferencia **estacional** (mediana 56 K), no la diurna: estaba mal etiquetado | descartado |
| `ice__water_frac` | MODIS/Terra Snow Cover Monthly `MOD10CM` v061 (NASA NSIDC), año 2019 | media anual de la cobertura de nieve (0-1) de los píxeles válidos de la ventana. Descarga de 15.8 MB en total (12 archivos, cada uno borrado tras reducirlo) | Verificado (Groenlandia 1.00, Antártida 1.00, Sahara 0.00, Amazonas 0.00, Dry Valleys 1.00) |
| `ice_precip_proxy` (diagnóstico) | POWER | el proxy anterior de precipitación; se conserva pero **ya no entra al modelo** (daba 1.0 en el Amazonas) | descartado |
| `ice_snow_cover_max`, `ice_snow_months_valid` (diagnóstico) | MOD10CM | máximo mensual y nº de meses con dato | verificado |
| `geo__basalt_frac` | **GLiM** v1.0 en rejilla de 0.5° (Hartmann y Moosdorf 2012; **no es de la NASA**, excepción aprobada por el equipo el 14 nov 2026) | fracción de las celdas de roca de una ventana de **75 km** cuya clase litológica dominante es "volcánicas básicas" (`vb`). Descarga de 38 kB, CC-BY 3.0 | Verificado: acierta 11 de 13 sitios basálticos conocidos y 0 de 9 falsos positivos (ver abajo) |
| `geo_glim_mafic_frac`, `geo_glim_class`, `geo_glim_rock_cells` (diagnóstico) | GLiM | fracción máfica (volcánicas + plutónicas básicas), clase dominante y nº de celdas de roca | verificado |
| (probado y descartado) | ASTER GED (NASA LP DAAC) | índice máfico (banda 12 / banda 13, Ninomiya 2005) de la emisividad infrarroja | No usable: ver abajo |

**Geología de la Tierra: probada con ASTER GED y descartada (14 nov 2026).** Se bajó un archivo mensual `AG5KMMOH` (337 MB; emisividad = DN × 0.002 + 0.49 en 5 bandas térmicas, más NDVI), se calculó el índice máfico `MI = b12/b13` y se validó con lugares de litología conocida (ninguno de nuestra lista de análogos):
- **Donde hay dato, separa:** basalto (Mauna Loa 0.925, Pinacate 0.939, Harrat Rahat 0.957, Erta Ale 0.958) frente a arena y cuarzo (Rub al Khali 0.755, Gran Mar de Arena 0.791, Namib 0.809), con AUC emparejado 1.00. **Es una muestra de 4 contra 6.**
- **Pero cubre muy poco:** de los 10 lugares basálticos, 6 no tienen píxeles utilizables. Craters of the Moon y Harrat Khaybar tienen un espectro **plano y de alta emisividad (~0.97)**, típico de lava oscura, que la máscara de contraste descarta. Askja y otros salen planos por nieve o vegetación.
- **Cobertura en nuestra malla:** solo **84 de 955 celdas (9 %)** tienen ≥ 50 % de píxeles utilizables (0 de 273 al sur de 60° S, 0 de 180 al norte de 60° N; casi todas entre 0° y 30° N). En el **57 %** de las celdas el espectro es plano y de alta emisividad, y ahí lava oscura, hielo, agua y vegetación rala **son indistinguibles**.
- **Sesgo:** en las celdas que mezclan ambos tipos de píxel, la máscara se queda con los de contraste alto (arena, cenizas, rocas félsicas) y descarta la lava plana, es decir, sesgaría hacia lo félsico.
- **Conclusión:** como índice para `geo__basalt_frac` no es fiable y se sustituyó por GLiM (siguiente párrafo).

**Geología de la Tierra con GLiM (14 nov 2026).** Fuente: Hartmann, J. y Moosdorf, N. (2012), *Global Lithological Map Database v1.0 (gridded to 0.5° spatial resolution)*, PANGAEA, https://doi.org/10.1594/PANGAEA.788537; artículo: *Geochemistry, Geophysics, Geosystems* 13, Q12004, https://doi.org/10.1029/2012GC004370. Licencia CC-BY 3.0 (hay que citarlo). Archivo: `hartmann-moosdorf_2012.zip` (38.7 kB), de https://epic.awi.de/id/eprint/31092/ ; ESRI ASCII de 720 × 360 celdas con **una clase dominante por celda**; el zip se extrae con comprobación de rutas. Los significados de los códigos (`vb` = volcánicas básicas, etc.) salen del artículo, no del archivo.
- **Validación con lugares de litología conocida (ninguno de nuestra lista de análogos):** 11 de 13 sitios basálticos clasificados como `vb` (Mauna Loa, Craters of the Moon, Harrat Rahat y Khaybar, Pinacate, San Francisco, Erta Ale, Askja, Decán, Karoo, Paraná); 0 de 9 sitios sin basalto (arenales, Amazonas, escudo canadiense, Alpes) como `vb`. Fallos: **Etna** (sin dato en una celda costera) y el **basalto del río Columbia** (sale como sedimentos por el loess que lo cubre).
- **En nuestra malla:** 715 de 955 celdas con dato (240 son hielo, agua o sin dato: NaN), 81 con algo de basalto, 13 con 1.0. Las de más basalto son provincias reales: Etiopía, Paraná, islas Feroe, Haruj (Libia), zona volcánica de Ross y de Marie Byrd (Antártida). Análogos: Mauna Kea 0.75, Askja 1.00, Craters of the Moon 0.50, Atacama 0.00, Death Valley 0.00; Lanzarote sin dato (las islas pequeñas no entran en la rejilla de 0.5°).
- **Limitaciones:** (1) una sola clase dominante por celda de ~55 km: una celda con 40 % de basalto y 60 % de sedimentos cuenta como sedimentos, así que la fracción **subestima**; (2) por eso la ventana es de 75 km (~2 × 2 a 3 × 3 celdas), mayor que los 25 km del resto de variables; (3) la fracción de basalto de la Tierra (área de roca) **no mide lo mismo** que el proxy lunar y marciano (basado en FeO); (4) bajo hielo (Antártida) GLiM da la roca subglaciar, que no es superficie visible.
- **Excepción a la regla "solo NASA":** decidida por el equipo; el resto de la dimensión geología de la Luna y Marte sigue siendo del PDS.

**Limitaciones de la nieve como "hielo":** no es hielo subsuperficial (la Luna mide hielo estable a ≤ 1 m y Marte agua en el suelo). En la noche polar el producto no tiene dato, así que la media anual de las celdas polares usa solo los meses con luz (7 a 11 de 12); sesgo hacia valores altos. 20 celdas (casi todas la plataforma de hielo de Ross) quedan en NaN porque MODIS las enmascara como océano. El hielo marino puede contar como nieve.

**Agua (océano, lagos y mares interiores):** Copernicus rellena el agua con una cota constante (0 m en el mar), y sin filtro esas celdas salían como "llanuras perfectas". Se descartan las celdas con **relieve local < 1 m a cualquier altitud** (14 nov, segunda versión; la primera exigía además elevación ~0 y dejaba pasar lagos como el Michigan o el Caspio). Con la malla de 5° el terreno llano real más plano (hielo antártico, humedales, llanuras) tiene relieve >= 4 m, así que hay margen. Quedan 951 celdas. Puede quitar alguna isla pequeña (p. ej. la de las islas Feroe, casi todo mar en la ventana de 50 km).

**Pendiente:** GLDAS (humedad del suelo y agua en nieve) está implementado en `earth_water.py` (`--gldas`) pero **sin probar con datos reales**: requiere aceptar en el perfil de Earthdata la licencia "NASA GESDISC DATA ARCHIVE" (error `EulaNotAccepted`).

### Revisión de la entrega del PDS (14 nov 2026) y limitaciones que quedan
Integrada con `dem.py` fusionado (acepta un DEM ya creado y conserva los reintentos de red). La topografía del PDS coincide con la que se había calculado antes con los mosaicos del USGS (p. ej. Shackleton 11.52° en ambas). Problemas abiertos:

- **`thermal__*` de Marte vacío (14/14 sitios).** Búsqueda del 14 nov: **no hay un mapa global listo de temperatura máxima/mínima en el PDS**, así que la afirmación de la entrega es correcta en lo esencial. Hay dos caminos, comprobados:
  - **MRO MCS, DDR v5** (PDS Atmospheres Node, NMSU; `https://atmos.nmsu.edu/PDS/data/MROM_2062/...`). Cada perfil trae `T_SURF` (temperatura de superficie, K), `SURF_LAT/LON`, `LTST` (hora solar local) y `L_S` (comprobado en `MCS_DDR1.FMT`). No hay producto en rejilla: hay que descargar y filtrar. Archivos de ~7 MB por tramo de 4 h (6 al día, unos 393 perfiles cada uno), ~29 GB por año marciano. Permitiría estimar la máxima (tarde) y el rango (tarde − noche) por sitio, con pocas decenas de perfiles por sitio y año.
  - **MGS TES, mapas de inercia térmica `MGS-M-TES-5-TIMAP-V1.0`** (PDS Geosciences, `https://pds-geosciences.wustl.edu/mgs/mgs-m-tes-5-timap-v1/mgst_9001/data/`). Mapas global día y noche, 7200 × 3600 int16 (20 px/°, ~3 km), 51.8 MB cada uno, con máscara de píxeles interpolados (< 8 %). **Solo inercia térmica** (5 a 5000 J m⁻² K⁻¹ s⁻½), no temperatura. Es lo que controla la amplitud diurna, pero no equivale a `t_max`/`t_range`.
  - **Decisión del equipo (14 nov): no se usa ninguno de los dos caminos.** `thermal__*` de Marte queda en NaN y la dimensión térmica no puntúa para los sitios marcianos (el modelo la ignora). Consecuencia: los sitios de Marte se comparan con la Tierra solo en topografía, hielo y geología, y los de la Luna en las cuatro dimensiones, así que sus puntuaciones no son comparables entre cuerpos. Se puede reabrir si sobra tiempo.
  - Descartados: TES "sampler" de temperatura global (solo imágenes GIF), mosaicos THEMIS IR del USGS (temperatura *relativa*, estirada y mezclada, no calibrada) y TES TSDR (registros crudos, enormes).
- ~~`ice__water_frac` de la Luna = 0 por supuesto~~ **Corregido (14 nov):** los 13 sitios fuera de la cobertura de Diviner (> 80° S) ahora son NaN; solo Shackleton (0.60) y Malapert (0.42) tienen dato. Consecuencia: en esos 13 sitios la dimensión de hielo ya no puntúa (se ignora), en vez de comparar contra un 0 inventado. El polo norte tampoco está cubierto por este archivo.
- **`geo__basalt_frac` de Marte satura en 1.0** en casi todos los sitios: el proxy (FeO de 5 a 20 %) está calibrado para la Luna y en Marte no discrimina.
- ~~Hielo en Marte~~ **Aclarado (14 nov):** el parser es correcto. El producto H2O_SR_5X5 no cubre más allá de ±57.5° y tiene huecos entre 45° y 60° (Viking 2 cae en una celda con dato; Arcadia y Phoenix en celdas sin dato). Los NaN son reales. Los datos de hielo de latitudes altas de Marte (donde está el agua) no están en este producto; hay que buscarlos aparte.
- **Escalas no comparables entre cuerpos:** el hielo es una fracción modelada en la Luna, un % medido en Marte y un proxy de precipitación en la Tierra. La temperatura lunar de superficie (~395 K en el ecuador) queda fuera de todo el rango de la Tierra (POWER mide aire y llega a ~330 K): los sitios lunares ecuatoriales puntuarán casi 0 en esa dimensión contra cualquier celda terrestre.
- **`geo__*` de la Tierra vacío:** sin litología, esa dimensión no se compara y el modelo la ignora.
- Detalle menor: `planetary.py` usa un radio de Marte de 3389.5 km y `pds_dem.py` 3396 km (0.2 %, sin efecto relevante).

## Problemas conocidos en las fuentes
- **Signo de longitud en NSSDC:** Apolo 12 y 14 tienen longitud negativa en una columna que dice "°E". Interpretamos que negativo = oeste y lo convertimos a 0–360 (336.58 y 342.53), pero la página no lo dice. La página de Apolo 12 usa "23.42 W", lo que lo apoya.
- **NSSDC Mars Mileage Guide:** las longitudes de Spirit y Opportunity parecen intercambiadas. No se usó.
- **Viking 1 y Pathfinder:** tres fuentes dan valores distintos (por ejemplo Viking 1: 22.269° N / 312.049° E en ODE, 22.54° N / 48.23° O en la Mileage Guide). Se usó el Mars Orbital Data Explorer sin resolver cuál es el correcto.
- **Chandrayaan-3:** ISRO da el sitio previsto, no el punto real de toma de contacto.
- **Páginas que no se pudieron abrir:** PDS Geosciences (403), Apollo Lunar Surface Journal (404), PDF de JAXA (403), ESA Oxia Planum (404), Nature Astronomy (login). Los ZIP/KML del Gazetteer del USGS no se descargaron.

## Pendiente de verificar
1. Abrir el catálogo maestro de la NSSDC y las páginas de HiRISE para Perseverance, Zhurong y los fallidos.
2. Descargar los ZIP/KML del Gazetteer del USGS y ver si traen puntos de aterrizaje.
3. Confirmar las coordenadas oficiales de SLIM, Chandrayaan-3 y Chang'e 3/5/6 con ISRO, JAXA y fuentes de la CNSA.
4. Sustituir las coordenadas de Wikipedia por fuentes primarias (USGS Gazetteer, NASA, GVP, GNIS) y verificar la analogía de Mauna Kea, Askja y Svalbard.
5. Verificar el centro de Arcadia Planitia en el PDF de SWIM, y el de Oxia Planum en ESA.
