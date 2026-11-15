# Preregistro: objetivos de hielo somero con evidencia publicada y variable de permafrost (15 nov 2026, escrito ANTES de calcular las características o ningún puntaje de estos objetivos)

**Motivo:** [PREREGISTRO_VALIDACION2.md](PREREGISTRO_VALIDACION2.md) y [PREREGISTRO_HIELO_POLAR.md](PREREGISTRO_HIELO_POLAR.md) dejaron la variable de permafrost sin una prueba justa: solo Phoenix era un objetivo claramente rico en hielo. Aquí se añaden objetivos de hielo somero **con evidencia publicada e independiente de nuestros datos** y se vuelve a probar, una sola vez, con el mismo diseño.

## Objetivos nuevos (8) y su procedencia
Lista fijada en `docs/objetivos_hielo_dundas.csv` (sha256 `02867f4eecc514ad`). Todas las coordenadas (latitud planetocéntrica, longitud este) se leen **del texto, las figuras y la Tabla 1** del artículo de acceso abierto de Dundas et al. (2021), *Widespread Exposures of Extensive Clean Shallow Ice in the Mid-Latitudes of Mars*, JGR Planets 126, e2020JE006617 (copia abierta: HAL hal-03186594): el cúmulo de escarpes de **Milankovič** (54,5 N, 213,5 E), el **escarpe S6** (56,9 S, 96,3 E), un **cráter con hielo expuesto** (69,3 N, 142,2 E) y los **5 sitios de la Tabla 1** (impactos con color helado). Son sitios donde **se ve hielo expuesto**; no dependen del índice de neutrones.
**Por qué solo 8:** el catálogo completo de escarpes (data release del USGS, DOI 10.5066/P9Y8FR1R) está tras una verificación anti-bots de ScienceBase que no se puede ni se debe saltar; se usan solo las coordenadas que el propio artículo da. Las Tablas S1 y S4 del suplemento no están en la copia abierta.
**Se excluyen** los sitios del artículo que no son ice-exposing confirmado (p. ej. el escarpe «sin coloración» de la Fig. 2B y el «marginal» de la Fig. 2A). Ninguno de los 8 está a menos de 15 km de un objetivo existente (el más cercano está a 541 km).

## Variable (sin cambios respecto de [PREREGISTRO_HIELO_POLAR.md](PREREGISTRO_HIELO_POLAR.md))
- **Marte:** clase *rico en hielo* = 1 para los 8 nuevos (evidencia publicada) y para **Phoenix** (índice de neutrones `H` ≥ ln 1,5, regla ya fijada); para los demás objetivos, la clase de `rico_en_hielo` ya calculada (Arcadia sigue «no», por la regla fijada).
- **Tierra:** *permafrost probable* si la temperatura media anual < 271 K (MODIS 2019, como antes).
- Estas clases sustituyen a `ice__water_frac` solo en la variante «permafrost». La variante **base** usa el `ice__water_frac` actual (con el hidrógeno de `h2o_sr_5x5`, que tiene huecos o NaN más allá de ≈ 42-57°). La topografía de los nuevos objetivos se calcula con MOLA (ventana de 50 km, como los demás); no hay térmica ni geología de Marte.

## Evaluación (fijada)
**Objetivos de hielo (9):** los 8 nuevos + Phoenix. **Análogos fríos:** los de la regla de [PREREGISTRO_GRUPOS.md](PREREGISTRO_GRUPOS.md) (temperatura máxima mensual diurna < 295 K) entre los 23 + los 9 del segundo conjunto (esperados: 5 + 2 = 7). **Pesos del modelo frío:** hielo 1, topografía 0,5, resto 0.
- **P1 (primaria):** u medio de los análogos fríos frente a los 9 objetivos de hielo con la variante permafrost; IC 95 % por bootstrap sobre los análogos. **Criterio: límite inferior > 0,5.**
- **P2 (primaria):** diferencia pareada por análogo frío (variante permafrost − base) con IC 95 %. **Criterio: límite inferior > 0.**
- **Se adopta solo si se cumplen P1 y P2.** Si no, la variable de permafrost no se adopta y el modelo no cambia.
- **Secundarias (no deciden):** (a) los 2 análogos fríos nuevos por separado; (b) el u de la variante base frente a los 9 objetivos de hielo (¿el modelo actual los reconoce con estos objetivos?); (c) efecto sobre el u medio de «todas» en Marte si se añaden los 8 objetivos al conjunto de 14 (diferencia pareada); (d) cuántos de los 8 son «ricos en hielo» según el índice de neutrones `H` (consistencia del índice con la evidencia publicada; no cambia ninguna clase).

## Qué no se hace
No se cambian los umbrales, la lista de objetivos, los análogos fríos, los pesos ni los criterios después de ver los números; cualquier variante se reporta aparte como exploratoria.

## Límites conocidos de antemano
Solo 7 análogos fríos (5 ya usados en pruebas anteriores, 2 independientes), así que el poder es bajo; los objetivos son puntos de evidencia local (un escarpe, un cráter) y la ventana de 50 km mezcla terreno distinto; sin térmica de Marte; las coordenadas vienen del artículo (planetocéntricas) y no se contrastaron con los datos primarios del USGS; el índice `H` tiene resolución de 5° y puede no marcar ricos a todos.

## Resultados (hash del protocolo `7513849a4b115d53`; lista `02867f4eecc514ad`; sin cambios al protocolo tras ver los números)
Código: `src/analogos/hielo_somero.py` (`python -m analogos.hielo_somero --build`, luego sin `--build`). Análogos fríos (7): Axel Heiberg, Fairbanks, Valles Secos, Eureka, Haughton, Svalbard, Tuktoyaktuk. Objetivos de hielo (9): los 8 nuevos + Phoenix.

| Análogo frío | u base | u permafrost | Diferencia |
|---|---|---|---|
| Axel Heiberg | 0,233 | 0,631 | +0,398 |
| Fairbanks (nuevo) | 0,411 | 0,755 | +0,344 |
| Valles Secos | 0,150 | 0,589 | +0,439 |
| Eureka | 0,515 | 0,840 | +0,325 |
| Haughton | 0,572 | 0,855 | +0,283 |
| Svalbard | 0,315 | 0,716 | +0,401 |
| Tuktoyaktuk (nuevo) | 0,607 | 0,883 | +0,276 |

| Criterio | Resultado | ¿Cumple? |
|---|---|---|
| **P1** u medio con permafrost, límite inferior > 0,5 | **0,753 (IC 0,672 a 0,829)** | **Sí** |
| **P2** diferencia pareada con la base, límite inferior > 0 | **+0,352 (IC +0,309 a +0,394)** | **Sí** |
| (b) u de la base frente a los objetivos de hielo | 0,400 (0,281 a 0,520) | (no decide) |
| (a) los 2 fríos nuevos | Fairbanks 0,41 → 0,76; Tuktoyaktuk 0,61 → 0,88 | (no decide) |
| (c) «todas» en Marte con los 22 objetivos | base 14 → base 22: −0,012 (−0,025 a +0,001); **base 14 → permafrost 22: −0,087 (−0,147 a −0,023)** | (no decide) |
| (d) índice de neutrones `H` en los 8 sitios | **4 de 8** «ricos» (Milankovič 0,62, S6 0,98, cráter 69° N 0,92, T1-c 0,43); T1-a, T1-b, T1-d y T1-e no (de −0,04 a 0,20) | (no decide) |

**Veredicto preregistrado: se cumplen P1 y P2, así que la variable de permafrost SE ADOPTA.** Es la primera idea de la serie que cumple su criterio.

### Alcance de la adopción (decisión tomada DESPUÉS de ver los números; el protocolo no lo fijaba)
- **Solo para el caso de uso «frío / hielo somero»** (pesos hielo 1, topografía 0,5), **no** para el puntaje global: la secundaria (c) muestra que con los 22 objetivos y la clase de permafrost el u de «todas» en Marte **empeora (−0,087, IC −0,147 a −0,023)**, y la prueba independiente anterior ([PREREGISTRO_VALIDACION2.md](PREREGISTRO_VALIDACION2.md), V3) también dio un efecto global negativo. El modelo global no cambia.
- **No está integrada todavía** en `usecases.py`, el atlas ni la app.

### Lectura honesta (por qué este resultado hay que leerlo con cuidado)
- **Parte del efecto es por construcción.** Con una clase binaria, los 7 análogos fríos (todos de clase «permafrost») coinciden exactamente en la dimensión de hielo con los 9 objetivos (todos «ricos en hielo»), y la mitad de las celdas de la Tierra (470 de 934) también son «permafrost» por temperatura; el resultado mide sobre todo que **estar en la clase correcta basta para subir en el ranking**, no que el modelo distinga permafrost de otros terrenos fríos.
- **La prueba lo confirma: las candidatas frías son las capas de hielo**, no permafrost (exploratorio, no decide): las seis celdas de mayor puntaje son la Antártida interior y Groenlandia (p. ej. −82,5°, −102,5° y 77,5°, −17,5°), así que **no hay candidatas creíbles** para el caso frío con esta variable. Es el mismo problema del terreno llano ya visto con la topografía.
- **El índice de neutrones solo reconoce 4 de los 8 sitios** con hielo publicado: es una medida de 5° y de la parte somera, y dice «no rico» en cuatro sitios donde se ve hielo expuesto. Esto sugiere que la clase de neutrones subestima el hielo en los demás objetivos (p. ej. Arcadia, que quedó 0,015 bajo el umbral); en este experimento los 8 se fijaron como ricos por evidencia publicada, no por `H`.
- **Poder bajo e independencia parcial:** solo 7 análogos fríos, 5 de ellos ya usados en pruebas anteriores (aunque ninguna se usó para ajustar nada); los 2 nuevos (Fairbanks, Tuktoyaktuk) suben igual que el resto.
- **Los 8 objetivos vienen de un solo artículo** (que elige sitios donde hay hielo expuesto) y sus coordenadas no se contrastaron con el catálogo del USGS (inaccesible por la verificación anti-bots).
