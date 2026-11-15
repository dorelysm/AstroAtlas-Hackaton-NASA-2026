# Cuevas y tubos de lava (15 nov 2026)

**Resumen:** hay datos abiertos de pits lunares y de tubos de lava terrestres, pero **no se pueden convertir en una dimensión de similitud**:
el catálogo terrestre no trae coordenadas y el de Marte no se pudo descargar automáticamente. Se integraron como **contexto**.

## Qué datos hay
| Cuerpo | Fuente | Contenido | Licencia | Estado |
|---|---|---|---|---|
| Luna | Losarcos y Dombard (Zenodo 10.5281/zenodo.20516852, jun 2026), capa `Pit-locations` (de LROC QuickMap; Wagner y Robinson) | 278 pits: 257 en lagos de fusión por impacto, 16 en mares, 5 en tierras altas | CC BY 4.0 | **Integrado** (`pits_within_50km`, `nearest_pit_km`, `nearest_pit_name` en `moon.parquet`) |
| Tierra | Pyroduct Digital Catalog v1 (Romio y Lobosco 2024, Zenodo 10.5281/zenodo.14535886) | 93 tubos de lava documentados (índice en [tubos_lava_documentados.csv](tubos_lava_documentados.csv)); el catálogo completo son secciones transversales en un DXF de 498 MB que no se descargó | CC BY 4.0 | **Integrado como índice por región** (sin coordenadas) |
| Marte | Mars Global Cave Candidate Catalog (USGS, Cushing; release PDS 2019) | 1 062 candidatas con coordenadas, tipo (sky 354, srp 218, APC 132, crk 87, …) y prioridad | dominio público (USGS) | **Integrado** (`caves_within_50km`, `nearest_cave_km`, `nearest_cave_name` en `mars.parquet`). El servidor del USGS bloquea la descarga automática y no se intentó esquivarlo: la bajó una persona del equipo a `data/raw/mgc3/`. La cabecera del CSV está desordenada; se usa el orden del XML |

## Tubos de lava documentados por región (Pyroduct)
Hawái (EE. UU.) 22 · Azores (Portugal) 20 · Etna (Italia) 17 · **Harrat Al-Shaam (Jordania) 8** · Oregón (EE. UU.) 6 · La Palma 5 · Queensland 3 · Victoria 3 · **Lanzarote 2** · Nuevo México 2 · Vesubio 1 · Harrat Buqum (Arabia Saudí) 1 · Harrat Ithnayn (Arabia Saudí) 1.
Que una región no aparezca **no** significa que no tenga tubos: el propio catálogo avisa de que no cubre todos los países (por ejemplo Haruj, en Libia, y Craters of the Moon no están).

## Resultados
1. **Marte:** ninguno de los 14 objetivos tiene una candidata a cueva a menos de 50 km; la más cercana está a 895 km (Mawrth Vallis). Las candidatas se concentran en Tharsis y alrededores y **nuestros objetivos son sitios de aterrizaje de rover, no regiones de cuevas**. La dimensión de cuevas tampoco discrimina en Marte.
2. **Luna:** solo 1 de los 21 objetivos lunares tiene un pit a menos de 50 km, el propio *Mare Tranquillitatis pit*. Los otros 20 sitios de aterrizaje y objetivos no están cerca de ninguno. Un resultado esperable, pero significa que la dimensión de cuevas casi no discrimina entre nuestros objetivos.
3. **El modelo no ve los tubos.** Los mejores análogos terrestres de *Mare Tranquillitatis pit* (puntaje 0,82-0,84) son celdas planas de hielo antártico, que solo coinciden por topografía (el resto de dimensiones no tiene dato). Ninguna es una región volcánica con tubos.
4. **Candidata A (Harrat ash-Shamah):** el catálogo documenta **8 tubos de lava en Harrat Al-Shaam (Jordania)**. Es la misma región volcánica que la candidata, aunque no se puede asegurar que estén dentro de la celda de 50 km (no hay coordenadas). Es un punto a favor de la candidata como análogo de cuevas, no una validación. **Candidata B (Haruj):** el catálogo no la cubre.
5. **Análogos conocidos:** Mauna Kea (Hawái, 22 tubos) y Lanzarote (2) están en regiones con tubos documentados; Craters of the Moon, que tiene cuevas conocidas, no está en este catálogo.

## Por qué no es una dimensión
- Sin coordenadas de los tubos terrestres no se puede comparar celda por celda.
- Ningún objetivo de Marte y solo 1 de la Luna tiene una cueva o un pit cerca: la dimensión no distingue entre los objetivos actuales. Para que importara habría que añadir objetivos de cuevas (Tharsis, Marius Hills).
- Que no se haya detectado un pit en imágenes no significa que no exista; hay un sesgo de detección.
- Para hacerlo bien habría que construir una tabla de tubos terrestres con coordenadas a partir de la bibliografía (Hawái, Azores, Etna, Harrat, Canarias, Oregón, Queensland) y validarla con análogos etiquetados por cuevas; es trabajo para otra etapa.

## Para qué sirve ya
Para las fichas: indica si la región de un candidato tiene cuevas documentadas, y para la presentación: muestra qué existe y por qué no se usa como puntaje.
