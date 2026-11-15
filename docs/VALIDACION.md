# Validación del modelo

Estado a 14 de noviembre de 2026, con los datos reales disponibles ese día. **Los resultados son preliminares y casi todos están dentro del ruido**; no deben presentarse como una validación lograda.

## Qué se cambió
1. **PCA blanqueada de la topografía** (`similarity.fit_topo_model`). Las 16 variables `topo__*` están muy correlacionadas (|r| medio ≈ 0.74 en la Tierra). Con la media de z-scores, una sola propiedad (la rugosidad, por ejemplo) contaba hasta 15 veces. Ahora se resumen en las componentes principales que explican ≥ 90 % de la varianza (hoy 3 componentes, 93.6 %) y se mide la distancia ahí. La PCA se ajusta **solo con celdas de la Tierra**.
2. **Validación por tipo de análogo** (`validate.known_for_body`). La columna `analog_of` de `docs/analogos_conocidos.csv` dice si un análogo sirve para la Luna, Marte o ambos. Un objetivo de Marte ya no se puntúa contra Mauna Kea, ni uno lunar contra Atacama.
3. **Intervalos de confianza al 95 %** (`validate.evaluate(..., n_boot=500)`), remuestreando los análogos conocidos. Hay entre 4 y 8 por tipo, así que sin intervalo la media engaña.
4. **Validación sin la malla gruesa** (`validate.evaluate_sites`). Se puntúan los propios análogos conocidos con las ventanas de 50 km de `earth_sites.parquet` (las mismas que los objetivos) y se mira en qué percentil caen entre todas las celdas de la Tierra. Evita depender de una celda de 5° (~550 km) "cerca" del análogo.

Se pueden reproducir los resultados anteriores con `python -m analogos.pipeline --no-pca --all-analogs`.

## Resultados (29 objetivos: 15 lunares y 14 marcianos)
Media [mínimo–máximo] entre objetivos. 0.5 = azar.

| | AUC celdas | AUC sitios 50 km | Recall sitios @5 % |
|---|---|---|---|
| Antes (sin PCA, todos los análogos) | 0.45 [0.34–0.64] | 0.45 [0.18–0.88] | 0.07 |
| **Después** (PCA + por tipo) | 0.47 [0.36–0.89] | **0.57** [0.37–0.82] | 0.06 |
| Después, Luna | 0.51 | 0.63 | 0.08 |
| Después, Marte | 0.43 | 0.51 | 0.04 |

Nota: el AUC medio "antes" que cité el día anterior (0.52) venía de un `metrics.json` de una ejecución previa; recalculado hoy con los datos actuales da 0.45.

## Cómo leerlo
- **Mejora real pero pequeña.** El AUC con sitios sube de 0.45 a 0.57. Antes, algunos objetivos puntuaban *peor que el azar* (por ejemplo Apolo 11: 0.24) porque se les comparaba con análogos que no les corresponden.
- **Sigue casi todo en el ruido.** El rango entre objetivos es enorme y el recall @5 % es ≈ 0.06 (lo esperado por azar es 0.05). Marte no mejora (0.51).
- **Muy pocos análogos.** Hay 4 análogos lunares y 8 marcianos, y solo 2 de los 4 lunares caen en celdas de la malla. Los intervalos son amplios (por ejemplo Jezero: AUC de celdas 0.47, IC 95 % 0.35–0.78).
- **Un caso que sí se ve coherente:** Shackleton (AUC de celdas 0.89, IC 0.73–0.97) puntúa alto en Haughton y Askja, dos sitios fríos. Pero son solo 2 análogos cubiertos, así que es una pista, no una prueba.
- **Dry Valleys sale lejos para Marte** (percentil 87–92 con Jezero y Oxia). Probable causa: los sitios de aterrizaje son llanos *por diseño* (Jezero 2.9°, Oxia 0.8°) y Dry Valleys es relieve de montaña (~11°). La topografía mide idoneidad para aterrizar, y los análogos clásicos se eligen por clima, hielo y geología. **Conviene separar los dos propósitos** en lugar de mezclarlos en un solo puntaje.

## Qué limita hoy los resultados
- **Dimensiones vacías o débiles:** la geología de la Tierra está vacía, la térmica de Marte también, y la térmica de la Tierra es temperatura del **aire** (POWER) y no de la superficie. El `ice__water_frac` de la Tierra es un proxy de precipitación.
- **Pocos positivos** y coordenadas de los análogos que vienen de Wikipedia (ver `FUENTES.md`).
- **Escala:** las celdas de la Tierra son de 5°; no se ha comprobado cómo se muestrea la topografía en cada una.

## Siguientes pasos para que la validación valga
1. Rellenar las dimensiones vacías (MODIS LST, geología, térmica de Marte).
2. Separar el puntaje de **idoneidad de aterrizaje** (topografía) del de **análogo ambiental** (clima, hielo, geología) y validar cada uno con su lista.
3. Ampliar la lista de análogos conocidos con fuentes oficiales.
4. Considerar Mahalanobis regularizado para todas las dimensiones y un modelo PU para idoneidad (ver la discusión de modelos).
