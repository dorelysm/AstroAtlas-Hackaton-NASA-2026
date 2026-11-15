# Estabilidad de las predicciones (15 nov 2026)

**Pregunta:** ¿las celdas candidatas dependen de decisiones arbitrarias del modelo? Código: `src/analogos/stability.py` (`python -m analogos.stability`).
**Método:** 150 réplicas por cuerpo. En cada una se perturban (1) los pesos por dimensión (Dirichlet uniforme), (2) la muestra de la Tierra con la que se estandariza y se ajusta la PCA de la topografía (bootstrap de celdas) y (3) la varianza que explica la PCA (80 a 95 %). Se calcula el puntaje medio de cada celda sobre todos los objetivos del cuerpo y se anota si queda en el 5 % mejor de las 384 celdas viables y sin vegetación. `freq_top5` es la fracción de réplicas en que ocurre.
No usa los análogos conocidos, y **no mide si la predicción es correcta**, solo si es robusta a decisiones sin respaldo en datos.

## Resultados
| Cuerpo | Celda | Lugar | `freq_top5` | Rango medio (0 = mejor) |
|---|---|---|---|---|
| Marte | 32.5° N, 37.5° E | Harrat ash-Shamah | **1,00** | 0,00 |
| Marte | 27.5° N, 17.5° E | Haruj | **0,79** | 0,04 |
| Marte | 17.5° N, 27.5° E | Sáhara oriental | 0,65 | 0,10 |
| Marte | 17.5° N, 32.5° E y 27.5° N, 22.5° E | Sáhara | 0,59 y 0,55 | 0,11 |
| Luna | −77.5° a −82.5° (varias celdas) | Antártida | 0,82 a 0,86 | 0,03 a 0,06 |
| Luna | 32.5° N, 37.5° E (Harrat) | | 0,23 | 0,11 |
| Luna | 27.5° N, 17.5° E (Haruj) | | 0,04 | 0,20 |

## Cómo leerlo
- **Las dos candidatas de Marte son robustas:** Harrat ash-Shamah queda entre el 5 % mejor en **todas** las réplicas y Haruj en el 79 %. No dependen de un peso ni de una PCA concreta. Es una razón para ordenarlas por encima de otras, aunque no demuestra que sean buenos análogos.
- **Robustez no es validez.** Las celdas antárticas de la Luna salen igual de robustas (0,82 a 0,86) y ya sabemos que son un artefacto: solo tienen dato de topografía y son planas. Una predicción puede ser estable y estar equivocada.
- **Para la Luna no hay candidatas terrestres sólidas:** las celdas de Harrat y Haruj aparecen poco (0,23 y 0,04), así que el resultado de Marte no se transfiere.
- **Qué no se perturbó:** las variables mismas, la ventana de 50 km, las fuentes de datos y los objetivos. Una estabilidad alta frente a lo que sí se perturbó no cubre esas decisiones.
