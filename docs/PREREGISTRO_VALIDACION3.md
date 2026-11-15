# Preregistro: tercer conjunto de análogos, tomado de un catálogo experto (15 nov 2026, escrito ANTES de calcular ninguna característica ni puntaje)

**Por qué:** los dos conjuntos anteriores los armé yo (el primero con 8 búsquedas fijadas, el segundo con otras 8). Un catálogo hecho por expertos y publicado hace años reduce el riesgo de que mi selección favorezca al modelo, y da más análogos para la Luna. **Fuente:** *The Catalogue of Planetary Analogues* (CAFE TN2, Preston, Grady y Barber, Open University, para la ESA, 5 dic 2012; [PDF](https://freight.cargo.site/m/D1821053255089660420449933921929/The-Catalogue-of-Planetary-Analogues.pdf)). **Modelo A:** el congelado (commit `0b8a0a2`); no se cambia nada. **Conjuntos previos:** los 23 de [PREREGISTRO_ANALOGOS.md](PREREGISTRO_ANALOGOS.md) y los 9 de [PREREGISTRO_VALIDACION2.md](PREREGISTRO_VALIDACION2.md).

## Regla de selección (mecánica; aplicada a las 30 entradas del catálogo)
1. **Unidad:** cada «sitio» del catálogo con **coordenada puntual dada en el propio catálogo** (a nivel de capítulo, o en una entrada «Site Specific Details» con coordenadas explícitas). Se excluyen las entradas regionales sin punto (Atacama «20-30° S», Namib, Kamchatka «51-61° N», Columbia River «Various», Australia Central) y las entradas sin coordenadas.
2. **Cuerpo (`analog_of`):** el de la tabla «Directory» del catálogo (qué rasgos de la Luna y de Marte cubre cada capítulo; la fila «Astrobiology» no cuenta). Luna: capítulos 1-4, 6-8, 10, 12-18, 22, 24-27; Marte: todos salvo 17 (y 29, 30 sí).
3. **Independencia:** se excluye cualquier sitio a **menos de 100 km** de cualquiera de los 32 análogos anteriores o de otro sitio ya aceptado de este conjunto (si hay empate gana el de menor número de capítulo). Por esta regla quedan fuera, entre otros: Etna, Tenerife, Utah/MDRS, Namib, Pilbara, Atacama/Yungay, Dry Valleys (y Blood Falls, Wright Valley, Beacon Valley), Ries, Sudbury, Rio Tinto, Meteor Crater, Cinder Lake, Black Point, Sunset Crater, Haughton y sus «supersites», Kilauea, Askja y Svalbard central.
4. **Sin etiquetas de aspecto** (el catálogo no las da por criterio medible): solo se evalúa la validación global.
5. **Lista congelada** (13 sitios; ningún par a menos de 100 km): `docs/analogos_set3.csv`, sha256 `2f3d816540d1cbf5`. **Luna: 7** (Lonar, Mistastin, Pampas de La Joya, Eyjafjallajökull, Krýsuvík, Bockfjord, Murchison Fjord). **Marte: 12** (todos salvo Mistastin). Distancia mínima a un análogo anterior: 153 km (Bockfjord-Svalbard). Los pares más cercanos entre nuevos están a 113 y 124 km.

## Evaluación (fijada)
Mismas ventanas de 50 km, dimensiones y métricas que [PREREGISTRO_VALIDACION2.md](PREREGISTRO_VALIDACION2.md).
- **V1, modelo base A:** u medio sobre los objetivos del cuerpo, IC 95 % por bootstrap sobre los análogos. **Marte:** los 12 nuevos; criterio: límite inferior > 0,5. **Luna:** los 7 nuevos **más el análogo lunar del segundo conjunto (Teide)**, 8 en total, todos posteriores al congelado del primer conjunto; criterio: límite inferior > 0,5. (Se reporta además la Luna con solo los 7 nuevos, sin veredicto por tener menos de 8.)
- **V2, unión «A o B»:** como en el segundo conjunto, con **los 32 análogos anteriores como únicas referencias** del modelo B. Criterio: límite inferior del u > 0,5 **y** diferencia pareada con `P_A` con límite inferior > 0 en al menos un cuerpo y ningún límite superior < 0. Marte con los 12 nuevos; Luna con los 7 (sin veredicto si < 8).
- **Descriptivo:** u por análogo; el conjunto total de 45 análogos; los sitios fríos (regla de [PREREGISTRO_GRUPOS.md](PREREGISTRO_GRUPOS.md)).

## Qué no se hace
No se cambian el modelo, los pesos, la lista ni los criterios después de ver los resultados; cualquier variante se reporta aparte como exploratoria.

## Límites conocidos de antemano
Coordenadas tomadas del catálogo sin verificar en fuente primaria (con errores tipográficos posibles, como un espacio en los segundos de Bockfjord); el catálogo es de 2012 y tiene sesgo hacia sitios con logística y publicaciones; la Luna depende de combinar dos conjuntos; las entradas de Svalbard e Islandia son varios sitios de una misma región (a 113-124 km entre sí), con correlación posible; GLiM de 0,5° y MODIS 2019 mensual como antes.

## Resultados (hash del protocolo `897392c2135d60fd`; lista `2f3d816540d1cbf5`; sin cambios al protocolo tras ver los números)
Código: `src/analogos/validation3.py` (`python -m analogos.validation3 --build`, luego sin `--build`).

| Prueba | Cuerpo | Análogos | Resultado | ¿Cumple? |
|---|---|---|---|---|
| **V1 modelo base A** | **Marte** (solo el conjunto nuevo) | 12 | **u = 0,577 (IC 0,423 a 0,726)** | **No** (límite inferior < 0,5) |
| **V1 modelo base A** | **Luna** (7 nuevos + Teide, preregistrado) | 8 | **u = 0,565 (IC 0,515 a 0,611)** | **Sí** (por poco) |
| V1 | Luna (solo los 7 nuevos) | 7 | 0,570 (0,510 a 0,622) | Sin veredicto (< 8) |
| V2 unión «A o B» | Marte | 12 | u = 0,581 (0,428 a 0,725); diferencia con `P_A` +0,011 (−0,071 a +0,105) | **No** |
| V2 unión «A o B» | Luna | 7 | u = 0,560 (0,413 a 0,710); diferencia con `P_A` **−0,123 (−0,157 a −0,086)** | Sin veredicto, y la unión **empeora** a A |

**Veredictos preregistrados:** **la unión A o B no se adopta** (otra vez: +0,011 en Marte y significativamente peor en la Luna). **El modelo base NO se confirma en Marte con este conjunto** (límite inferior 0,423) y **sí en la Luna por un margen pequeño** (límite inferior 0,515).

### Descriptivo (no preregistrado como prueba; mezcla conjuntos)
- **Marte, los tres conjuntos juntos (40 análogos):** u = **0,595 (IC 0,515 a 0,670)**; solo el segundo conjunto cumplía por separado (0,698), el primero (0,564) y el tercero (0,577) no. Los tres promedios están sobre 0,5 pero dos de los tres intervalos incluyen el azar.
- **Luna, los tres conjuntos juntos (20 análogos):** u = **0,583 (IC 0,545 a 0,619)**: supera el azar por poco, de forma consistente con el primer conjunto (0,595).
- **Por análogo (Marte):** altos Lonar 0,95, Krýsuvík 0,95, Turpan 0,85, Eyjafjallajökull 0,80, Ibn Battuta 0,65, Pampas de La Joya 0,63, Barberton 0,59; **bajos los fríos y lacustres**: Bockfjord 0,11, Pavilion Lake 0,30, Murchison Fjord 0,31, Yellowstone 0,35, Golden Deposit 0,46. Es el mismo patrón de siempre: reconoce lo árido, volcánico y de impacto y falla en lo frío, hidrotermal y lacustre.

### Lectura honesta
- **El resultado independiente más estricto (catálogo experto, 12 análogos) no pasa:** el modelo base queda sobre el azar en promedio (0,577) pero el intervalo lo incluye. Es la segunda vez que un conjunto de Marte no pasa (el primero lo hizo) y la primera que uno armado por otros tampoco; la confirmación del segundo conjunto (0,698) puede deberse en parte a que mis 8 consultas favorecían desiertos y dunas.
- **La estimación más razonable con todos los datos es modesta:** u ≈ 0,6 en Marte (0,515 a 0,670) y ≈ 0,58 en la Luna (0,545 a 0,619): el método discrimina algo mejor que el azar, no mucho.
- **Aviso:** en el conjunto de la ESA, varios sitios (Islandia, Svalbard) son del mismo entorno regional (113 a 124 km), así que no son independientes del todo.
- **Luna:** la unión empeora de forma consistente (−0,12): B (análogos Tierra con Tierra) casi no sirve para la Luna con 13 referencias.
