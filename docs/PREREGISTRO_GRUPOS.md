# Preregistro: dos grupos de análogos, frío y cálido (15 nov 2026, escrito ANTES de calcular nada con grupos)

## Cómo surge la idea (y un aviso de honestidad)
La validación ampliada ([VALIDACION_AMPLIADA.md](VALIDACION_AMPLIADA.md)) y el experimento de inercia ([PREREGISTRO_INERCIA.md](PREREGISTRO_INERCIA.md)) mostraron que el modelo recupera los análogos **cálidos y áridos** y falla con los **fríos y de hielo**. **Esa división se vio mirando los resultados, no se planteó antes**, así que es una hipótesis generada con los datos de prueba. Para limitar el sesgo: (1) la regla de grupo usa solo una variable climática de la Tierra, no los puntajes; (2) todo se fija aquí antes de calcular; (3) el modelo frío reutiliza pesos ya definidos antes de este análisis (`usecases.py`); (4) el resultado se declara de entrada **probablemente no concluyente** por el tamaño del grupo frío (5 análogos). Sí se vio la distribución de `thermal__t_max_k` de los 23 análogos al fijar el umbral, pero no ningún u.

**Conjunto de prueba:** los 23 análogos congelados ([PREREGISTRO_ANALOGOS.md](PREREGISTRO_ANALOGOS.md)). **Modelo base:** el congelado (commit `0b8a0a2`).

## Grupos (fijados)
- **Análogos de Marte (`analog_of` contiene «mars»):** *fríos* si `thermal__t_max_k` (máximo mensual de la temperatura diurna de superficie, MODIS) **< 295 K** (≈ 22 °C); *cálidos* si no. Resultan **5 fríos** (Valles Secos, Haughton, Svalbard, Axel Heiberg, Eureka) y 15 cálidos.
- **Objetivos de Marte:** *fríos* si |latitud| ≥ 45° (Arcadia Planitia, Viking 2, Phoenix); *cálidos* los otros 11.
- **Luna:** no se evalúa (solo 2 objetivos polares y 1 análogo frío).

## Modelos (fijados; sin ajuste)
- **Modelo cálido:** el base («todas», cuatro dimensiones con pesos iguales).
- **Modelo frío:** pesos `{hielo: 1, topografía: 0,5, térmica: 0, geología: 0}` (los del caso de uso «hielo y permafrost en el norte de Marte» de `usecases.py`, definidos antes). La térmica no entra porque Marte no la tiene.

## Evaluación (fijada)
Mismas medidas que la validación ampliada (u por análogo con ventanas de 50 km, bootstrap sobre los análogos), solo Marte.
- **E1, primaria:** análogos **fríos** frente a objetivos **fríos**: diferencia pareada por análogo del u medio entre el **modelo frío** y el **base («todas»)** sobre esos mismos objetivos (n = 5), con IC 95 % por bootstrap y una prueba exacta de cambio de signo (una cola).
  **Criterio de éxito:** límite inferior del IC de la diferencia **> 0** y u del modelo frío con límite inferior **> 0,5**.
- **E2, descriptiva (no decide):** «sistema por grupos»: cada análogo se evalúa con el modelo de su grupo sobre los objetivos de su grupo (cálidos con el base sobre los 11 cálidos; fríos con el modelo frío sobre los 3 fríos). Se reporta el u del sistema sobre los 20 análogos con su IC y la diferencia pareada frente al base sobre los 14 objetivos (0,564), **avisando de que los objetivos usados no son los mismos**.

## Qué se haría si se cumple
Presentar la salida del sistema en dos clases («análogos de clima frío» y «análogos cálidos y áridos») en el atlas y la app, con el modelo frío para el primer grupo. **Si no se cumple, no se adopta** y se documenta el resultado.

## Qué no se hace
No se cambian el umbral de 295 K, el de 45°, los pesos del modelo frío ni los grupos después de ver los resultados; cualquier variante se reporta aparte como exploratoria.

## Límites conocidos de antemano
Solo 5 análogos fríos (un intervalo de bootstrap con 5 elementos es muy ancho: es lo esperado); el grupo frío incluye análogos de hielo, permafrost y polares que no son equivalentes entre sí; la temperatura de superficie de MODIS son medias mensuales; solo 3 objetivos de Marte son fríos, y 2 de ellos (Arcadia, Phoenix) son los únicos con hielo somero conocido; y la «nieve» terrestre sigue sin medir lo mismo que el hielo de Marte, así que el modelo frío hereda ese defecto.

## Resultados (hash del preregistro `97f2baf653687789`; sin cambios al protocolo tras ver los números)
Código: `src/analogos/grupos.py` (`python -m analogos.grupos`). Objetivos fríos: Arcadia Planitia, Phoenix y Viking 2. Análogos fríos: Valles Secos, Haughton, Svalbard, Axel Heiberg y Eureka.

**E1, análogos fríos frente a objetivos fríos (n = 5):**

| Análogo | Modelo base | Modelo frío | Diferencia |
|---|---|---|---|
| Axel Heiberg | 0,102 | 0,140 | +0,038 |
| Valles Secos | 0,052 | 0,059 | +0,007 |
| Eureka | 0,472 | 0,495 | +0,023 |
| Haughton | 0,581 | 0,599 | +0,018 |
| Svalbard | 0,227 | 0,256 | +0,029 |

- Diferencia pareada media **+0,023 (IC 95 % +0,014 a +0,032; p exacta de una cola 0,031)**: el modelo frío mejora a los **cinco**, pero por poco.
- **u del modelo frío = 0,310 (IC 0,131 a 0,489)**: sigue **por debajo del azar** (0,5). Con el modelo base, 0,287.
- **Criterio (IC inferior de la diferencia > 0 y u frío con IC inferior > 0,5): NO se cumple** (se cumple la primera parte, no la segunda). **Los grupos NO se adoptan como modelo** y la salida del proyecto no cambia.

**E2, descriptiva:** el «sistema por grupos» da u = 0,614 (IC 0,495 a 0,727) frente a 0,564 del base sobre los 14 objetivos (diferencia pareada +0,050, IC +0,025 a +0,074). **No hay que leerlo como una mejora real:** los análogos cálidos se evalúan solo sobre los 11 objetivos cálidos y dejan fuera los 3 fríos, donde puntúan peor; la diferencia sale en buena parte de cambiar los objetivos, tal como se avisó de antemano.

## Qué enseña
- **Separar los grupos corrige un problema de promedio, no el problema de fondo.** Aun comparando los análogos fríos solo con objetivos polares y usando pesos pensados para ellos, **cuatro de cinco siguen por debajo del azar o cerca**; solo Haughton (0,60) y Eureka (0,50) están en torno a 0,5 o por encima.
- **CORRECCIÓN (15 nov, posterior): lo que sigue sobre la variable de hielo era erróneo.** Se escribió que Phoenix y Arcadia tienen un contenido de agua moderado según Odyssey y que las magnitudes no eran comparables; en realidad **Phoenix y Arcadia no tienen dato de hielo (NaN)**: el mapa de Odyssey usado no cubre más allá de ≈ 57° de latitud. El modelo frío solo disponía de la topografía de esos objetivos y del hielo de Viking 2, así que este experimento **no podía** acertar con los análogos fríos y su resultado no dice nada sobre la variable de nieve. Ver [PREREGISTRO_MODELOS.md](PREREGISTRO_MODELOS.md) (Fase 0).
- **Conclusión práctica:** para los análogos fríos y de hielo **no hay una mejora de modelo disponible con los datos actuales**; lo honesto es decirlo y presentar esa parte como la limitación principal del método.
