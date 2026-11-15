# Dimensiones del reto que el modelo no cubre (15 nov 2026)

El reto sugiere varias dimensiones. Estado de cada una:

| Dimensión del reto | Estado | Qué hay |
|---|---|---|
| Geología y materiales | Modelada (débil) | `geo__basalt_frac` (GLiM 0.5°, un solo tipo de roca) |
| Topografía | Modelada | 16 variables, PCA blanqueada |
| Temperatura | Modelada (limitada) | LST mensual; la Tierra no reproduce los extremos diarios de Marte; Marte vacía |
| Agua y hielo | Modelada (floja) | Nieve; no mide sequedad ni hielo subsuperficial (GLDAS probado, no mejora) |
| **Biología / habitabilidad** | **Marca de contexto** | `vegetated` (NDVI MODIS): oculta selvas y bosques. No mide extremófilos ni biofirmas |
| Asentamientos / logística | Marca de contexto | `viable` (GRUMP). No mide accesibilidad ni seguridad |
| **Polvo, viento y erosión** | **Solo contexto descriptivo** | `dust_surface_ugm3`, `dust_column_mgm2` y `wind10m_ms` (MERRA-2, 2019, rejilla 0.5° × 0.625°) en `earth*.parquet` y en las fichas. **No hay contraparte** en Marte (haría falta la opacidad de polvo de MCS/TES) ni en la Luna, así que no se puntúa similitud |
| **Cuevas y tubos de lava** | **Solo contexto** | Pits lunares (LROC, 278) integrados en `moon.parquet`; tubos terrestres de Pyroduct solo por región (sin coordenadas); catálogo de Marte (USGS) pendiente de descarga manual. Ver [CUEVAS.md](CUEVAS.md) |
| **Iluminación polar** | **No cubierta** | LOLA publica mapas de iluminación para la Luna, pero la Tierra no tiene un equivalente comparable (la noche polar terrestre depende de la inclinación del eje, no del relieve) |
| Procesos (no solo lugares) | No cubierta | El método compara lugares, no procesos |

## Por qué no se añadieron más
Polvo/viento y cuevas necesitan una fuente en **ambos** cuerpos y una validación con análogos etiquetados por esas dimensiones, y hoy no se tienen ni una cosa ni la otra. Añadir variables sin contraparte o sin validación aumentaría la apariencia de rigor sin el rigor. Lo que sí se hizo fue la marca de vegetación, que corrige un fallo real (selvas como candidatas) con una fuente NASA abierta.
Polvo y viento se añadieron solo como contexto descriptivo (15 nov 2026). Para puntuarlos haría falta la contraparte marciana; es el siguiente paso si el equipo lo quiere.
