# Ablación por dimensión (14 nov 2026)

Pregunta: ¿cuáles de las cuatro dimensiones (topografía, térmica, hielo, geología) ayudan a que el modelo recupere los análogos terrestres conocidos? Código: `src/analogos/ablation.py` (`python -m analogos.ablation`); resultados completos en `data/results/ablation_*.csv` (no se versiona).

## Método
- Para cada uno de los 29 objetivos (15 lunares, 14 marcianos) se puntúa la Tierra con: **todas** las dimensiones, **una sola** y **todas menos una**.
- Métrica `u` = probabilidad de que un análogo conocido puntúe más que una celda típica de la malla (0.5 = azar). Los análogos se puntúan con las mismas ventanas de 50 km que los objetivos.
- **Cuidado estadístico:** todos los objetivos de un cuerpo se evalúan contra **los mismos análogos** (4 en la Luna, 8 en Marte). La unidad independiente es el análogo, no el objetivo, así que los intervalos de confianza del 95 % se obtienen remuestreando los **análogos**. Con tan pocos, los intervalos son anchos.

## Resultados
**Marte** (14 objetivos, 8 análogos):

| Configuración | u medio | IC 95 % | Cambio frente a "todas" |
|---|---|---|---|
| todas | 0.50 | 0.32 – 0.69 | — |
| solo hielo | **0.62** | 0.38 – 0.86 | **+0.10** (0.02 a 0.18) |
| solo topografía | 0.45 | 0.34 – 0.56 | −0.06 (−0.22 a 0.10) |
| solo geología | **0.14** | 0.00 – 0.42 | −0.32 (−0.60 a 0.01) |
| sin topografía | 0.60 | 0.32 – 0.83 | +0.07 (−0.02 a 0.16) |
| sin hielo | 0.44 | 0.30 – 0.60 | −0.06 (−0.21 a 0.08) |
| sin geología | 0.51 | 0.36 – 0.65 | +0.01 (−0.04 a 0.04) |
| sin térmica | 0.50 | 0.32 – 0.69 | 0.00 (Marte no tiene térmica) |

**Luna** (15 objetivos, 4 análogos):

| Configuración | u medio | IC 95 % | Cambio frente a "todas" |
|---|---|---|---|
| todas | 0.60 | 0.52 – 0.68 | — |
| solo térmica | 0.64 | 0.42 – 0.86 | +0.04 (−0.26 a 0.31) |
| solo topografía | 0.58 | 0.42 – 0.71 | −0.02 (−0.10 a 0.07) |
| solo geología | 0.44 | 0.18 – 0.60 | −0.17 (−0.50 a 0.06) |
| solo hielo | 0.68 | — | solo 2 objetivos tienen hielo (Shackleton, Malapert); no concluyente |
| sin térmica | 0.57 | 0.48 – 0.62 | **−0.04** (−0.04 a −0.03) |
| sin topografía, sin hielo, sin geología | 0.60 – 0.62 | anchos | ≈ 0 |

## Qué dicen (y qué no)
1. **Con 4 y 8 análogos no se puede afirmar que ninguna combinación supere al azar de forma robusta.** El modelo completo da 0.50 en Marte y 0.60 en la Luna (esta última con intervalo apenas por encima de 0.5, y solo 4 análogos).
2. **Geología de Marte es contraproducente (u = 0.14).** El proxy de basalto saturaba en 1.0 en casi todos los sitios marcianos (mediana 1.00, mínimo 0.89), así que busca en la Tierra celdas basálticas. Seis de los siete análogos con dato tienen basalto 0 y puntúan 0.00. Solo Craters of the Moon, basáltico, sale alto (0.97). Esto **no** dice que Marte no sea basáltico (lo es), sino que esa variable no discrimina entre sitios marcianos y que los análogos de la lista no lo son por su geología.
3. **El hielo de Marte funciona como detector de "desierto sin nieve".** Los sitios marcianos tienen 3 a 7 % de agua, y la nieve media anual de la Tierra vale ~0 en desiertos. Por eso puntúan alto los desiertos (Death Valley 0.97, Atacama 0.93, Lanzarote 0.92, Río Tinto 0.91) y bajo los polares (Valles Secos 0.00, Svalbard 0.31, Haughton 0.39). Es una señal real pero **accidental**: no compara agua con agua. Y penaliza a los Valles Secos, el análogo marciano más clásico, porque MODIS les da nieve media 1.00.
4. **La térmica ayuda un poco en la Luna** (quitarla baja `u` en 0.04, de forma consistente), pero la Tierra no alcanza las temperaturas lunares: el efecto viene de ordenar celdas, no de igualarlas.
5. **La topografía no aporta señal clara** en ninguno de los dos cuerpos.

## Límites de esta prueba (importantes)
- **La lista de análogos no dice en qué aspecto es análogo cada sitio.** Atacama y Valles Secos lo son por clima seco y frío; Mauna Kea, Askja y Craters of the Moon por su basalto; Haughton por ser un cráter de impacto polar; Río Tinto por la química del agua. Exigirle a *cada* dimensión que recupere *todos* los análogos mezcla criterios distintos y empuja los resultados hacia el azar.
- Los análogos de la Luna son solo 4, y los objetivos de la Luna comparten el mismo perfil térmico (~390 K salvo los polares), lo que apenas aporta variación.
- Son varias comparaciones con pocos datos: las diferencias pequeñas (±0.05) no son fiables.

## Siguiente paso recomendado: validación por aspecto
Etiquetar cada análogo con la(s) dimensión(es) por la(s) que se considera análogo, **tomando las etiquetas de las fuentes ya citadas en `docs/analogos_conocidos.csv` y fijándolas antes de volver a medir** (si no, se está ajustando la etiqueta al resultado, y esta ablación ya se ha visto). Después se exigiría a cada dimensión solo lo que le corresponde: la geología debe recuperar los analogos basálticos; el hielo y la térmica, los desiertos fríos y secos; la topografía, los cráteres. También conviene ampliar la lista a más de 4 y 8 análogos.
