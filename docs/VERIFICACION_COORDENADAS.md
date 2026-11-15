# Verificación de coordenadas y analogías (15 nov 2026)

Objetivo: sustituir coordenadas de Wikipedia por fuentes primarias antes de citarlas. **Resultado: verificación parcial.**
Se intentó abrir fuentes con una herramienta de descarga de páginas; varios servidores (USGS Gazetteer, NASA, Earth Impact Database,
SEDAC, Copernicus) rechazaron la conexión o devolvieron 404 en esta sesión, así que **la mayor parte sigue sin verificar**.

## Lo que sí se comprobó
| Sitio | Dato en el repo | Qué se encontró | Conclusión |
|---|---|---|---|
| Oxia Planum | 18.2° N, 335.7° E (ESA 2018) | Wikipedia cita la aprobación del IAU de 2019: **18.275° N, 335.368° E** (y a Quantin-Nataf et al. 2021, *Astrobiology*) | **Discrepancia de ~19 km en longitud**, dentro de la ventana de 50 km. No se cambió el CSV para no alterar resultados ya medidos; si se corrige hay que recalcular `mars.parquet` y repetir las evaluaciones |
| Jezero | 18.38° N, 77.58° E | Coincide con Wikipedia (18°23′N 77°35′E); la fuente primaria (Gazetteer del USGS) no se pudo abrir | Coordenada de centro del cráter plausible; sigue "no verificado en fuente primaria" |
| Río Tinto | 37.7° N, 6.55° O (valor de memoria) | Wikipedia da la desembocadura en 37.21° N, 6.94° O; no da la zona minera | La coordenada es la de la zona de las minas, no la desembocadura. Sigue sin fuente. La analogía con Marte sí está en una nota de NASA JPL de 2005 citada por Wikipedia (agua del depósito de Meridiani) |

## Lo que sigue sin verificar (hay que abrir a mano)
- **Análogos terrestres** (`docs/analogos_conocidos.csv`): coordenadas de Atacama, Haughton, Mauna Kea, Askja, Lanzarote, Svalbard, Craters of the Moon y Death Valley vienen de Wikipedia. Fuentes primarias sugeridas: Earth Impact Database (Haughton), Global Volcanism Program (Askja), USGS GNIS (Death Valley, Craters of the Moon). Los Valles Secos y Atacama son regiones: la coordenada es un punto representativo.
- **Analogías sin fuente:** Mauna Kea, Askja y Svalbard (la razón de la analogía no está comprobada).
- **Sitios objetivo:** Shackleton (aproximado), Mare Tranquillitatis pit, Jezero, Oxia Planum y Arcadia Planitia (la tabla SWIM no se pudo leer).
- **Sin tabla de LROC:** Chang'e 4 y Chang'e 6 (posteriores a 2016).

## Qué hay que hacer antes de citar
Abrir cada `source_url` / `coord_source` de los CSV y, para las filas anteriores, buscar la fuente primaria. Una persona del equipo puede hacerlo con acceso a esos sitios en unos 30 minutos; si se corrige alguna coordenada de un objetivo, repetir `python -m analogos.data.mars` (o `moon`) y las evaluaciones.
