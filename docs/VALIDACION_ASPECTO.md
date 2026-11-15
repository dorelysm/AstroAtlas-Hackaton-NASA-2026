# Validación por aspecto (14 nov 2026)

Pregunta: ¿cada dimensión recupera los análogos conocidos **que lo son por ese aspecto**? Es la corrección que propuso la ablación global (`docs/ABLACION.md`), que exigía a cada dimensión recuperar todos los análogos aunque unos lo sean por su clima y otros por su basalto.

Código: `src/analogos/aspect.py` (`python -m analogos.aspect`). Etiquetas: `docs/aspectos_analogos.csv`. Resultados completos: `data/results/aspect_summary.*` (no se versiona).

> **Nota (14 nov 2026):** las tablas de este documento son de la primera versión (**15 sitios lunares**). La Luna pasó después a **21 sitios** (tablas de LROC) y todo se repitió: ver la sección "Repetición con 21 sitios lunares" más abajo. Las cifras de Marte no cambian.

## Cómo se hizo (y qué se fijó antes de medir)
- **Etiquetas fijadas antes de medir.** Salen solo de lo que dicen las fuentes ya citadas en `docs/analogos_conocidos.csv`. Huella del archivo: **sha256 `ca45726975642cb2…`** (14 nov 2026, 22:38), registrada en los resultados. El análisis principal también se declaró antes: el nivel "fuente + nota".
- **Tres niveles de evidencia por etiqueta:** *fuente* (la página citada nombra el aspecto: por ejemplo NASA dice que los Valles Secos son fríos y secos), *nota* (solo lo dice nuestra nota descriptiva) y *general* (conocimiento sin fuente abierta). Se evalúa con cada nivel acumulado para ver si el resultado depende de cuánto se confía en las etiquetas.
- **Prueba:** con la dimensión D **sola**, se compara cómo puntúan (u = probabilidad de superar a una celda típica; 0.5 = azar) los análogos etiquetados con D frente a los que tienen etiquetas pero no D. Los análogos sin etiquetas no entran en ningún grupo.
- **Estadística:** con 1 a 6 análogos por grupo se usa una **prueba de permutación exacta** (una cola) y un bootstrap sobre los análogos, sin supuestos de normalidad.

## Resultados (análisis principal: fuente + nota)
`gap` = u de los análogos del aspecto − u de los demás; positivo es lo esperado.

| Cuerpo | Dimensión | Con el aspecto | Sin él | u con | u sin | gap (IC 95 %) | p permutación |
|---|---|---|---|---|---|---|---|
| Marte | geología | Craters of the Moon | 4 análogos | 0.97 | 0.00 | **+0.97** | 0.20 |
| Marte | topografía | Lanzarote, Death Valley, Haughton | 3 | 0.52 | 0.38 | +0.14 (−0.12 a 0.39) | 0.25 |
| Marte | hielo | Valles Secos | 5 | 0.00 | 0.75 | **−0.75** (−0.94 a −0.53) | 1.00 |
| Marte | térmica | — | — | no evaluable: Marte no tiene térmica | | | |
| Luna | geología | Mauna Kea, Askja, Craters of the Moon | Haughton | 0.57 | 0.03 | **+0.53** (0.47 a 0.57) | 0.25 |
| Luna | topografía | Haughton | 3 | 0.65 | 0.56 | +0.08 (−0.10 a 0.30) | 0.50 |
| Luna | térmica | Haughton | 3 | 0.28 | 0.76 | **−0.48** (−0.59 a −0.30) | 1.00 |
| Luna | hielo | — | — | no evaluable: ningún análogo lunar lleva la etiqueta de hielo | | | |

**Sensibilidad al nivel de evidencia.** Solo con etiquetas de fuente: geología de Marte +0.97, topografía +0.06, hielo de Marte −0.84; la Luna no es evaluable (un solo análogo etiquetado por grupo). Añadiendo las de conocimiento general: geología +0.97 (Marte) y +0.53 (Luna), topografía +0.11 y +0.08, hielo de Marte pasa a −0.21 (Atacama 0.93 sube el grupo, los Valles Secos 0.00 lo bajan). **La dirección de cada resultado no cambia con el nivel.**

## Qué dicen

1. **Ninguna dimensión queda validada de forma estadísticamente concluyente, y no podía ocurrir.** Con 1 positivo o 1 negativo por grupo, el p mínimo alcanzable es de 0.20 a 0.50. Es un límite del número de análogos, no del modelo.
2. **La geología va en la dirección correcta en los dos cuerpos** (Luna +0.53, Marte +0.97): los análogos que lo son por su basalto puntúan alto y los que no, bajo. Es la señal más consistente, pero descansa en 1 a 3 análogos por grupo. En Marte solo cuenta Craters of the Moon, porque Lanzarote no tiene dato de geología (sin rejilla de 0.5° para una isla pequeña).
3. **El hielo de Marte falla justo donde debía acertar (−0.75).** Los Valles Secos son el ejemplo clásico de lugar frío y seco, pero MODIS les da nieve media 1.00 (hielo y glaciares), mientras que los sitios marcianos tienen 3 a 7 % de agua. La "nieve" de la Tierra no mide sequedad. Es el fallo más claro y confirma la advertencia de semántica de `docs/FUENTES.md`: esa variable no representa lo que el aspecto pide.
4. **La térmica de la Luna sale en contra (−0.48), pero con una sola referencia.** Solo Haughton lleva la etiqueta (cráter polar frío, por nota), y se compara con 15 objetivos lunares casi todos ecuatoriales (~390 K). Un análogo polar frío no puede parecerse térmicamente a un sitio ecuatorial: **la analogía solo tendría sentido para los dos objetivos polares** (Shackleton y Malapert). Esta prueba promedia sobre todos los objetivos, y eso mezcla casos donde el aspecto no aplica.
5. **La topografía muestra una diferencia pequeña a favor** (+0.14 y +0.08) con intervalos que incluyen el cero: sin información.

## Límites de esta prueba
- **Poquísimos análogos por grupo** (1 a 3 positivos). Los intervalos de bootstrap con 1 elemento son degenerados (p. ej. el de la geología de Marte colapsa en 0.97) y no deben leerse como certeza.
- **Los objetivos no se filtran por relevancia.** Para cada aspecto se promedian todos los objetivos del cuerpo, aunque el aspecto solo aplique a algunos (térmica: solo los polares). Filtrarlos después de ver los resultados sería ajustar la prueba a los datos; hacerlo bien exige decidir el criterio de relevancia de antemano.
- **Las etiquetas "nota" y "general" son débiles.** Mauna Kea, Askja y Svalbard tienen la razón de analogía sin verificar; Río Tinto no tiene ningún aspecto medible (química y habitabilidad) y solo sirve como negativo.
- **No se probó más de un análisis principal**, pero sí se mira cada dimensión por separado (4 dimensiones × 2 cuerpos): un resultado aislado de p = 0.2 no debe tomarse como hallazgo.

## Bases de datos de sitios análogos que existen (búsqueda del 14 nov 2026)
**No hay una base de datos de la NASA con un catálogo de sitios análogos.** Lo más cercano:

| Recurso | Quién | Contenido | Acceso | Estado |
|---|---|---|---|---|
| **Known Terrestrial Analog Sites for Planetary Science** (Hunter 2020, DOI 10.5066/P9J72921) | USGS Astrogeology | **192 puntos** (shapefile `TerrestrialAnalogs.shp`). Campos: `Name`, `AnalogType` (solo 3 valores: *Impact Crater*, *Dunes*, *Volcanic Eruption*), `Lat`, `Lon` (latitud de -34.7 a 75.7: **no incluye la Antártida**) y `AnalogBody` (cuerpo extraterrestre para el que se usó el sitio). Limitado a sitios **verificados con investigación financiada por la NASA** (financiado por el acuerdo USGS-NASA del Terrestrial Analogs Data Portal). Dominio público. | los **metadatos** se leyeron (archivo `AnalogSites_metadata.xml`, aportado por el equipo); la página del DOI en ScienceBase | **Metadatos verificados. Advertencias del propio productor:** "para identificar áreas de investigación, no para análisis"; los puntos aproximan áreas grandes y pueden estar **hasta 10 km** del centroide; estado "en trabajo"; no incluye todos los análogos posibles. **La capa de puntos todavía no está descargada** |
| **Planetary Aeolian Analog Database (PAAD)** (Gullikson, Titus y Hunter 2023, DOI 10.5066/P9IFVZEX) | USGS | 45 campos de dunas; atributos: tipo de forma, clase climática, origen y composición de la arena, latitud, longitud, elevación, extensión; CC0 | página del DOI; se integrará al Terrestrial Analogs Data Portal (tadp.astrogeology.usgs.gov) | Verificado en la página del USGS; datos sin descargar |
| **Catalogue of Planetary Analogues (CAFE / CPA)** | ESA (proyecto CAFE, Open University) | sitios de los siete continentes organizados por rasgo lunar y marciano | PDF; **403 a mi acceso automático** | Existe según los resultados de búsqueda; contenido sin verificar |
| **Astrobiology Habitable Environments Database (AHED)** | NASA Ames | repositorio de datos y muestras astrobiológicas | portal web | Es de muestras, no un catálogo de sitios |
| **Astrobiology research locations** | NASA | descripciones de lugares de campo (p. ej. Atacama) | página en migración | Sin verificar |
| IMEWG Mars Analog Database | grupo internacional | base interactiva de sitios análogos de Marte | en desarrollo | estado no confirmado |
| PTAL (ptal.eu) | consorcio europeo | 102 muestras de roca análogas, centradas en Mawrth Vallis y Oxia Planum | base de datos web | Es de muestras, no de sitios |

**Para nuestro problema:** la capa del USGS aporta sitios con una categoría de proceso dada por una autoridad, no por nosotros. Sus tres categorías solo cubren los aspectos de **topografía** (cráteres, dunas) y **geología** (volcanes). **No hay ninguna categoría de frío ni de sequedad: la térmica y el hielo quedan sin análogos con esta fuente.** Hay que bajarla desde un navegador, porque mi acceso automático está bloqueado.

**Regla de categoría a aspecto, fijada antes de ver ningún punto** (`docs/aspectos_usgs.csv`, sha256 `af372c56698d6704…`, 14 nov 2026, 22:50, antes de descargar los puntos): *Impact Crater* y *Dunes* cuentan como aspecto **topografía** y *Volcanic Eruption* como **geología**, todos con nivel de evidencia "fuente". Cada sitio solo se evalúa con los objetivos del cuerpo que indique `AnalogBody`. Advertencia que ya se conoce: "erupción volcánica" no implica basalto, y la variable de geología mide fracción de basalto; un sitio volcánico félsico puede salir mal por eso y no por fallo de la dimensión.

## Protocolo con la capa del USGS (fijado el 14 nov 2026, antes de calcular ningún score)
Lo que se vio antes de fijarlo: solo la **estructura** de los datos, no ningún resultado. De los 192 puntos, 190 son cráteres de impacto, 1 es un campo de dunas (Grand Falls, Marte) y 1 una erupción volcánica; `AnalogBody` está vacío en 191 de 192; hay 5 cráteres duplicados (mismo nombre, 15 a 30 km de diferencia). El registro volcánico se llama "Ritland" (como un cráter noruego) pero sus coordenadas (64.93° N, 16.52° O) caen en Islandia, cerca de Askja: **error de etiquetado del productor**. Los cráteres vienen de la Earth Impact Database, es decir, son *los cráteres confirmados de la Tierra*, no una selección hecha por similitud con la Luna o Marte.

**Datos:** cráteres únicos (duplicados con el mismo nombre a menos de 50 km se fusionan), más Grand Falls, como análogos del aspecto **topografía** (regla de `docs/aspectos_usgs.csv`, sha256 `af372c56698d6704…`). El único registro volcánico no permite evaluar la geología (n = 1): solo se informa.
**Cuerpo:** como `AnalogBody` está vacío, los cráteres se evalúan contra los objetivos de la Luna y de Marte, cada uno por separado.
**Variable:** u = probabilidad de que el sitio puntúe más que una celda de la malla de la Tierra, usando solo la dimensión de topografía (con la PCA), promediado sobre los objetivos del cuerpo.

**El control (para separar "cráter" de "terreno llano y estable").** 200 puntos aleatorios de tierra firme, con latitud entre -35° y 76° (el rango de los cráteres) uniforme en el seno de la latitud, longitud uniforme, semilla 20261114. Se descartan los puntos a menos de 50 km de un cráter, los que no tienen DEM válido o son mar plano, y los de hielo, agua o sin dato en GLiM. Se evalúan con el mismo cálculo.
**Prueba principal:** `AUC_rank` = P(u de un cráter > u de un punto de control), una cola (Mann-Whitney), con intervalo de confianza del 95 % por bootstrap sobre ambos grupos, por cuerpo. **Se considera que hay señal solo si el límite inferior del intervalo supera 0.5.**
**Límites ya conocidos:** los cráteres se conservan en cratones y desiertos, que son terreno estable, así que el control no elimina del todo ese sesgo; la mayoría son más pequeños que la ventana de 50 km; los puntos pueden estar hasta 10 km desplazados; el único contraste que se puede hacer es con topografía.

## Resultado con la capa del USGS (14 nov 2026)
Se ejecutó el protocolo anterior sin cambiarlo. Código: `src/analogos/aspect_usgs.py`; datos: `data/features/earth_usgs.parquet` (no se versiona).

**Muestra.** 185 cráteres únicos + Grand Falls (dunas) y 200 puntos de control (un cráter sin DEM). Con score quedaron **180 positivos y 186 controles**: 6 cráteres y 14 controles se perdieron por el defecto descrito abajo.

| Cuerpo | u cráteres y dunas | u control | Cráteres con u > 0.5 | Control con u > 0.5 | AUC de rango (IC 95 %) | p (Mann-Whitney, 1 cola) | ¿Señal? |
|---|---|---|---|---|---|---|---|
| Luna | 0.530 | 0.530 | 58 % | 63 % | 0.491 (0.432 a 0.552) | 0.62 | **No** |
| Marte | 0.597 | 0.548 | 78 % | 68 % | 0.557 (0.499 a 0.618) | 0.029 | **No** (el límite inferior, 0.499, no supera 0.5) |

Solo cráteres, sin las dunas: Luna 0.488 (0.430 a 0.548), Marte 0.555 (0.497 a 0.614). Los dos registros restantes, informativos (n = 1): Grand Falls puntúa u = 0.71 contra la Luna y 0.79 contra Marte; el volcán (mal etiquetado "Ritland", en Islandia) 0.72 y 0.77.

**Veredicto según el criterio fijado antes: la topografía no queda validada como aspecto con esta capa.**
- En la **Luna** no hay ninguna diferencia entre cráteres y puntos aleatorios (AUC 0.49).
- En **Marte** hay una diferencia pequeña (AUC 0.56) que roza el umbral: el p-valor (0.029) es nominalmente bajo, pero se hicieron dos comparaciones (Luna y Marte), con lo que el umbral corregido sería 0.025, y el intervalo no excluye el 0.5 por una milésima. **No se debe presentar como evidencia a favor.**
- **El sesgo de terreno llano es real en los propios datos:** los cráteres son más llanos que el control (pendiente media 1.33° frente a 2.53°; relieve local mediano 152 m frente a 250 m). Como los sitios de Marte también son llanos (pendiente mediana 0.7°), un cráter puede puntuar algo mejor **solo por estar en un cratón estable**. La ligera ventaja en Marte es compatible con eso y no con una semejanza de forma de cráter.

**Defecto encontrado: las celdas más planas no reciben score de topografía.** Las variables `topo__aspect_concentration` y `topo__aspect_equatorward` valen NaN cuando la pendiente media es menor de 0.1° (sin laderas no hay orientación), y la PCA no admite NaN. Consecuencias medidas:
- **91 de las 955 celdas de la malla de la Tierra no puntúan** en topografía: 54 en la Antártida (53 con nieve media anual mayor de 0.5), y el resto son **lagos** (Michigan, Caspio, que Copernicus aplana a relieve cero a cualquier altitud, así que el filtro de océano no los atrapa) y llanuras reales (el Sudd).
- Salen de los rankings **justo los sitios más parecidos topográficamente a Marte** (pendientes de 0.3° a 0.7°).
- En este test se perdieron el 3 % de los cráteres y el 7 % de los controles (los más llanos de cada grupo).
- **No se ha corregido.** Dar a esas variables el valor 0 en terreno llano es lo neutro, pero además hay que filtrar los lagos (relieve menor de 1 m a cualquier altitud) o aparecerían como candidatos. Es un cambio al modelo que afecta a todos los resultados anteriores y requiere decisión.

**Límites:** los cráteres son la lista de los confirmados de la Tierra (Earth Impact Database), no una selección por parecido con la Luna o Marte; la mayoría son más pequeños que la ventana de 50 km; los puntos pueden estar desplazados hasta 10 km; no se probó la sensibilidad al defecto de arriba porque habría que filtrar los lagos antes y eso es parte del arreglo.

## Segunda ejecución, tras corregir el terreno llano (14 nov 2026)
**Qué cambió en el modelo** (decidido después de ver la primera ejecución): las variables de orientación valen 0, no NaN, en terreno llano (pendiente media < 0.1°); y el filtro de agua descarta relieve < 1 m a cualquier altitud (lagos incluidos). Resultado: las 91 celdas más llanas de la Tierra pasan a puntuar, salen 4 de agua (951 celdas) y ya no se pierde ningún cráter ni control (**185 positivos y 200 controles, antes 180 y 186**). Los controles se volvieron a seleccionar con la misma semilla y reglas. Luna y Marte no cambian (pendientes mínimas 0.59° y 0.28°).

**Topografía con la capa del USGS (misma prueba y mismo criterio fijado de antemano):**

| Cuerpo | Ejecución | u cráteres y dunas | u control | AUC de rango (IC 95 %) | p (1 cola) | ¿Señal? |
|---|---|---|---|---|---|---|
| Luna | primera (antes de corregir) | 0.530 | 0.530 | 0.491 (0.432 a 0.552) | 0.62 | No |
| Luna | **segunda (corregida)** | 0.548 | 0.538 | **0.522 (0.465 a 0.578)** | 0.23 | **No** |
| Marte | primera (antes de corregir) | 0.597 | 0.548 | 0.557 (0.499 a 0.618) | 0.029 | No (límite 0.499) |
| Marte | **segunda (corregida)** | 0.598 | 0.547 | **0.567 (0.507 a 0.620)** | **0.012** | **Sí** (límite 0.507) |

**Cómo leerlo, con cautela:**
- **En Marte se cumple ahora el criterio fijado de antemano** (límite inferior > 0.5, y p = 0.012 está por debajo del umbral de 0.025 que corrige las dos comparaciones). La señal es pequeña: un cráter puntúa más que un punto aleatorio el 57 % de las veces (el azar es 50 %), y el límite inferior supera 0.5 por solo 0.007. En la **Luna sigue sin haber señal**.
- **El veredicto de Marte cambió por una corrección hecha después de ver un resultado límite** (0.499). La corrección es de principio (era un defecto de diseño que descartaba justo los sitios más llanos, y no se eligió por su efecto: antes de medir no se sabía en qué dirección iba), y devuelve la muestra completa. Pero por eso la **primera ejecución es la que cumple el protocolo en sentido estricto, y la segunda debe presentarse como una repetición tras corregir un defecto, no como una confirmación independiente.**
- **El sesgo de terreno llano sigue sin eliminarse:** los cráteres son más llanos que el control, y los sitios de Marte también. La ventaja de 0.567 puede deberse a ese parecido de terreno y no a la forma de cráter. Esta prueba no puede separarlos.
- El intervalo de confianza ya incorpora la variación del grupo de control (se remuestrean ambos grupos), así que no hace falta probar otras semillas, pero es un solo conjunto de 200 controles.

**Efecto de la corrección en el resto de resultados** (cambios pequeños, dentro del ruido; las conclusiones no cambian):
- Pipeline (29 objetivos): AUC con celdas 0.479 → 0.505; AUC con sitios exactos 0.556 → 0.539; recall con sitios 0.147 → 0.147.
- Ablación: Marte "todas" 0.50 → 0.49 y Luna 0.60 → 0.58; "solo hielo" de Marte 0.62 (+0.11), "solo geología" de Marte 0.14, "solo térmica" de la Luna 0.64: igual que antes.
- Validación por aspecto (nivel principal): topografía de Marte +0.14 → +0.15 y de la Luna +0.08 → +0.12 (siguen sin ser concluyentes); geología (+0.97 Marte, +0.53 Luna), hielo de Marte (−0.75) y térmica de la Luna (−0.48): idénticos.

## Repetición con 21 sitios lunares (14 nov 2026)
Se repitió todo tras actualizar la Luna con LROC (21 sitios, antes 15). **Marte no cambia.** Las etiquetas de aspecto y el protocolo del USGS no se tocaron.

**Validación por aspecto (nivel fuente + nota), Luna:**

| Dimensión | Con el aspecto | Antes (15 sitios) | **Ahora (21 sitios)** | p permutación |
|---|---|---|---|---|
| Geología | Mauna Kea, Askja, Craters of the Moon (frente a Haughton) | +0.53 (0.47 a 0.57) | **+0.64 (0.56 a 0.69)** | 0.25 (el mínimo posible con 1 negativo) |
| Topografía | Haughton | +0.12 | +0.14 (−0.08 a 0.39) | 0.50 |
| Térmica | Haughton | −0.48 | −0.48 (−0.58 a −0.29) | 1.00 |
| Hielo | — | no evaluable | no evaluable | |

La dirección de cada resultado se mantiene. La geología sigue en la dirección correcta y ahora es algo mayor, pero **sigue sin poder ser concluyente** (el p mínimo alcanzable es 0.25). La térmica sigue en contra por el mismo motivo ya explicado (un análogo polar frío contra objetivos casi todos ecuatoriales).

**Topografía con la capa del USGS (misma prueba y criterio):**

| Cuerpo | Antes (15 sitios) | **Ahora (21 sitios)** | ¿Señal? |
|---|---|---|---|
| Luna | 0.522 (0.465 a 0.578), p 0.23 | **0.531 (0.473 a 0.586), p 0.144** | **No** |
| Marte | 0.567 (0.507 a 0.620), p 0.012 | 0.567 (0.507 a 0.620), p 0.012 | Sí (sin cambios; es la repetición tras corregir un defecto, no una confirmación independiente) |

**Pipeline (35 objetivos: 21 lunares y 14 marcianos):** AUC con sitios exactos 0.539 → **0.579** (rango 0.27 a 0.89); recall con sitios 0.147 → **0.171**; AUC con celdas 0.505 → 0.498. Siguen cerca del azar, con una mejora pequeña que viene de los objetivos nuevos y no de un cambio de método.

## Qué haría falta para poder concluir
1. **Más análogos por aspecto, con la razón citada** (al menos 5 por aspecto): campos basálticos, desiertos fríos y secos, cráteres de impacto, zonas polares. Cada uno con su fuente de la NASA o la ESA abierta y su etiqueta fijada antes de medir.
2. **Cambiar la variable de hielo de la Tierra** por una que mida sequedad o agua del suelo (precipitación o humedad del suelo, como GLDAS, que exige aceptar su licencia) en lugar de la cobertura de nieve.
3. **Definir de antemano qué objetivos son relevantes** para cada aspecto (térmica: sitios polares; geología: sitios con basalto).
