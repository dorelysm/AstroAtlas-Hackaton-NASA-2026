# Preregistro: permafrost sin capas de hielo, para el caso de uso frío (15 nov 2026, escrito ANTES de calcular nada con esta regla)

**Motivo:** [PREREGISTRO_HIELO_SOMERO.md](PREREGISTRO_HIELO_SOMERO.md) adoptó la variable de permafrost solo para el caso frío, pero las seis mejores celdas salieron en la Antártida interior y Groenlandia: **capas de hielo, no permafrost**. La clase «permafrost probable» (temperatura media anual < 271 K) no las distingue. Aquí se fija una regla para excluirlas, se comprueba que la prueba preregistrada sigue cumpliéndose y se ve qué candidatas frías quedan.

## Regla (fijada ahora; no se prueban otros umbrales)
- **Nieve perenne / capa de hielo:** nieve media anual de MODIS (MOD10CM 2019, `ice__water_frac` de la Tierra, fracción del año con nieve) **≥ 0,9**. Es un criterio físico simple (nieve casi todo el año = hielo glaciar, no suelo helado); el umbral 0,9 es **arbitrario y se fija aquí**.
- **Clase «permafrost sin capas de hielo» (PF2):** 1 si temperatura media anual < 271 K **y** nieve media anual < 0,9; 0 en caso contrario. Se aplica **igual** a las celdas de la Tierra y a los sitios análogos, sin excepciones. Las clases de Marte no cambian (los 8 objetivos de hielo publicado + Phoenix = 1; los demás, la clase ya calculada).

## Evaluación (fijada)
Mismo diseño que [PREREGISTRO_HIELO_SOMERO.md](PREREGISTRO_HIELO_SOMERO.md): 7 análogos fríos (más los que cumplan la regla de [PREREGISTRO_GRUPOS.md](PREREGISTRO_GRUPOS.md)) frente a los 9 objetivos de hielo, pesos del modelo frío (hielo 1, topografía 0,5), variante base idéntica.
- **Q1:** u medio con PF2, límite inferior del IC 95 % (bootstrap sobre análogos) **> 0,5**.
- **Q2:** diferencia pareada PF2 − base, límite inferior **> 0**.
- **Q3 (credibilidad de las candidatas):** las 6 mejores regiones (≥ 500 km entre sí, `viable` y no vegetadas, a más de 500 km de cualquier análogo conocido de los dos conjuntos, puntaje = media sobre los 9 objetivos de hielo) deben tener **nieve < 0,9 y temperatura media anual < 271 K** (se comprueba, no se impone al elegir) y **ninguna puede caer en una capa de hielo conocida** (Antártida al sur de 60° S o interior de Groenlandia al norte de 66° N con nieve ≥ 0,9).
- **Se integra al caso de uso frío solo si se cumplen Q1, Q2 y Q3.** Si Q1 o Q2 fallan, la variable de permafrost **no se usa para ninguna candidata** y el caso frío queda documentado como sin candidatas creíbles. Si solo falla Q3, se reporta y no se integra.
- **Control de novedad de las candidatas** (texto, no decide): para cada una de las 3 primeras, dos búsquedas fijadas: `<región> Mars analog permafrost ice` y `<región> planetary analogue cold desert`; control positivo `Devon Island Mars analog permafrost`. Clasificación como en [PREREGISTRO_NOVEDAD.md](PREREGISTRO_NOVEDAD.md).
- **Descriptivo:** cuántas celdas pasan de clase 1 a 0 por la regla, y el valor de nieve de cada análogo frío (si alguno queda excluido por la regla, se reporta).

## Qué no se hace
No se cambian el umbral de nieve, el de temperatura, los objetivos, los análogos ni los criterios después de ver los resultados; cualquier variante se reporta aparte como exploratoria.

## Límites conocidos de antemano
MODIS 2019 es un solo año; la nieve media anual ≥ 0,9 también incluye mesetas muy altas con nieve casi permanente; la temperatura y la nieve no miden permafrost (no hay mapa de permafrost en el proyecto); las candidatas son hipótesis, no medidas.

## Resultados (hash del protocolo `f5e36b4e33503e3c`; sin cambios al protocolo tras ver los números)
Código: `src/analogos/frio.py` (`python -m analogos.frio`).
**Descriptivo:** la regla pasa de 470 a **190 celdas** con clase 1 (280 pasan a 0 por nieve perenne). Entre los 7 análogos fríos, **los Valles Secos de la Antártida quedan en clase 0** (nieve media anual 1,00, el producto MODIS los ve cubiertos): la regla los trata como capa de hielo, lo que es un fallo del producto de nieve en un valle seco; los otros 6 quedan en clase 1 (Axel Heiberg 0,79, Svalbard 0,78, Haughton 0,63, Eureka 0,61, Tuktoyaktuk 0,60, Fairbanks 0,48).

| Criterio | Resultado | ¿Cumple? |
|---|---|---|
| **Q1** u medio con PF2, límite inferior > 0,5 | **0,778 (IC 0,558 a 0,908)** | **Sí** |
| **Q2** diferencia pareada PF2 − base, límite inferior > 0 | **+0,378 (IC +0,229 a +0,500)** | **Sí** |
| **Q3** las 6 candidatas son permafrost y ninguna cae en una capa de hielo | **Una cae en la Antártida** (−82,5°, 167,5° E, nieve sin dato) | **No** |

Por análogo (base → PF2): Axel Heiberg 0,23 → 0,83; Fairbanks 0,41 → 0,86; **Valles Secos 0,15 → 0,14 (no mejora: quedó en clase 0)**; Eureka 0,52 → 0,91; Haughton 0,57 → 0,92; Svalbard 0,32 → 0,85; Tuktoyaktuk 0,61 → 0,94.
Candidatas preregistradas (6): cinco en Groenlandia o el Ártico (77,5° N −17,5° E; 82,5° N −22,5°; 67,5° N −67,5°; 72,5° N −22,5°; 72,5° N −102,5°) y una en la Antártida (−82,5° 167,5° E). **Tres de ellas están en Groenlandia** (77,5° N −17,5°; 82,5° N −22,5°; 72,5° N −22,5°): aunque el protocolo las dejaba pasar (la nieve media de su celda de 500 km es < 0,9 porque mezclan costa libre de hielo y capa), son en gran parte capa de hielo.

**Veredicto preregistrado: Q1 y Q2 se cumplen pero Q3 no; NO SE INTEGRA al caso frío.** La variable de permafrost **no se usa para ninguna candidata** y el caso frío queda documentado como **sin candidatas creíbles**.

### Lectura honesta
- **La prueba de los análogos sale mejor que antes** (u 0,778 y +0,378), pero ese resultado sigue siendo en parte por construcción (clase binaria que los análogos comparten con los objetivos) y ahora descansa en 6 análogos (los Valles Secos no cuentan).
- **El fallo es de las candidatas, no de la regla en sí:** la nieve media de una celda de 500 km no basta para separar capa de hielo de permafrost cuando la celda mezcla costa y glaciar, y la Antártida con nieve sin dato se coló. Habría hecho falta una máscara de capas de hielo (p. ej. un mapa de glaciares o cobertura del suelo), que el proyecto no tiene.
- **Exploratorio (posterior a ver Q3, no preregistrado, no decide nada):** si se excluyen a mano toda la Antártida y Groenlandia, las seis mejores celdas son: **Isla de Baffin (67,5° N, −67,5°), el Ártico canadiense (72,5° N, −102,5° y 77,5° N, −117,5°), el norte del Tíbet/Kunlun (37,5° N, 87,5° E), el Pamir (37,5° N, 72,5° E) y la costa de Columbia Británica (57,5° N, −132,5°)** (puntajes 0,83 a 0,69). Son **hipótesis a revisar**: el Ártico canadiense es el entorno clásico de análogos de Marte (Devon, Axel Heiberg están cerca pero a menos de 500 km se descartaron), y no se hizo el control de novedad ni se comprobó que las celdas del Tíbet y de Columbia Británica no sean glaciares.
- **Siguiente paso real:** una máscara de capas de hielo (glaciares o cobertura del suelo) y un mapa de permafrost, no más ajustes de umbral.
