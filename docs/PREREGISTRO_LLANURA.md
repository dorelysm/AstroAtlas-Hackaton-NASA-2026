# Preregistro: control por terreno llano en la prueba USGS (15 nov 2026, escrito ANTES de medir)

Pregunta: ¿la ventaja de los cráteres sobre los controles (Marte 0,567) sobrevive cuando se comparan cráteres y controles **igual de llanos**?

Método: se estratifica por `topo__slope_mean_deg` (pendiente media de la ventana de 50 km) en 5 cuantiles calculados sobre cráteres + dunas + controles juntos.
Dentro de cada estrato se calcula el AUC de rango (cráter/duna > control) con la u de la prueba actual (topografía sola, media sobre los objetivos del cuerpo).
AUC estratificado = media de los AUC de los estratos ponderada por n_pos × n_ctrl; se omiten estratos con menos de 3 positivos o 3 controles.
IC 95 % por bootstrap dentro de cada estrato (2000 réplicas, semilla 0).

**Criterio (el mismo de la prueba original):** hay señal si el límite inferior del IC > 0,5. Se reportan Luna y Marte.
No se cambian estratos ni variable de control después de ver los números.

## Resultado (hash del preregistro `fd6303ddeaf5ab57`)

| Cuerpo | AUC sin control (prueba original) | AUC estratificado por pendiente | IC 95 % | ¿Señal? |
|---|---|---|---|---|
| Luna | 0,531 | 0,476 | 0,418-0,534 | No |
| Marte | 0,567 | 0,494 | 0,436-0,552 | **No** |

**Veredicto:** al comparar cráteres y controles igual de llanos, la ventaja de Marte desaparece (0,567 → 0,494, el azar es 0,5). La señal de Marte se explica por que los cráteres están en terreno más llano que los controles, no por su forma de cráter. La topografía **no queda validada como aspecto** con esta capa. Esto confirma el sesgo que ya se había señalado en `docs/VALIDACION_ASPECTO.md`; el resultado anterior de Marte debe presentarse como confundido por la planitud.
Límite: la pendiente media es una sola variable de control; otras (relieve, rugosidad) podrían dejar algo de confusión residual, pero en sentido de reducir aún más la señal, no de crearla.
