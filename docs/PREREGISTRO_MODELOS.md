# Preregistro: modelo de análogos Tierra-Tierra, consenso entre modelos y variable de permafrost (15 nov 2026, escrito ANTES de calcular nada de esto)

**Conjunto de prueba:** los 23 análogos congelados ([PREREGISTRO_ANALOGOS.md](PREREGISTRO_ANALOGOS.md)). **Modelo A (el actual, congelado):** commit `0b8a0a2`.

## Fase 0: un hallazgo que cambia el planteamiento (diagnóstico, sin protocolo)
Al preparar la variable de permafrost se comprobó que **los objetivos polares de Marte no tienen dato de hielo**: el mapa de hidrógeno de Odyssey que usamos (`h2o_sr_5x5.tab`) no tiene valores entre ≈ 57° y 90° de latitud en ningún hemisferio y tiene huecos entre 42° y 57° N. **Phoenix (68,2° N) y Arcadia Planitia (47,25° N) salen con `ice__water_frac = NaN`**; Viking 2 (47,7° N) sí tiene valor (0,046). Consecuencias:
- Para los dos únicos objetivos con hielo somero conocido, el modelo compara **solo topografía** (la dimensión de hielo se ignora).
- Los otros 12 objetivos con dato de hielo tienen entre 0,03 y 0,07 de agua: todos **secos**. **No hay ningún objetivo de nuestro conjunto que represente lo que imitan los análogos fríos (permafrost, hielo somero).**
- Por eso el fallo con los análogos fríos y los resultados del experimento de grupos **no se pueden atribuir a la variable de hielo terrestre** (nieve): el test no tenía dónde acertar. Esto corrige lo que se escribió antes (ver `PREREGISTRO_GRUPOS.md` y `RESUMEN.md`).
**Variable de permafrost (E3):** **no se puede probar de forma honesta** mientras Marte no tenga dato de hielo en los polos; con los 12 objetivos secos solo mediría «ausencia de permafrost», lo mismo que hoy mide la nieve. Se deja anotada como paso siguiente (hace falta un producto de hidrógeno polar de Marte, p. ej. de los mapas de neutrones del espectrómetro de Odyssey) y **no se ejecuta**.

## E1: modelo de análogos (Tierra con Tierra)
Puntúa cada celda de la Tierra por su parecido con **los análogos conocidos del cuerpo**, todo medido con variables terrestres (no usa la Luna ni Marte). Elimina la comparabilidad entre cuerpos y no depende del dato de hielo de los objetivos.
- **Referencias:** los análogos con `analog_of` que contiene el cuerpo (Luna 12, Marte 20), con sus características terrestres (topografía en PCA blanqueada, térmica, nieve, geología GLiM), exactamente las mismas del modelo A, con pesos iguales.
- **Parecido** de una celda `c` con un análogo `a`: la misma puntuación global del modelo (media de `exp(−RMS z)` por dimensión, ignorando las ausentes) usando como perfil las características de `a`. **Puntaje de la celda = máximo sobre las referencias** (vecino más parecido).
- **Evaluación (dejar fuera uno):** para cada análogo `a` se quitan de las referencias `a` y **todos los análogos a menos de 500 km** de `a` (para que los vecinos no se filtren); `u(a)` = fracción de celdas de la malla con puntaje menor que el de `a`, con la misma regla de referencias. Media por cuerpo con IC 95 % por bootstrap sobre los análogos.
- **Criterio de éxito:** límite inferior del IC del u medio **> 0,5** en cada cuerpo (el mismo criterio de la validación ampliada). Se reporta además la diferencia pareada frente al estadístico equivalente del modelo A (ver abajo) y los grupos frío/cálido.

## E2: consenso entre los dos modelos
- **Modelo A, estadístico comparable:** `A(c)` = media, sobre los objetivos del cuerpo, del puntaje global de la celda con el modelo base. `P_A` = percentil de `A` entre las celdas (0-1). Para un análogo, `P_A` se calcula con su `A` frente a las celdas.
- **Modelo B:** el de E1, con su `P_B` (en la evaluación, con la regla de dejar fuera uno).
- **Consenso:** `s(c) = min(P_A(c), P_B(c))` (la celda es buena solo si lo es en los dos).
- **Evaluación:** `u` de cada análogo con `s` (misma regla de E1); media con IC. **Criterio de éxito:** límite inferior del IC del u medio **> 0,5** y diferencia pareada con `P_A` con límite inferior **> 0 en al menos un cuerpo** y ningún límite superior < 0.
- **Salida:** las celdas de mayor consenso (viables, sin vegetación y a más de 500 km de cualquier análogo conocido), con el modelo B usando **todos** los análogos como referencia (solo para proponer candidatas, no para evaluar).

## Qué no se hace
No se cambia la forma de agregar (máximo), el radio de exclusión (500 km), la forma de combinar (mínimo) ni las dimensiones después de ver los resultados; cualquier variante se reporta aparte.

## Límites conocidos de antemano
Con 12 y 20 referencias el modelo B solo reencuentra lo que los análogos tienen en común y no usa la información del sitio objetivo; el conjunto de prueba es el mismo que sirve de referencia (se mitiga con la regla de dejar fuera uno y la exclusión espacial, pero no equivale a un conjunto independiente); los análogos de la Luna son pocos (12) y 8 de ellos son de «Luna y Marte»; y el modelo B hereda los defectos de los datos terrestres (nieve, térmica mensual, GLiM).

## Resultados (hash del preregistro `947e23b621db661f`; sin cambios al protocolo tras ver los números)
Código: `src/analogos/modelos.py` (`python -m analogos.modelos`). `P_A` es el estadístico del modelo A comparable con B (percentil del puntaje medio sobre los objetivos); por eso difiere del u de la validación ampliada (Luna 0,595, Marte 0,564), que promedia el u de cada objetivo.

| Cuerpo | Modelo | u medio | IC 95 % | ¿Cumple (límite inferior > 0,5)? |
|---|---|---|---|---|
| Marte (20) | A (`P_A`) | 0,551 | 0,427 a 0,672 | No (ya se sabía) |
| Marte (20) | **E1: B, análogos Tierra-Tierra** | **0,499** | 0,371 a 0,631 | **No** |
| Marte (20) | **E2: consenso (mínimo)** | **0,452** | 0,334 a 0,578 | **No** |
| Luna (12) | A (`P_A`) | 0,699 | 0,545 a 0,839 | Sí |
| Luna (12) | **E1: B** | **0,465** | 0,326 a 0,621 | **No** |
| Luna (12) | **E2: consenso** | **0,509** | 0,389 a 0,643 | **No** |

Diferencia pareada frente a A: E1 Marte −0,052 (−0,230 a +0,125) y Luna −0,234 (−0,457 a −0,016); **E2 Marte −0,099 (−0,202 a −0,010) y Luna −0,190 (−0,390 a −0,003)**: el consenso por mínimo **empeora** en los dos cuerpos.
**Veredicto: no se cumple ningún criterio. Ni el modelo B ni el consenso se adoptan. E3 no se ejecutó** (ver la Fase 0). El modelo del proyecto no cambia.

## Lo que sí mostró (resultado secundario preregistrado: grupos frío y cálido)
| Marte | n | Modelo A (`P_A`) | Modelo B |
|---|---|---|---|
| Análogos **fríos** (Valles Secos, Haughton, Svalbard, Axel Heiberg, Eureka) | 5 | **0,191** (0,071 a 0,316) | **0,743** (0,541 a 0,851) |
| Análogos **cálidos** | 15 | **0,671** (0,571 a 0,767) | **0,418** (0,282 a 0,563) |

- **Los dos modelos son complementarios:** A reconoce los cálidos y B reconoce los fríos. El modelo B, que no usa ningún dato de Marte, **sí recupera los análogos fríos** (cuatro de cinco con u ≥ 0,83; los Valles Secos con 0,34), lo que confirma que el fallo del modelo A con ellos viene de **comparar con objetivos que no representan ese tipo de lugar** (Fase 0) y no de que los análogos fríos sean inalcanzables.
- Por qué B funciona con los fríos: son lugares parecidos entre sí (todos polares y de permafrost) y, al compararse Tierra con Tierra, desaparecen la comparabilidad entre cuerpos y la falta de dato de hielo de los objetivos.
- Por qué no funciona en conjunto: con cálidos y áridos B queda por debajo del azar (0,418), porque esos análogos son muy distintos entre sí (arenales, volcanes, cráteres, salares) y un análogo no se parece mucho a los demás.
- **Exploratorio (NO preregistrado, no decide nada):** la unión («buena en A o en B», `máximo` de los percentiles) da en Marte u = 0,601 (IC 0,503 a 0,700), diferencia con A +0,050 (−0,056 a +0,169), y en la Luna 0,675 (0,510 a 0,829), −0,024 (−0,090 a +0,063). Sugiere que combinar por «cualquiera de los dos» recupera los dos grupos, pero **no es significativo y se eligió después de ver los resultados**; haría falta preregistrarlo y evaluarlo con un conjunto independiente.

## Qué cambia en nuestras conclusiones (correcciones)
- Se había escrito que el problema con los análogos fríos era que la «nieve» terrestre no mide lo mismo que el hielo de Marte. **Eso no se puede afirmar:** los dos objetivos polares no tenían dato de hielo y los otros 12 son secos. La conclusión correcta es que **el conjunto de objetivos no incluye ningún sitio de hielo somero con dato**, así que la validación de los análogos fríos con el modelo A no es informativa.
- Se corrigieron `PREREGISTRO_GRUPOS.md`, `INFORME.md`, `RESUMEN.md` (y su PDF), `VALIDACION_AMPLIADA.md` y `FUENTES.md`.

## Siguiente paso que sí tiene sentido
1. **(Hecho el 15 nov: ver [PREREGISTRO_HIELO_POLAR.md](PREREGISTRO_HIELO_POLAR.md); la variable de permafrost no se adopta, resultado no concluyente.)** **Conseguir dato de hielo para los polos de Marte** (p. ej. los mapas de neutrones epitérmicos del espectrómetro de Odyssey, del propio PDS) para Phoenix y Arcadia; solo entonces se puede probar una variable de permafrost terrestre (E3) frente a objetivos con hielo.
2. **(Hecho el 15 nov: ver [PREREGISTRO_VALIDACION2.md](PREREGISTRO_VALIDACION2.md) y [PREREGISTRO_VALIDACION3.md](PREREGISTRO_VALIDACION3.md); la unión A o B no se adopta, +0,006 frente a A con IC −0,079 a +0,118 en 8 análogos independientes de Marte.)** Preregistrar la unión A o B y evaluarla con un conjunto de análogos independiente.
