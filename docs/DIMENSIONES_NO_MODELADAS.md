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
| **Polvo, viento y erosión** | **No cubierta** | Haría falta un dato terrestre (p. ej. MERRA-2 de aerosoles y viento, NASA GES DISC, licencia ya aprobada) **y su contraparte en Marte** (opacidad de polvo de MCS/TES); sin la contraparte no se puede comparar |
| **Cuevas y tubos de lava** | **No cubierta** | No hay un catálogo global abierto de tubos de lava terrestres ni un mapa de cuevas comparable con los candidatos de pozos lunares/marcianos |
| **Iluminación polar** | **No cubierta** | LOLA publica mapas de iluminación para la Luna, pero la Tierra no tiene un equivalente comparable (la noche polar terrestre depende de la inclinación del eje, no del relieve) |
| Procesos (no solo lugares) | No cubierta | El método compara lugares, no procesos |

## Por qué no se añadieron más
Polvo/viento y cuevas necesitan una fuente en **ambos** cuerpos y una validación con análogos etiquetados por esas dimensiones, y hoy no se tienen ni una cosa ni la otra. Añadir variables sin contraparte o sin validación aumentaría la apariencia de rigor sin el rigor. Lo que sí se hizo fue la marca de vegetación, que corrige un fallo real (selvas como candidatas) con una fuente NASA abierta.
Si se quiere seguir: el siguiente paso más barato es polvo y viento terrestres con MERRA-2 solo como contexto descriptivo en las fichas, indicando que no hay contraparte marciana.
