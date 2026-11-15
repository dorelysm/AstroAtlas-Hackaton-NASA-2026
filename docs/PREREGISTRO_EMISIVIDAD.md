# Preregistro: índice de emisividad infrarroja para la geología (15 nov 2026, escrito ANTES de descargar o calcular nada)

## Aviso previo (corrección a lo que se planteó)
Se propuso este índice como algo que «distinguiría basalto de arena de cuarzo mejor que GLiM». **Eso ignoraba una prueba anterior del proyecto** ([FUENTES.md](FUENTES.md), «ASTER GED, probado y descartado»): con el índice máfico de ASTER, la lava oscura (Craters of the Moon, Harrat Khaybar) tiene un espectro **plano y de alta emisividad (~0,97)** que no se distingue de hielo, agua o vegetación; solo el 9 % de las celdas tenía dato; y la máscara de contraste sesgaba hacia lo félsico.
El contraste de emisividad de MODIS (bandas 29, 31 y 32) detecta sobre todo **cuarzo y minerales félsicos** (una emisividad baja en 8,55 µm), no el basalto. «Sin cuarzo» no es «basalto». **Se espera que falle por el mismo motivo**, y este preregistro está diseñado para comprobarlo barato antes de gastar más.
**Cambio de alcance respecto al planteamiento inicial:** no se encontraron productos cuadriculados de Marte (TES) ni de la Luna (Diviner, 32 píxeles/grado, solo ±60°) que midan la misma banda que MODIS, y calibrar entre bandas diferentes exigiría un modelo espectral que no tenemos. Por eso **no se compara emisividad entre cuerpos**: el índice se usa solo para **medir mejor la fracción de basalto de la Tierra** (hoy GLiM de 0,5°, que da 0,14 en Pinacate y 0 en el Etna), dejando intacto el lado de la Luna y Marte (proxy de FeO).

## Fase 1: viabilidad (cuesta ≈ 70 MB, un solo mes)
**Datos:** NASA MODIS MOD11C3 v061, mes de julio de 2019 (bandas de emisividad `Emis_29`, `Emis_31`, `Emis_32`; emisividad = DN × 0,002 + 0,49; relleno 0). Se borra el archivo tras reducirlo. Es un solo mes: la emisividad del suelo varía poco con la estación (no verificado).
**Índice:** `C = E29 − (E31 + E32)/2` (contraste espectral, que reduce el efecto de la emisividad general por vegetación y humedad). **Mayor C = más máfico** (el cuarzo baja E29, así que da C más negativo). Mediana de los píxeles válidos en una ventana de ±25 km.
**Lugares de litología conocida** (conocimiento general; coordenadas por verificar; **excluidos los que están a < 100 km de alguno de los 23 análogos congelados**, para evitar fuga de información):
- *Basalto (10):* Harrat Rahat (23,5; 39,8), Harrat Khaybar (25,6; 39,9), Harrat Uwayrid (26,1; 37,8), Decán (19,0; 74,5), Karoo/Lesoto (−29,5; 28,5), Paraná (−25,0; −52,0), río Columbia (46,0; −119,5), meseta etíope (10,0; 38,0), Hekla (64,0; −19,7), Jebel Marra (12,9; 24,3).
- *Sin basalto (10):* Rub al Khali (21,0; 51,0), Gran Mar de Arena (27,0; 25,0), arenal del Namib (−24,8; 15,3), Taklamakán (38,9; 83,4), desierto de Simpson (−25,5; 137,0), Sand Hills de Nebraska (42,0; −101,5), escudo canadiense (52,0; −88,0), Alpes (46,5; 9,0), Amazonia (−3,0; −60,0), Kalahari (−23,0; 22,0).
**Puertas (todas deben cumplirse; si no, se detiene y no se pasa a la Fase 2):**
1. **Cobertura:** índice válido en ≥ 90 % de los 20 lugares de litología y en ≥ 80 % de las 951 celdas de la malla (ASTER dio 9 %).
2. **Discriminación:** AUC de C para separar basalto de no basalto ≥ 0,80 (en el sentido «mayor C = basalto»).
3. **Campos pequeños:** de los sitios basálticos que GLiM subestima (fracción de basalto < 0,3 o sin dato: Pinacate, Etna, Lanzarote), al menos 2 de 3 tienen C por encima de la mediana de los 10 lugares sin basalto.

## Fase 2: solo si pasa la Fase 1
Descargar los 12 meses de 2019 (≈ 840 MB), promediar C y calibrar `p_basalto = logística(C)` con los 20 lugares de litología (**no con los análogos**). Nueva característica de la Tierra `geo__basalt_frac` = `p_basalto`, en lugar de la de GLiM; Luna y Marte sin cambios.
**Evaluación (sobre los 23 análogos congelados, mismas medidas que [VALIDACION_AMPLIADA.md](VALIDACION_AMPLIADA.md)):** diferencia pareada por análogo del u medio de «todas» entre el modelo con `p_basalto` y el base, con IC 95 % por bootstrap, para la Luna y para Marte, más «solo geología».
**Criterio de éxito:** el límite inferior de la diferencia pareada de «todas» es **> 0 en al menos un cuerpo** y el límite superior no es **< 0 en ninguno**. Si no se cumple, no se adopta.

## Qué no se hace
No se cambian las puertas, el índice, las ventanas, el mes ni la lista de lugares después de ver los resultados; cualquier variante se reporta aparte como exploratoria.

## Límites conocidos de antemano
Las 20 coordenadas son de conocimiento general; MODIS tiene píxeles de 5 km que mezclan suelo, vegetación y agua; hielo y agua quedan enmascarados; un solo mes; y la relación entre emisividad en 8,55 µm y composición depende de la humedad y la vegetación.

## Resultado de la Fase 1 (hash del preregistro `82bb4a7f27a3e299`; sin cambios al protocolo)
Un mes de MOD11C3 (julio de 2019, descargado y borrado), 20 lugares de litología conocida, 951 celdas de la malla y 3 campos pequeños que GLiM subestima.

| Puerta | Umbral | Resultado | ¿Pasa? |
|---|---|---|---|
| 1. Cobertura | ≥ 90 % de los lugares y ≥ 80 % de las celdas | 100 % de los lugares, **64,2 % de las celdas** | **No** |
| 2. Discriminación (AUC basalto frente a no basalto) | ≥ 0,80 | **0,69** | **No** |
| 3. Campos pequeños sobre la mediana de «sin basalto» | ≥ 2 de 3 | 3 de 3 (Pinacate −0,044, Etna −0,031, Lanzarote −0,053; mediana −0,074) | Sí |

**Veredicto: la Fase 1 falla (dos puertas de tres). Por el protocolo se detiene aquí: no se descargan los 12 meses, no se calibra ni se evalúa la Fase 2, y el modelo no cambia.**

## Qué mostró el índice (coincide con lo que se esperaba)
- **Separa muy bien los arenales de cuarzo:** Rub al Khali −0,21, Gran Mar de Arena −0,18, Namib −0,16, Simpson −0,14.
- **No separa basalto de lo demás:** los 10 lugares basálticos están entre −0,006 y −0,061, el mismo rango que los lugares **cubiertos por vegetación o sin cuarzo** (Alpes −0,006, Sand Hills −0,013, escudo canadiense −0,013, Amazonia −0,015). Es decir, detecta «hay cuarzo desnudo», no «hay basalto». La puerta 3 se cumple porque los tres campos pequeños no son arenales, no porque el índice los reconozca como basalto.
- **Cobertura:** el 36 % de las celdas no tiene índice válido (hielo, agua, relleno), un valor muy superior al 9 % de ASTER pero por debajo del umbral.

Con esto son **dos productos de emisividad infrarroja** (ASTER y MODIS) que no sirven para medir el basalto de la Tierra. La geología se queda en GLiM, con su límite conocido (subestima el basalto en campos pequeños y da la roca subglaciar bajo el hielo).
