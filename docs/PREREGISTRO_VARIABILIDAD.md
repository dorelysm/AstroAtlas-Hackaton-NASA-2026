# Preregistro A: calibrar la distancia con la variabilidad del objetivo (15 nov 2026, escrito ANTES de leer ninguna ventana adicional ni calcular ningún puntaje con ella)

**Problema:** hoy un sitio de la Luna o de Marte es una sola ventana de 50 km y la distancia se escala con la dispersión de la Tierra. No se sabe qué tan «parecido» es suficiente: un sitio heterogéneo tolera más diferencia que uno muy uniforme.
**Conjunto de prueba y modelo base:** los mismos que en [PREREGISTRO_MULTIESCALA.md](PREREGISTRO_MULTIESCALA.md).

## Método (fijado)
- **Ventanas adicionales por objetivo:** malla 3 × 3 de ventanas de 50 km centradas en desplazamientos de −25, 0 y +25 km (norte-sur y este-oeste sobre la superficie del cuerpo; ventanas solapadas al 50 %), con los mismos DEM, la misma base de 500 m y las mismas 16 variables topográficas que la ventana central. Objetivos con |latitud| ≥ 85° (los polares): solo los 3 desplazamientos norte-sur. Se descartan las ventanas con menos de 50 % de píxeles válidos.
- **Variabilidad:** se proyectan las ventanas válidas en las componentes principales blanqueadas de la Tierra (las del modelo base) y se toma la **desviación típica muestral** `s_k` de cada componente entre las ventanas del objetivo. Un objetivo con menos de 5 ventanas válidas (menos de 3 los polares) **no se calibra** (`s_k = 0`).
- **Distancia calibrada (solo topografía):** la diferencia en cada componente se divide por `√(1 + s_k²)` (varianza de la medida de la Tierra, 1 tras blanquear, más la del objetivo). Se implementa con un modelo de PCA propio por objetivo cuya escala se multiplica por `√(1 + s_k²)`. Térmica, hielo y geología no cambian (solo tienen un valor por sitio).

## Evaluación (fijada)
Igual que en B: diferencia pareada de **«todas»** (primaria) con IC 95 % por bootstrap sobre los análogos, por cuerpo; secundarias: «solo topografía» y AUC estratificado por pendiente del USGS. **Criterio de éxito:** límite inferior > 0 en al menos un cuerpo y ningún límite superior < 0.

## Qué no se hace
No se cambian los desplazamientos, el mínimo de ventanas, la forma de combinar varianzas ni el conjunto de componentes después de ver los resultados; cualquier variante se reporta aparte.

## Límites conocidos de antemano
La variabilidad mide la **heterogeneidad del terreno alrededor del sitio a escala de 25 km**, no la elipse de aterrizaje ni la variabilidad de la celda terrestre (que no se modela). Con 9 ventanas solapadas la desviación típica es una estimación ruidosa. Solo calibra la topografía.

## Resultados (hash del preregistro `ddb02975a17bf101`; sin cambios al protocolo tras ver los números)
Ventanas leídas: Luna 177 (21 objetivos) y Marte 126 (14 objetivos), todas con dato; **los 35 objetivos quedaron calibrados**. Variabilidad media entre ventanas, en unidades de la componente blanqueada: Luna s₁ = 0,37, s₂ = 0,58, s₃ = 1,01; Marte s₁ = 0,22, s₂ = 0,54, s₃ = 0,60. Código: `src/analogos/variability.py` con el evaluador común `variants.py`; el modelo base reproduce los u de la validación ampliada y el AUC estratificado del USGS.

| Cuerpo | Configuración | u base | u variante | Diferencia pareada | IC 95 % |
|---|---|---|---|---|---|
| Luna | **todas** (primaria) | 0,595 | 0,579 | **−0,016** | −0,026 a −0,005 |
| Marte | **todas** (primaria) | 0,564 | 0,560 | **−0,005** | −0,008 a −0,001 |
| Luna | solo topografía | 0,602 | 0,602 | +0,001 | −0,015 a +0,015 |
| Marte | solo topografía | 0,520 | 0,520 | −0,001 | −0,008 a +0,006 |

USGS, AUC estratificado por pendiente: base Luna 0,476 y Marte 0,494; **variante** Luna 0,482 (0,425 a 0,538) y Marte 0,495 (0,436 a 0,552). Ninguno supera el azar.

**Veredicto: no se cumple el criterio. En los dos cuerpos el límite superior de «todas» es < 0 (empeora, aunque por muy poco). La calibración NO se adopta y el modelo no cambia.**
**Lectura:** con «solo topografía» la diferencia es prácticamente cero (±0,001): dividir la diferencia por `√(1 + s²)` con s entre 0,2 y 1,0 equivale casi a un reescalado uniforme de las distancias de cada objetivo, que **no cambia el orden de las celdas**. Lo que cambia es el **equilibrio entre dimensiones**: la topografía de un objetivo heterogéneo sube de puntaje frente a térmica, hielo y geología, y eso empeora un poco el global. La heterogeneidad a escala de 25 km, medida con 9 ventanas solapadas, no aporta información que ayude a ordenar mejor los análogos.
**Límites de la conclusión:** solo se midió heterogeneidad espacial alrededor del sitio, no la elipse de aterrizaje ni la variabilidad de la celda terrestre; y solo calibra la topografía.
