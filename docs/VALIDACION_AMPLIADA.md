# Validación con el conjunto ampliado de análogos (15 nov 2026)

Protocolo y lista congelada **antes** de calcular nada: [PREREGISTRO_ANALOGOS.md](PREREGISTRO_ANALOGOS.md) (hash del protocolo registrado al congelar la lista; listas `analogos_ampliado.csv` `0f234908cd16ce94` y `aspectos_analogos_ampliado.csv` `3cc33c3ddf4c8a6f`). Modelo congelado (commit `0b8a0a2`): no se ajustó nada tras ver estos números.
Código: `src/analogos/validation_ext.py` (`python -m analogos.validation_ext --build` y luego sin `--build`). **23 análogos** = 10 originales + 13 nuevos (Luna: 12 con algún aspecto aplicable; Marte: 20).

## Resultado según el criterio fijado
Criterio: el límite inferior del IC 95 % del u medio («todas las dimensiones») debe ser > 0,5 en cada cuerpo con ≥ 8 análogos. u = P(análogo > celda típica), 0,5 = azar; bootstrap sobre los análogos.

| Cuerpo | Grupo | Análogos | u medio | IC 95 % | ¿Cumple? |
|---|---|---|---|---|---|
| **Luna** | todos | 12 | **0,595** | 0,545 a 0,644 | **Sí** (por poco) |
| Luna | originales / nuevos | 4 / 8 | 0,637 / 0,575 | 0,558 a 0,682 / 0,509 a 0,635 | (nuevos: sí; originales: n < 8) |
| **Marte** | todos | 20 | **0,564** | 0,448 a 0,678 | **No** (el límite inferior está por debajo de 0,5) |
| Marte | originales / nuevos | 8 / 12 | 0,493 / 0,612 | 0,301 a 0,674 / 0,468 a 0,737 | No / No |

**Lectura honesta:** en la Luna el modelo supera el azar por un margen pequeño; en Marte la media es algo mayor que 0,5 pero el intervalo incluye el azar, **así que no se puede afirmar que funcione**. Es la primera vez que algún cuerpo pasa el criterio, y conviene no sobrevenderlo: el margen es de unos 0,05, los análogos lunares que cuentan son 12 (varios cráteres de impacto que valen para Luna y Marte), y las coordenadas de los nuevos no están verificadas.

## Qué análogos recupera el modelo y cuáles no (Marte, u medio sobre los 14 objetivos)
- **Altos (≥ 0,65):** Lanzarote 0,96, Rochechouart 0,87, Vredefort 0,84, Pinacate 0,79, Ries 0,75, Lava Beds 0,75, Salar Grande 0,74, Danakil 0,73, Meteor Crater 0,69, Río Tinto 0,68, Atacama 0,65.
- **Cerca de cero:** Valles Secos 0,04, **Axel Heiberg 0,10**, Svalbard 0,18, Salar de Uyuni 0,25 (ver nota), Eureka 0,38.

**El patrón es claro:** el modelo reconoce los análogos **áridos, volcánicos o de impacto** y **falla con los fríos y de hielo** (Valles Secos, Axel Heiberg, Svalbard, Eureka). Es el problema ya conocido de la variable de hielo (nieve), ahora con una muestra más grande de sitios de permafrost que lo confirma. Nota: Uyuni sale con «nieve» media 1,00 porque el producto MODIS confunde la sal brillante con nieve, un fallo de la fuente.

## Por aspecto (fuente + nota; n_on = análogos con el aspecto)
| Cuerpo | Aspecto | n_on / n_off | Diferencia | IC 95 % | p (permutación) |
|---|---|---|---|---|---|
| Luna | Geología | 5 / 6 | **+0,41** | 0,06 a 0,69 | **0,05** |
| Marte | Geología | 2 / 11 | **+0,86** | 0,66 a 0,97 | 0,04 |
| Marte | Topografía | 8 / 6 | +0,12 | −0,05 a 0,30 | 0,11 |
| Luna | Topografía | 6 / 5 | +0,03 | −0,13 a 0,18 | 0,37 |
| Marte | **Hielo** | 3 / 11 | **−0,51** | −0,75 a −0,30 | 1,00 |
| Luna | Térmica | 1 / 10 | −0,51 | −0,59 a −0,42 | 1,00 |

- **Geología:** la única con señal en la dirección correcta, en los dos cuerpos. La de Marte descansa en solo **2 análogos** (Craters of the Moon y Pinacate), por debajo del mínimo de 3 del protocolo, así que **no cuenta como evidencia**. La lunar tiene 5 y p = 0,05 (límite).
- **Topografía:** diferencia pequeña a favor en Marte, sin significación. Hay que recordar que 5 de los 13 sitios nuevos son cráteres de impacto y que ya vimos que la señal topográfica se explica por terreno llano ([PREREGISTRO_LLANURA.md](PREREGISTRO_LLANURA.md)).
- **Hielo de Marte:** falla de forma consistente (−0,51 con 3 sitios; antes −0,75 con 1). Es el aspecto a corregir.

## Límites
- La lista no llegó a 30 sitios y tiene sesgo hacia cráteres de impacto (5 de 13).
- Las coordenadas de los 13 nuevos vienen de conocimiento general y están por verificar.
- Térmica de los sitios nuevos: medias mensuales MODIS de 2019, con las limitaciones ya descritas. Geología: GLiM de 0,5° da 0,14 para Pinacate (un campo pequeño) y 0 para el Etna, así que **subestima** el basalto en campos pequeños.
- No se aplicó ninguna corrección del terreno llano ni de marcas de población o vegetación: es la misma medida que la de los originales.
- Con 23 análogos los intervalos siguen siendo anchos; un segundo conjunto independiente daría más poder.

## Qué sugiere para mejorar el modelo
1. **El hielo/frío es lo que impide recuperar un tercio de los análogos de Marte.** Cualquier mejora debe atacar eso: una variable física comparable (inercia térmica o emisividad) y rellenar la térmica de Marte, que es la dimensión que distingue los análogos fríos de los cálidos.
2. Las mejoras se probarán contra **este mismo conjunto congelado**, sin tocarlo, y se reportarán aparte.
