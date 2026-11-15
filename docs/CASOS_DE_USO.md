# Análogos por caso de uso (15 nov 2026)

En lugar de un ranking único, seis perfiles de uso. Cada uno fija con qué objetivos se compara, qué dimensiones pesan y qué se puede afirmar.
Código: `src/analogos/usecases.py` (`python -m analogos.usecases`). Solo se consideran celdas viables y sin vegetación. **Son hipótesis**: la validación del modelo está cerca del azar.

## Resultados (3 regiones por caso, separadas ≥ 500 km)
| Caso de uso | Mejores celdas (lat, lon) | Puntaje | Lectura honesta |
|---|---|---|---|
| **Movilidad y aterrizaje, Marte** (12 sitios, topografía) | 37.5°, 92.5° · −72.5°, −72.5° · 22.5°, −2.5° | 0.51 · 0.51 · 0.50 | Parecido **moderado**. La primera cae en la cuenca de Qaidam (China), que por lo que sé se ha propuesto como análogo de Marte (**no verificado aquí**); la segunda es hielo antártico y la tercera el Sáhara occidental |
| **Movilidad y aterrizaje, Luna** (18 sitios, topografía) | 27.5°, 37.5° · 77.5°, −27.5° · 42.5°, 107.5° | 0.48 · 0.47 · 0.47 | Parecido **bajo**. La segunda es Groenlandia. Solo topografía |
| **Frío en polos lunares** (2 objetivos) | 37.5°, 87.5° · 37.5°, 72.5° · 72.5°, −87.5° | 0.24 · 0.22 · 0.21 | **Muy bajo**: la Tierra no reproduce una zona sombreada (< 100 K). La tercera está a 327 km de Haughton, el único análogo polar conocido, lo cual es coherente |
| **Hielo en el norte de Marte** (2 objetivos) | 17.5°, 27.5° · 22.5°, 52.5° · 32.5°, 37.5° | 0.74 · 0.74 · 0.74 | **Artefacto**: son desiertos sin nieve (Sáhara, Arabia). El puntaje alto es "no hay nieve", no hielo subsuperficial |
| **Terreno basáltico, Marte** (9 sitios, geología + topografía) | 32.5°, 37.5° · 27.5°, 17.5° · −77.5°, −127.5° | 0.78 · 0.69 · 0.66 | **El único caso con sentido claro**: las dos primeras son las candidatas de [FICHAS_CANDIDATOS.md](FICHAS_CANDIDATOS.md) (Harrat ash-Shamah y Haruj); la tercera es la zona volcánica de Marie Byrd (Antártida) |
| **Volcánico y tubos de lava, Luna** (8 sitios) | −87.5°, 52.5° · −82.5°, −132.5° · 77.5°, −27.5° | 0.54 · 0.53 · 0.52 | Todas en hielo polar; salen por topografía. **No ve los tubos** (solo 1 de 21 objetivos tiene un pit cerca, ver [CUEVAS.md](CUEVAS.md)) |

**Lectura global:** solo el caso basáltico de Marte da una recomendación defendible. Movilidad da parecidos moderados, y los casos de frío y hielo muestran los límites de la Tierra como análogo. Que el método lo diga explícitamente es parte del resultado.

## Por qué no se usan umbrales de ingeniería
Las variables del modelo son de una malla común de **500 m** y ventanas de 50 km. Los umbrales publicados se definen a escalas de metros y de 2 a 5 km, así que **no se pueden aplicar como umbrales absolutos** a estos datos. Por eso los casos de movilidad comparan con el terreno de sitios donde ya se aterrizó o se condujo (medida relativa). Los umbrales, solo como contexto (**por verificar en la fuente primaria**):

| Magnitud | Valor | Fuente (resultado de búsqueda, no verificado en el documento original) |
|---|---|---|
| Pendiente de aterrizaje de MSL (Curiosity) | ≤ 3° a escala de 2 a 5 km dentro de la elipse | [MSL Engineering User Guide](https://marsoweb.nas.nasa.gov/landingsites/msl/memoranda/MSL_Eng_User_Guide_v2.pdf) |
| Pendiente y rocas de InSight | < 15° a escalas de 84 m y 2 m; abundancia de rocas < 10 % | resultados de búsqueda sobre la selección del sitio de InSight |
| Aterrizaje de Starship HLS en la Luna | ≤ 8° respecto a la vertical (referencias de evaluación hablan de ≤ 10°) | [Evaluación de sitios de Artemis III](https://arxiv.org/pdf/2406.19863) y comunicados de NASA |
| Inclinación de rover que se evita al planear | ≈ 30° (Perseverance); tolerancia mecánica de 45° (Curiosity); récords de 31° y 32° | [NASA/JPL, Perseverance](https://www.jpl.nasa.gov/news/nasas-perseverance-rover-looks-back-while-climbing-slippery-slope/) |

## Qué falta para que sean más útiles
- Umbrales de ingeniería a la escala correcta: requeriría modelos digitales de terreno de metros (HiRISE en Marte, LROC NAC en la Luna) y sus equivalentes terrestres, no los de 90 m.
- Casos de uso con dimensiones nuevas (polvo y viento, cuevas) cuando haya contraparte marciana y análogos para validarlos.
