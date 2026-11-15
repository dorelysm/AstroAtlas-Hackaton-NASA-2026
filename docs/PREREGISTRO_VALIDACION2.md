# Preregistro: segundo conjunto de análogos, independiente (15 nov 2026, escrito ANTES de buscar y de calcular nada)

**Por qué:** con 23 análogos casi todas las pruebas quedaron inconclusas, y varias ideas se probaron sobre los mismos 23 (riesgo de ajustar al test). Un segundo conjunto, buscado y congelado antes de medir, es la única forma de comprobar de forma independiente (a) si el modelo base funciona, (b) la unión «A o B» y (c) la variable de permafrost.
**Modelo A:** el congelado (commit `0b8a0a2`). **Primer conjunto (referencia):** los 23 de [PREREGISTRO_ANALOGOS.md](PREREGISTRO_ANALOGOS.md). No se cambia nada de ellos.

## Criterios de inclusión (los mismos que en el primer conjunto, más una regla de independencia)
1. Una fuente abierta **nombra el sitio como análogo terrestre de la Luna y/o de Marte** (agencia, artículo o resumen revisado, o instituto/universidad dedicado a análogos).
2. **Sitio localizable** con coordenada de incertidumbre razonable (≈ ≤ 10 km), con su origen anotado (**POR VERIFICAR** si viene de conocimiento general o Wikipedia).
3. **No se consulta ningún resultado del modelo** para decidir qué entra.
4. **Independencia:** un candidato a **menos de 100 km** de cualquiera de los 23 análogos del primer conjunto, o de otro candidato ya aceptado (entra el de fuente más fuerte), **se excluye**.
5. Etiquetas de aspecto solo si el texto de la fuente nombra el aspecto (mismas reglas que antes).

## Búsquedas (8, fijadas ahora; no se añaden consultas para buscar más sitios después de ver resultados)
(1) `Wudalianchi volcanic field Mars analog` · (2) `Iceland basaltic terrestrial analog Mars field site Holuhraun Kverkfjoll` · (3) `Mars analog dunes Namib Sahara Gobi field site aeolian` · (4) `Mars Desert Research Station Utah analog field site Hanksville` · (5) `Mars analog Oman Dhofar sabkha desert field site` · (6) `Mars analog Pilbara Western Australia field site` · (7) `Mars analog ice-rich permafrost field site Alaska Siberia Yukon Banks Island` · (8) `lunar analog Kamchatka Tolbachik Tenerife Teide volcanic field site Moon`.
Solo se hacen consultas de seguimiento para obtener coordenadas o la razón citada de sitios ya encontrados. La lista se congela (con hash) **antes** de calcular características o puntajes.

## Evaluación (fijada; el nuevo conjunto es el único que decide)
Mismas ventanas de 50 km y mismas dimensiones que el primer conjunto. Se calcula en cada cuerpo con ≥ 8 análogos nuevos aplicables.
- **V1, modelo base A:** u medio sobre los 14 objetivos de Marte (o los de la Luna), IC 95 % por bootstrap sobre los análogos nuevos. **Replica si el modelo funciona:** límite inferior > 0,5.
- **V2, unión «A o B»:** `s(c) = max(P_A(c), P_B(c))`. `P_A`: percentil del puntaje medio del modelo A sobre los objetivos (como en [PREREGISTRO_MODELOS.md](PREREGISTRO_MODELOS.md)). `P_B`: modelo de análogos Tierra-Tierra con **los 23 análogos del primer conjunto como únicas referencias** (los nuevos no se usan como referencia al evaluarse; se excluyen referencias a menos de 500 km del análogo evaluado). **Se adopta solo si:** límite inferior del u medio > 0,5 **y** diferencia pareada con `P_A` con límite inferior > 0 en al menos un cuerpo y ningún límite superior < 0.
- **V3, variable de permafrost** (clases y umbrales de [PREREGISTRO_HIELO_POLAR.md](PREREGISTRO_HIELO_POLAR.md), sin cambios): diferencia pareada del u medio de «todas» en Marte frente al base, límite inferior > 0 (primaria); y análogos fríos nuevos (regla de [PREREGISTRO_GRUPOS.md](PREREGISTRO_GRUPOS.md)) frente a objetivos fríos con pesos del modelo frío, u con límite inferior > 0,5 (secundaria, solo si hay ≥ 5 análogos fríos nuevos; si hay menos, se reporta sin veredicto). Se adopta solo si se cumplen las dos.
- **Conjunto combinado (exploratorio):** los 23 + los nuevos, solo como descripción; no decide nada.

## Qué no se hace
No se cambian modelos, umbrales, pesos, radios ni criterios después de ver resultados; cualquier variante se reporta aparte como exploratoria.

## Límites conocidos de antemano
Coordenadas por verificar; el conjunto final puede ser menor de 8 en la Luna (entonces la Luna se reporta sin veredicto); sesgo de selección de las 8 consultas; geología GLiM de 0,5° subestima campos pequeños de basalto; MODIS mensual 2019 para la térmica.

## Lista congelada (anexo, escrito después de las 8 búsquedas y ANTES de calcular ninguna característica ni ningún puntaje)
Hash del protocolo anterior a este anexo: `7645d89cbe9a9476`. `docs/analogos_set2.csv` sha256 `ec1a07d1da462b70` (9 sitios); `docs/aspectos_set2.csv` sha256 `9612fd97ab33f8d6` (3 etiquetas).
**Incluidos (9):** Wudalianchi, Namib/Sossusvlei, Bruneau Dunes, Maspalomas, Mars Desert Research Station, Strelley Pool (Pilbara), CRREL Permafrost Tunnel (Fairbanks), Tuktoyaktuk y Teide (Tenerife; único de la Luna). Distancia mínima a cualquiera de los 23 anteriores: 185 km; entre nuevos, el par más cercano (Maspalomas-Teide) está a 117 km.
**Excluidos y por qué:** Holuhraun (a ~20 km de Askja, que ya está) y Kverkfjöll (no aparece como análogo de Marte); Dhofar/AMADEE-18 (la fuente dice que la ubicación exacta se mantuvo en reserva, no cumple el criterio 2); Tengger y Sahara (la fuente no los presenta como análogos); Siberia nororiental (región, no un sitio) y Banks Island/Yukon (sin fuente); Kamchatka/Tolbachik (la fuente lo trata como análogo de Venus, no de la Luna); Dresser/North Pole (Pilbara) por estar a < 100 km de Strelley Pool; Pingo Canadian Landmark por estar a < 100 km de Tuktoyaktuk.
**Consecuencias conocidas de antemano:** solo hay **1 análogo nuevo de la Luna**, así que la Luna **no tiene veredicto** en este conjunto; Marte tiene 8 (justo el mínimo). Solo hay **2 análogos fríos nuevos**, por lo que la prueba secundaria de V3 se reporta **sin veredicto**. Coordenadas por verificar (Strelley Pool con incertidumbre quizá de 10-20 km).

## Resultados (hash del protocolo `7645d89cbe9a9476`; lista congelada con los hashes del anexo; sin cambios al protocolo tras ver los números)
Código: `src/analogos/validation2.py` (`python -m analogos.validation2 --build`, luego sin `--build`). Térmica y nieve de MODIS 2019 (descarga de unos 900 MB reducidos y borrados), geología GLiM (falta en 1 de los 9 sitios).

| Prueba | Cuerpo | Análogos | Resultado | ¿Cumple? |
|---|---|---|---|---|
| **V1 modelo base A** | **Marte** | 8 | **u = 0,698 (IC 0,563 a 0,821)** | **Sí** (límite inferior > 0,5) |
| V1 modelo base A | Luna | 1 (Teide) | u = 0,525 | Sin veredicto (1 análogo) |
| **V2 unión «A o B»** | Marte | 8 | u = 0,716 (0,616 a 0,833); diferencia con `P_A` **+0,006 (−0,079 a +0,118)** | **No** (el u cumple, pero la diferencia con A no tiene límite inferior > 0) |
| V2 unión | Luna | 1 | 0,304 | Sin veredicto |
| **V3 permafrost, primaria** | Marte «todas» | 8 | base 0,698 → 0,640; **diferencia −0,058 (−0,106 a −0,008)** | **No** (y el efecto es significativamente **negativo**) |
| V3 secundaria | Marte, fríos | 2 | Fairbanks 0,39 → 0,43; Tuktoyaktuk 0,71 → 0,61 | Sin veredicto (< 5 fríos) |

**Veredictos preregistrados:** el modelo base **se confirma en Marte con un conjunto independiente**; la **unión A o B no se adopta** (no mejora a A de forma demostrable: +0,006); la **variable de permafrost no se adopta** (empeora). La Luna no tiene veredicto (1 análogo nuevo).

### Por análogo (Marte; u del modelo A, u del modelo B con los 23 anteriores como referencia, u de la unión)
Bruneau 0,92 / 0,41 / 0,98 · Maspalomas 0,99 / 0,38 / 0,98 · MDRS 0,79 / 0,77 / 0,70 · Namib 0,77 / 0,56 / 0,68 · Strelley Pool 0,72 / 0,63 / 0,63 · Wudalianchi 0,65 / 0,60 / 0,54 · Tuktoyaktuk 0,46 / 0,67 / 0,57 · **Fairbanks (permafrost) 0,30 / 0,76 / 0,66**. Temperaturas medias anuales: Fairbanks 270,7 K y Tuktoyaktuk 263,7 K (los dos en la clase de permafrost); todos los demás ≥ 275 K.

### Lectura honesta
- **Lo bueno:** con 8 análogos que el modelo nunca vio y que no se usaron para ajustar nada, el u medio en Marte es 0,70 con límite inferior 0,56. Es la primera confirmación independiente de que el modelo base supera el azar en Marte. El primer conjunto dio 0,564 (no concluyente); la diferencia entre 0,56 y 0,70 está dentro del ruido que cabe esperar con 20 y 8 análogos, así que no se debe leer como que el modelo mejoró.
- **Lo que no hay que sobrevender:** 5 de los 8 son desiertos, dunas o campos volcánicos (justo lo que el modelo reconoce bien: Bruneau y Maspalomas dan 0,92 y 0,99 por ser dunas llanas, otra vez el efecto del terreno llano de [PREREGISTRO_LLANURA.md](PREREGISTRO_LLANURA.md)); los **dos análogos de hielo (Fairbanks, Tuktoyaktuk) son los más bajos del modelo A (0,30 y 0,46)**, así que la debilidad con lo frío se repite en datos nuevos. Las coordenadas están por verificar.
- **La unión A o B:** el resultado es el esperado por su construcción (B recupera los fríos: Fairbanks sube de 0,30 a 0,66) pero a cambio baja en otros (Namib de 0,77 con A a 0,68 con la unión, Wudalianchi de 0,65 a 0,54), y el efecto neto sobre A es cero. **No hay evidencia de que combinar mejore.**
- **Permafrost:** con dos análogos fríos que sí tienen clase de permafrost, la variable **no mejora** y el efecto global es negativo (−0,058): al sustituir la «nieve» por una clase binaria se pierde información en los 6 análogos cálidos (que pasan a clase «sin permafrost» idéntica a la de la mayoría de los objetivos). Con este resultado no hay motivo para volver a probarla con este diseño.

## Objetivos adicionales de hielo somero en Marte (SWIM): primer intento sin lista; luego resuelto con otra fuente (ver [PREREGISTRO_HIELO_SOMERO.md](PREREGISTRO_HIELO_SOMERO.md))
Se intentó conseguir una lista de sitios de hielo somero con coordenadas verificables (proyecto SWIM, USGS/PSI; escarpes de Dundas et al. 2018). Las fuentes abiertas encontradas dan el resumen (hielo somero poleward de ~40°, escarpes a 55-58° de latitud) pero **no una lista de sitios con coordenadas**; esas están en tablas suplementarias o en el PDS que no se pudieron obtener y comprobar. **No se inventaron coordenadas.** Alternativa descartada: definir los objetivos de hielo con el propio índice de neutrones (`H`), porque sería circular (la clase de «rico en hielo» ya sale de ese dato). Además, con el resultado de V3 (la variable de permafrost empeora en datos independientes) añadir objetivos pierde prioridad. Queda pendiente: obtener la tabla de Dundas et al. (2018) o de Morgan et al. (2021) y, solo si sale una lista verificable, preregistrar una versión con esos objetivos.
