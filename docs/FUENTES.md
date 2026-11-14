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
**Datos sintéticos** generados con `python -m analogos.synthetic`. Son aleatorios y no tienen valor científico. Cualquier métrica calculada con ellos (AUC, recall) no significa nada.

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
