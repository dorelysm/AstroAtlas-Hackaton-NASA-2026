# Preregistro: mapa de permafrost real en lugar de la regla de temperatura (15 nov 2026, escrito ANTES de calcular ninguna clase con este mapa)

**Motivo:** [PREREGISTRO_PERMAFROST_FRIO.md](PREREGISTRO_PERMAFROST_FRIO.md) mostró que la clase «permafrost probable» basada en temperatura (< 271 K) y nieve no separa permafrost de capas de hielo y deja candidatas poco creíbles. Aquí se sustituye por un **mapa de permafrost modelado y validado con sondeos**: Obu, Westermann, Kääb y Bartsch (2018), *Ground Temperature Map, 2000-2016, Northern Hemisphere Permafrost*, PANGAEA, [doi:10.1594/PANGAEA.888600](https://doi.org/10.1594/PANGAEA.888600) (licencia CC-BY 3.0; proyecto ESA GlobPermafrost). Archivo usado: `UiO_PEX_5.0_20181127_2000_2016_25km.nc` (25 km; variable `PerProb`, probabilidad de permafrost 0-1, solo sobre **tierra emergida sin hielo**, de 25° N a 84° N).

## Clase (fijada ahora; no se prueban otros umbrales)
**PF3 = 1** si la media de `PerProb` de los píxeles válidos cuyo centro está a ≤ 25 km del centro de la celda o sitio (la misma ventana de 25 km de MODIS) es **≥ 0,5**; si ningún píxel cae en la ventana se usa el más cercano si está a ≤ 30 km. **PF3 = 0** en cualquier otro caso, incluidos: capas de hielo y glaciares (el mapa no tiene dato), el hemisferio sur y las latitudes < 25° N (fuera de la cobertura), el mar y celdas sin píxel válido. Se aplica **igual** a las celdas de la Tierra y a los sitios análogos. Las clases de Marte no cambian (los 8 objetivos de hielo publicado + Phoenix = 1).
**Consecuencia conocida de antemano:** los Valles Secos (Antártida) quedan en clase 0, igual que con la regla anterior.

## Evaluación (fijada)
Mismo diseño que [PREREGISTRO_PERMAFROST_FRIO.md](PREREGISTRO_PERMAFROST_FRIO.md): pesos del modelo frío (hielo 1, topografía 0,5), 9 objetivos de hielo, variante base idéntica. **Análogos fríos:** los que cumplan la regla de [PREREGISTRO_GRUPOS.md](PREREGISTRO_GRUPOS.md) (temperatura máxima mensual diurna < 295 K) entre **los 45 análogos** de los tres conjuntos (se reporta además el subconjunto de los 7 de la prueba anterior).
- **R1:** u medio con PF3, límite inferior del IC 95 % (bootstrap sobre análogos) **> 0,5**.
- **R2:** diferencia pareada PF3 − base, límite inferior **> 0**.
- **R3 (credibilidad de las candidatas):** las 6 mejores regiones (≥ 500 km entre sí, `viable`, no vegetadas, a más de 500 km de cualquiera de los 45 análogos, puntaje = media sobre los 9 objetivos de hielo) deben tener **PF3 = 1**, estar fuera de la Antártida y de la capa de hielo de Groenlandia, y no ser un píxel solitario (la media de `PerProb` de su ventana ≥ 0,5 por definición de PF3).
- **Se integra al caso de uso frío solo si se cumplen R1, R2 y R3.** Si falla R1 o R2 la variable de permafrost se descarta para candidatas; si solo falla R3 se reporta y no se integra.
- **Descriptivo:** cuántas celdas tienen clase 1 con el mapa (frente a 190 con la regla de temperatura y nieve y 470 con la de temperatura sola); la concordancia entre ambas reglas; el valor de `PerProb` de cada análogo frío.
- **Control de novedad** (texto, no decide), solo si se integra: dos búsquedas fijadas por región para las 3 primeras (`<región> Mars analog permafrost ice`, `<región> planetary analogue cold desert`) y control positivo `Devon Island Mars analog permafrost`.

## Qué no se hace
No se cambian el umbral 0,5, la ventana, los objetivos, los análogos ni los criterios después de ver los resultados; cualquier variante se reporta aparte como exploratoria.

## Límites conocidos de antemano
El mapa es un **modelo** (error cuadrático medio de 2 °C frente a sondeos) a 25 km, que no ve el permafrost de montaña pequeño ni el del hemisferio sur; no distingue hielo en el suelo del permafrost seco; la clase binaria pierde información; los Valles Secos y el resto del hemisferio sur quedan sin dato; las candidatas son hipótesis, no medidas.

## Resultados (hash del protocolo `d5d333c504413cb2`; sin cambios al protocolo tras ver los números)
Código: `src/analogos/permafrost_mapa.py` (`python -m analogos.permafrost_mapa`). Mapa: Obu et al. (2018), 25 km, CC-BY 3.0 (descarga de 15 MB en `data/raw/permafrost/`, no versionada).
**Descriptivo:** con el mapa hay **144 celdas** de clase 1 (frente a 190 con la regla de temperatura y nieve y 470 con la de temperatura sola); de las 470 por temperatura, **331 no son permafrost según el mapa** (la regla de temperatura sobreestimaba). Análogos fríos (14, regla de temperatura máxima < 295 K sobre los 45 análogos): clase 1 en Axel Heiberg, Svalbard, Bockfjord, Murchison Fjord, Eureka, Haughton, Tuktoyaktuk y Golden Deposit (`PerProb` 0,95 a 1,00); **clase 0 en Fairbanks (0,28), Eyjafjallajökull, Krýsuvík, Pavilion Lake, Yellowstone (≈ 0) y los Valles Secos (sin dato)**.

| Criterio | Resultado | ¿Cumple? |
|---|---|---|
| **R1** u medio con PF3, límite inferior > 0,5 | **0,683 (IC 0,512 a 0,840)** | **Sí** (por poco) |
| **R2** diferencia pareada PF3 − base, límite inferior > 0 | **+0,244 (IC +0,100 a +0,391)** | **Sí** |
| **R3** las 6 candidatas son PF3 = 1, fuera de la Antártida y de capas de hielo | las 6 con `PerProb` = 1,0 | **Sí** |
| (subconjunto de los 7 análogos fríos de la prueba anterior) | u 0,726 (0,482 a 0,928); dif +0,326 (+0,140 a +0,505) | descriptivo |

Por análogo (base → PF3): Axel Heiberg 0,23 → 0,87; Svalbard 0,32 → 0,89; Bockfjord 0,26 → 0,88; Eureka 0,52 → 0,94; Haughton 0,57 → 0,95; Tuktoyaktuk 0,61 → 0,95; Golden Deposit 0,60 → 0,96; Murchison 0,58 → 0,97; **bajan** Pavilion Lake 0,30 → 0,12, Fairbanks 0,41 → 0,34, Eyjafjallajökull 0,42 → 0,36; sin cambio Krýsuvík, Yellowstone y Valles Secos.
**Veredicto preregistrado: se cumplen R1, R2 y R3; SE INTEGRA AL CASO DE USO FRÍO** (nuevo caso «Hielo en el suelo y permafrost (Marte), con mapa de permafrost» en `usecases.csv` y en la app). **El puntaje global del modelo no cambia.**

### Candidatas (6 regiones, puntaje 0,86 a 0,82)
Noreste de Groenlandia (77,5° N, −17,5°), norte de Groenlandia / Peary Land (82,5° N, −22,5°), isla de Baffin (67,5° N, −67,5°), este de Groenlandia (72,5° N, −22,5°), oeste de Groenlandia (72,5° N, −52,5°) y Ártico canadiense (72,5° N, −102,5°). Todas son **tierra sin hielo con permafrost probable según el mapa** (no capa de hielo), a más de 500 km de cualquiera de los 45 análogos. No son sitios nuevos para la ciencia: el Ártico canadiense (Devon, Axel Heiberg) es el entorno clásico y Groenlandia occidental ya se ha usado (Kangerlussuaq, Paatuut).

### Control de novedad (preregistrado, texto; método válido: el control positivo Devon Island salió «estudiado»)
- **Noreste de Groenlandia:** **estudiada como análogo de forma parcial**: las cuevas de Grottedal (Kronprins Christian Land) se presentan como entorno de desierto polar con rasgos comunes con Marte y banco de pruebas astrobiológico.
- **Peary Land:** **mencionada de pasada**: se estudia como desierto frío (microbiología de costras y permafrost), pero ninguna fuente la enmarca como análogo planetario.
- **Isla de Baffin:** **mencionada de pasada**: una fuente cita el Ártico alto alrededor de Baffin y Victoria como buenos análogos de Marte, sin estudios específicos de Baffin.
Un «sin evidencia» no prueba que no exista literatura (búsqueda web estándar de EE. UU., sin bases de pago).

### Lectura honesta
- **La mejora ahora es mayor y más limpia que con la regla de temperatura**, y las candidatas dejaron de ser capas de hielo. Pero **sigue siendo en parte por construcción**: con una clase binaria los análogos de permafrost real coinciden en hielo con los 9 objetivos, y solo 144 de 934 celdas tienen clase 1; el 0,683 mide sobre todo que **tener permafrost real basta para subir**.
- **El conjunto de «análogos fríos» está definido por temperatura, no por hielo**, así que incluye sitios fríos sin permafrost (Islandia, Yellowstone, Pavilion Lake) que, correctamente, bajan o no suben; eso arrastra la media y el límite inferior (0,512) es justo.
- **Las candidatas son regiones de permafrost real y conocido, no hallazgos:** sirven como lista de dónde buscar análogos de hielo somero, no como predicción de algo desconocido. El mapa solo cubre el hemisferio norte, así que **se pierden los Valles Secos y todo el sur**.
- **No se integra en el puntaje global** (el efecto global de la variable de permafrost fue negativo en [PREREGISTRO_HIELO_SOMERO.md](PREREGISTRO_HIELO_SOMERO.md)): solo cambia el caso de uso frío.
