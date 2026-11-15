# Preregistro: dato de hielo polar de Marte y variable de permafrost (15 nov 2026, escrito ANTES de descargar o calcular nada con estos datos)

**Motivo:** [PREREGISTRO_MODELOS.md](PREREGISTRO_MODELOS.md) (Fase 0) mostró que Phoenix y Arcadia Planitia no tienen dato de hielo (el mapa de hidrógeno de Odyssey que usamos no cubre más allá de ≈ 57° de latitud), así que ningún objetivo con hielo somero conocido podía probar la variable de hielo. Aquí se intenta conseguir ese dato y, si es válido, probar por fin una variable de permafrost terrestre.
**Conjunto de prueba:** los 23 análogos congelados ([PREREGISTRO_ANALOGOS.md](PREREGISTRO_ANALOGOS.md)). **Modelo base:** el congelado (commit `0b8a0a2`).

## Fase 1: un índice de hidrógeno relativo para todos los objetivos de Marte
**Datos:** NASA PDS, Mars Odyssey GRS, *Averaged Neutron Data* v2.0 (`ODY-M-GRS-5-AND-V2.0`, DOI 10.17189/1522868): tablas binarias de 5° × 5° (2 592 celdas, cobertura de polo a polo) con la tasa de conteo de neutrones **epitérmicos** (`CEPI`) por intervalo de 15° de longitud solar (Ls) y año de Odyssey (≈ 290 archivos de ≈ 114 kB, unos 33 MB). Menos neutrones epitérmicos = más hidrógeno (agua) en el primer metro del suelo. **No se convierte a agua equivalente** (no hay una calibración publicada en un producto cuadriculado del PDS que pueda usar con rigor).
**Regla de estación (la escarcha estacional de CO₂ también apantalla neutrones):** para |latitud| ≥ 40° se usan solo los intervalos de Ls **completamente dentro** de [105°, 165°] (hemisferio norte, verano) o [285°, 345°] (sur); para |latitud| < 40°, todos los intervalos. Se ignoran celdas con `CEPI` ≤ 0 o sin dato.
**Valor por celda:** mediana de `CEPI` sobre los intervalos y años seleccionados.
**Índice:** `H = −ln(CEPI / CEPI_ref)`, con `CEPI_ref` la mediana de las celdas con |latitud| < 30°. Más positivo = más hidrógeno que el ecuador. Cada objetivo toma el valor de la celda de 5° que lo contiene.
**Puerta de validez (si falla, se detiene y no hay Fase 2):** correlación de Spearman entre `H` y el hidrógeno ya medido (`h2o_sr_5x5`) en las celdas con |latitud| < 42° donde ambos existen: **ρ ≥ 0,6**.

## Fase 2: variable de «hielo en el suelo» comparable entre cuerpos
- **Marte:** clase binaria *rico en hielo* si `H` ≥ ln(1,5) (la tasa epitérmica es al menos un tercio menor que la del ecuador). El umbral es **arbitrario y se fija aquí**; no se prueban otros.
- **Tierra:** clase binaria *permafrost probable* si la temperatura media anual de la superficie es **< 271 K** (≈ −2 °C), calculada como la media de los 12 meses de (LST diurna + LST nocturna)/2 de MODIS 2019 (los mismos datos ya reducidos; sin descargas nuevas). Es un **sustituto** de un mapa de permafrost, no el mapa.
- Estas dos clases sustituyen a `ice__water_frac` (que hoy es agua en Marte y nieve en la Tierra) en la dimensión de hielo; el resto del modelo no cambia. La Luna no se toca.
**Evaluación (Marte, 20 análogos congelados; mismas medidas que [VALIDACION_AMPLIADA.md](VALIDACION_AMPLIADA.md)):**
- **Primaria:** diferencia pareada por análogo del u medio de «todas» entre el modelo con las clases y el base, con IC 95 % por bootstrap sobre los análogos. **Criterio de éxito: límite inferior > 0.**
- **Secundaria (decide también):** análogos **fríos** (regla de [PREREGISTRO_GRUPOS.md](PREREGISTRO_GRUPOS.md)) frente a objetivos fríos (|lat| ≥ 45°) con los pesos del modelo frío (hielo 1, topografía 0,5): u con límite inferior **> 0,5**.
**Se adopta solo si se cumplen la primaria y la secundaria.** Si no, no se adopta.

## Qué no se hace
No se cambian el umbral de `H`, el de 271 K, la regla de estación, la puerta de validez ni la referencia ecuatorial después de ver los resultados; cualquier variante se reporta aparte como exploratoria.

## Límites conocidos de antemano
`H` es un índice **relativo** y no un contenido de agua; la escarcha de CO₂ y la nieve de la Tierra no se corrigen más allá de la regla de estación; el sustituto terrestre de permafrost solo usa la temperatura media anual de superficie (no la nieve, la humedad ni el tipo de suelo); la celda de 5° del objetivo mezcla terreno distinto del de la ventana de 50 km; y la clase binaria pierde información (la intensidad de la señal).

## Resultados (hash del preregistro `48118c278237c3dd`; sin cambios al protocolo tras ver los números)

### Fase 1: dato de hielo polar de Marte, conseguido
Se descargaron 287 tablas del PDS (unos 33 MB; hubo que añadir reintentos porque el servidor cortó la conexión una vez). **La puerta de validez se cumple: ρ de Spearman = 0,816 (mínimo 0,6) entre `H` y el hidrógeno ya medido, sobre 1 152 celdas con |latitud| < 42°.** El índice sigue al hidrógeno donde sí había dato, así que es utilizable.
`H` por objetivo (CEPI de referencia ecuatorial 7,36; umbral de «rico en hielo» `H` ≥ 0,405):

| Objetivo | Latitud | `H` | ¿Rico en hielo? |
|---|---|---|---|
| **Phoenix** | 68,2° | **1,299** | **Sí** |
| **Arcadia Planitia** | 47,3° | **0,390** | No (por **0,015** bajo el umbral) |
| Spirit | −14,6° | 0,326 | No |
| Viking 2 | 47,7° | 0,206 | No |
| Los otros 10 objetivos | | de 0,170 a −0,353 | No |

- **Phoenix pasa de «sin dato» a claramente rico en hielo** (la tasa epitérmica es 3,7 veces menor que la ecuatorial), lo que coincide con lo que se sabe de ese sitio.
- **Arcadia queda en 0,390, el segundo valor más alto y apenas por debajo del umbral.** Por el protocolo no se cambia el umbral: se clasifica como «no rico». Es un caso límite y la clase binaria pierde ahí información.
- Solo **un** objetivo (Phoenix) es «rico en hielo» con la regla preregistrada.

### Fase 2: variable de permafrost
Tierra: **470 de 934 celdas** con permafrost probable (temperatura media anual < 271 K); **los 5 análogos fríos** (Valles Secos, Haughton, Svalbard, Axel Heiberg, Eureka) caen en esa clase.

| Prueba | Resultado | ¿Cumple? |
|---|---|---|
| **Primaria:** Marte «todas», diferencia pareada con las clases frente a la base | 0,564 → 0,589; **+0,025 (IC −0,026 a +0,087)** | **No** (límite inferior < 0) |
| **Secundaria:** análogos fríos frente a objetivos fríos con pesos del modelo frío, u con límite inferior > 0,5 | u = **0,370 (IC 0,257 a 0,483)**; diferencia con la base **+0,060 (IC −0,017 a +0,127)** | **No** |

Por análogo frío (u base → variante): Axel Heiberg 0,14 → 0,25; Valles Secos 0,06 → 0,21; Svalbard 0,26 → 0,37; Eureka 0,50 → 0,49; Haughton 0,60 → 0,53.
**Veredicto preregistrado: no se cumplen la primaria ni la secundaria; la variable NO se adopta y el modelo no cambia.**

### Lectura
- **Mejora en la dirección esperada, pero no es concluyente:** tres de los cinco análogos fríos suben bastante (los Valles Secos de 0,06 a 0,21), uno queda igual y Haughton baja; el efecto medio (+0,060) tiene un intervalo que incluye el cero y con 5 análogos no podía ser de otro modo.
- **Sigue por debajo del azar (0,370):** de los tres objetivos «fríos» solo Phoenix es rico en hielo; Arcadia es un caso límite y Viking 2 no lo es. Con un solo objetivo de hielo claro, el test tiene poco que reconocer.
- **Conclusión:** conseguir el dato de hielo polar **sí era el paso correcto** (la puerta de validez se cumple y las clases coinciden con lo esperado: Phoenix rico, los 5 análogos fríos en permafrost), pero con el conjunto actual de objetivos y análogos **no se puede demostrar una mejora**. Lo que haría falta es **más objetivos de hielo somero en Marte** (los de la misión SWIM, por ejemplo) y un conjunto de análogos fríos mayor.
