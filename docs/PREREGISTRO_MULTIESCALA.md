# Preregistro B: topografía a varias escalas (15 nov 2026, escrito ANTES de calcular ningún puntaje con ella)

**Problema:** la dimensión de topografía usa 16 variables muy correlacionadas (la PCA las resume en ~3 componentes) y, tras controlar por terreno llano, no muestra señal ([PREREGISTRO_LLANURA.md](PREREGISTRO_LLANURA.md)). Una descripción de **cómo cambia la rugosidad con la escala** es una propiedad más estable entre cuerpos que las magnitudes absolutas.
**Conjunto de prueba:** los 23 análogos congelados ([PREREGISTRO_ANALOGOS.md](PREREGISTRO_ANALOGOS.md)) y la capa del USGS con 185 cráteres y dunas frente a 200 controles. **Modelo base:** el congelado (commit `0b8a0a2`).

## Variante B (fijada)
Se sustituyen las 16 variables por **tres derivadas de las que ya existen** (sin datos nuevos):
1. `H` = pendiente de la regresión por mínimos cuadrados de ln(rugosidad_L) frente a ln(L), con L = 1, 2 y 5 km (`topo__rough_{1,2,5}km_m`; la rugosidad se acota por debajo en 0,01 m). Es un exponente de Hurst aparente.
2. `ln(rugosidad_1km)`.
3. `ln(pendiente media en grados + 0,1)`.
Después, PCA blanqueada ajustada con las celdas de la Tierra (varianza explicada 0,90, máximo 3 componentes), igual que la topografía base. El resto de dimensiones no cambia.

## Evaluación (fijada)
- **Primaria:** diferencia pareada por análogo del u medio de **«todas»** entre B y el modelo base, con IC 95 % por bootstrap sobre los análogos, por separado para la Luna y Marte.
- **Secundarias (se reportan, no deciden):** lo mismo con «solo topografía», y el **AUC estratificado por pendiente** de la prueba del USGS (5 estratos, mismo método que [PREREGISTRO_LLANURA.md](PREREGISTRO_LLANURA.md)) para el modelo base y para B.
- **Criterio de éxito:** el límite inferior de la diferencia pareada de «todas» es **> 0 en al menos un cuerpo** y el límite superior **no es < 0 en ninguno**. Si no se cumple, no se adopta.
- Si además el AUC estratificado de B tiene límite inferior > 0,5, se anota como la primera señal topográfica real tras el control de planitud.

## Qué no se hace
No se prueban otras escalas, otras combinaciones de variables ni otros umbrales de la PCA después de ver los resultados; cualquier variante se reporta aparte como exploratoria.

## Límites conocidos de antemano
Solo hay tres escalas (1, 2 y 5 km) sobre una base de 500 m, así que `H` es un exponente aparente y ruidoso; con ventanas de 50 km la rugosidad a 5 km se estima con pocas muestras.

## Resultados (hash del preregistro `82ddf50863e9d8c8`; sin cambios al protocolo tras ver los números)
Código: `src/analogos/multiscale.py` (`python -m analogos.multiscale`) con el evaluador común `variants.py`. Con el modelo base se reproducen los u de la validación ampliada (Luna 0,595; Marte 0,564) y el AUC estratificado del USGS (0,476 y 0,494), lo que comprueba que la comparación es limpia.

| Cuerpo | Configuración | u base | u variante | Diferencia pareada | IC 95 % |
|---|---|---|---|---|---|
| Luna | **todas** (primaria) | 0,595 | 0,592 | −0,003 | −0,043 a +0,036 |
| Marte | **todas** (primaria) | 0,564 | 0,566 | +0,002 | −0,054 a +0,055 |
| Luna | solo topografía | 0,602 | 0,613 | +0,012 | −0,048 a +0,074 |
| Marte | solo topografía | 0,520 | 0,517 | −0,003 | −0,091 a +0,085 |

USGS, AUC estratificado por pendiente (cráteres y dunas frente a controles): base Luna 0,476 (0,418 a 0,534) y Marte 0,494 (0,436 a 0,552); **variante** Luna 0,500 (0,443 a 0,560) y Marte 0,494 (0,435 a 0,554). Ninguno supera el azar.

**Veredicto: no se cumple el criterio (ningún límite inferior de «todas» es > 0). La variante NO se adopta y el modelo no cambia.** Las diferencias son del orden de ±0,01 con intervalos de ±0,05: **no hay diferencia detectable**, ni a favor ni en contra. La PCA de la variante reduce las tres variables a 2 componentes que explican toda la varianza, así que las tres variables escalares llevan la misma información que las 16 en lo que respecta a este test.
**Lectura:** describir la rugosidad por su exponente de escala no aporta nada medible con tres escalas (1, 2 y 5 km) sobre una base de 500 m. No es evidencia de que el enfoque no sirva con más escalas o con DEM de mayor resolución, solo de que este diseño no mejora nada.
