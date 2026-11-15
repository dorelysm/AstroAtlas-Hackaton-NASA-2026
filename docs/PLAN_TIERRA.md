# Plan: datos reales de la Tierra sin descargar todo

Estado a 14 nov 2026. Tamaños tomados de la API de búsqueda de la NASA (CMR, sin login) el mismo día. **Verificado** = consultado hoy. **Sin verificar** = depende de algo que aún no hemos probado.

## Dónde estamos (Tierra, 1 057 celdas de 5° con tierra firme)
| Dimensión | Hoy | Problema |
|---|---|---|
| Topografía | real (Copernicus, 16 variables) | nada; ocupa 204 MB en caché |
| Térmica | POWER: temperatura del **aire** a 2 m | no es temperatura de superficie |
| Hielo/agua | proxy de precipitación (POWER) | no mide hielo ni agua del suelo |
| Geología | vacía | sin fuente |

Disco: `data/` ocupa 206 MB; quedan 74 GB libres. **El cuello de botella no es el disco, es el tiempo de descarga y que casi todo exige login de Earthdata.**

## Principios para que corra en un portátil
1. **Descargar, reducir y borrar.** Cada archivo grande se baja, se extrae solo el valor de las 1 057 celdas (una tabla de unos KB) y se borra. Disco máximo en uso: un archivo (≈70 a 320 MB). Lo que se guarda es la tabla.
2. **Productos mensuales o climatológicos, no diarios.** Un año de datos diarios son cientos de GB; el mensual son unos cientos de MB.
3. **Caché y reanudación.** Cada archivo ya reducido no se vuelve a pedir (como hace ya `data/copernicus.py`). Si se corta la red, se sigue donde se quedó.
4. **Embudo grueso → fino.** Se puntúa en la malla de 5° y solo los mejores candidatos (p. ej. 30 por sitio) se recalculan con más detalle, usando teselas ya en caché.
5. **Consulta por API cuando existe:** solo se baja el valor de los puntos pedidos, no el ráster.
6. **Tope de datos:** una opción `--max-gb` que se detiene antes de pasarse.

## Qué usar para cada dimensión

### Térmica: MODIS LST mensual (temperatura de superficie)
- **Producto:** `MOD11C3` v061 (Terra, 0.05°, global). **Verificado:** ~70 MB por mes (12 meses de 2019: 68 a 73 MB cada uno), cloud-hosted en LP DAAC.
- **Plan:** bajar los 12 meses de un año (≈840 MB en total, o 4 meses estacionales ≈280 MB), extraer `LST_Day` y `LST_Night` de cada celda, borrar cada archivo tras reducirlo.
- **Variables:** `t_max_k` = máximo de los meses de LST diurna; `t_range_k` = media de (día − noche).
- **Limitación importante:** son **medias mensuales**, no el pico instantáneo. Sale por debajo del máximo real de la Tierra y muy por debajo de los ~395 K lunares de Diviner. Esta dimensión seguirá sin ser comparable con la Luna. Conviene bajar su peso o puntuar por rango, no por valor absoluto.
- **Alternativa sin descargar rásteres:** AppEEARS (API) acepta puntos y devuelve un CSV con la serie temporal. **Sin verificar** el límite de puntos por petición; probar con 20 puntos antes de lanzar los 1 057.

### Hielo y agua: nieve y humedad del suelo
- **Nieve:** `MOD10CM` (cobertura mensual de nieve, 0.05°, NSIDC). **Verificado:** ~1.2 MB por mes, **≈15 MB al año**. Variable propuesta: fracción del año con nieve.
- **Humedad del suelo y agua en nieve:** GLDAS Noah mensual 0.25° (GES DISC). **Verificado:** ~24 MB por mes, ≈280 MB al año. Alternativa: SMAP L3 diario 36 km (17 a 35 MB por día; muestrear 12 días repartidos en el año ≈ 400 MB).
- **Honestidad semántica:** la Luna mide "fracción de área con hielo estable a ≤ 1 m", Marte "% de agua en masa" y la Tierra sería "nieve y humedad". **No miden lo mismo.** Para un análogo de hielo subsuperficial lo ideal es permafrost, pero el producto que apareció (ESA Permafrost CCI) no es de la NASA; solo se usa si el equipo relaja esa regla.

### Geología: emisividad ASTER como índice máfico
- **Producto:** ASTER GED mensual 0.05° (`AG5KMMOH`, LP DAAC). **Verificado:** ~321 MB por archivo. Como la emisividad casi no cambia con el mes, **basta un mes (≈320 MB)**.
- **Reto científico:** hay que definir un índice máfico (parecido al basalto) a partir de las bandas de emisividad. **No lo definimos aquí**: hay que citar una referencia y validarlo con zonas basálticas conocidas (Hawái, Islandia, Decán, río Columbia) frente a zonas no basálticas antes de usarlo. Si no sale limpio, mejor dejar `geo__*` en NaN que inventar un proxy.

### Topografía (ya hecha)
- Copernicus GLO-90 leído decimado a 360 m, 204 MB en caché. Siguiente mejora: en el paso fino, releer los candidatos a 90 m.

## Presupuesto de datos
| Fuente | Descarga | Se queda en disco |
|---|---|---|
| Copernicus (ya hecho) | 204 MB | 204 MB (caché) |
| MODIS LST, 12 meses | ~840 MB | < 1 MB (tabla) |
| Nieve MOD10CM, 12 meses | ~15 MB | < 1 MB |
| GLDAS, 12 meses | ~280 MB | < 1 MB |
| ASTER GED, 1 mes | ~320 MB | < 1 MB |
| **Total nuevo** | **≈1.5 GB** | **< 5 MB** |
Pico de disco durante la descarga: un archivo a la vez, unos 320 MB.

## Requisitos
- **Cuenta gratuita de Earthdata** (https://urs.earthdata.nasa.gov). Es obligatoria para MODIS, NSIDC, GES DISC y ASTER. La crea la persona del equipo; las credenciales van en `.env` (ver `.env.example`) y **nunca se comparten por chat ni se suben al repositorio**.
- `earthaccess` instalado en el entorno. **Sin verificar** que instale en Python 3.14; si falla, se descarga con `requests` y el token de Earthdata.
- MOD11C3, MOD10CM y GLDAS tienen formatos HDF4 o NetCDF; rasterio puede no abrir HDF4 (**sin verificar**). Plan B: `pyhdf` o `netCDF4`/`xarray`.

## Paso 1 completado (14 nov 2026): flujo de extremo a extremo verificado
- **Login de Earthdata:** funciona con las credenciales de `.env` (`earthaccess.login(strategy="environment")`).
- **`earthaccess` 0.19.0 instala en Python 3.14** con wheels (antes sin verificar).
- **Búsqueda y descarga:** un archivo `MOD10CM` de julio de 2019 (0.98 MB) bajó bien a `data/raw/earthdata/`. Ojo: en CMR la versión de esa colección se llama `61`, no `061`; **buscar sin filtrar la versión**.
- **Formato HDF4:** el GDAL de rasterio **no lo abre** (comprobado). `pyhdf` sí tiene wheel para Python 3.14 en Windows y **lee el archivo** (`from pyhdf.SD import SD`). Ya está en el extra `data` de `pyproject.toml`.
- **Contenido de `MOD10CM`:** `Snow_Cover_Monthly_CMG` (3600 × 7200, uint8, 0.05°, válido 0 a 100, relleno 255) y `Snow_Spatial_QA`. Solo el 32.8 % de los píxeles es válido (tierra); el resto son códigos de océano o sin dato (211, 250, 254, 255), que hay que tratar como NaN.
- **Comprobación con puntos conocidos (julio 2019):** Groenlandia 100, Valles Secos 100, Everest 78, Sahara 0, Atacama 0, Alpes 0.

## Paso 2 (nieve) completado el 14 nov 2026
- **12 meses de `MOD10CM` (2019) sobre las 955 celdas + 10 análogos:** 15.8 MB descargados, 47 s, ningún archivo HDF queda en disco (cada uno se borra tras reducirlo; solo quedan vectores pequeños en `data/raw/earthdata/reduced/`).
- **`ice__water_frac` de la Tierra = nieve media anual**, en vez del proxy de precipitación. Control: Groenlandia 1.00, Antártida 1.00, Sahara 0.00, Amazonas 0.00 (el proxy anterior daba 1.00).
- **Hallazgo y arreglo:** el océano costero de Copernicus (0 m) se colaba como terreno plano. Filtro `is_flat_ocean` en `earth.py`: 102 celdas fuera, quedan 955.
- **GLDAS bloqueado por una licencia:** hay que aceptar "NASA GESDISC DATA ARCHIVE" en el perfil de Earthdata. Código listo y sin probar. No alimenta el modelo (solo diagnóstico), así que no bloquea nada.
- **72 → 73 tests.**

## Paso 3 (temperatura de superficie) completado el 14 nov 2026
- **12 meses de `MOD11C3` (2019):** 886.7 MB en 168 s (~7 MB/s), cada archivo borrado tras reducirlo; solo quedan vectores pequeños. El acceso a LP DAAC funcionó sin aceptar licencias extra.
- **`thermal__t_max_k` (máximo de la LST diurna mensual) y `thermal__t_range_k` (día − noche)** ahora son de **superficie**. 938 de 955 celdas con dato (las 17 sin dato son casi todas la plataforma de hielo de Ross).
- **Corrección:** el "rango" anterior de POWER (mediana 56 K) era el rango estacional del aire; el diurno real tiene mediana 6.5 K.
- **Sigue sin ser comparable con la Luna:** máximo de la Tierra 332 K frente a ~395 K de Diviner; rango diurno máximo 34 K frente a ~300 K en la Luna. Son medias mensuales y la Tierra no alcanza esas temperaturas. Esta dimensión sirve para comparar entre celdas terrestres, pero para los sitios lunares ecuatoriales puntuará cerca de 0 con cualquier celda.

## Paso 4 (geología) probado y descartado el 14 nov 2026
- ASTER GED (337 MB, un archivo) con el índice máfico `b12/b13`: separa basalto de arena donde hay dato, pero solo **9 % de las celdas** son utilizables y el método sesga hacia lo félsico. Detalle y cifras en `docs/FUENTES.md`. `geo__*` de la Tierra queda en NaN; el archivo de 337 MB se borró.
- **Decisión del equipo (14 nov 2026): se relajó la regla "solo NASA" solo para la geología** y se usó el mapa litológico GLiM (38 kB, CC-BY 3.0). Resultado: 11 de 13 sitios basálticos acertados y 0 falsos positivos; 715 de 955 celdas con dato. Ver `docs/FUENTES.md` y `src/analogos/data/earth_geology.py`.

## Pasos
1. **Cuenta y prueba de login:** descargar un solo archivo de MOD10CM (1.2 MB) como prueba de extremo a extremo. *Bloquea todo lo demás.*
2. **Nieve y GLDAS** (los más pequeños): validan el flujo descargar → reducir → borrar con poco riesgo.
3. **MODIS LST mensual:** lo mismo, un mes primero, luego los 12.
4. **ASTER GED y el índice máfico**, con su validación.
5. **Embudo fino** para los mejores candidatos de cada sitio.
6. **Comprobaciones:** Atacama (cálido y seco), Valles Secos (frío), Death Valley (muy cálido), Groenlandia (nieve ≈ 1) y Sahara (nieve ≈ 0); y tests con archivos falsos para no depender de la red.

## Riesgos
- **Login y cuotas:** si Earthdata falla o se corta, los pasos 2 a 4 se bloquean. Mientras tanto POWER sigue como respaldo.
- **Formato HDF4** sin soporte en el entorno.
- **Comparabilidad:** aunque la Tierra tenga datos reales, térmica e hielo no equivalen a lo que se mide en la Luna y Marte. Hay que decirlo en las fichas.
- **Una sola ventana de 50 km por celda de 5°:** cada celda de 5° (~300 000 km² en el ecuador) se resume con una ventana de 2 500 km², menos del 1 % de su área; un cambio de resolución de la malla cambia los resultados.
