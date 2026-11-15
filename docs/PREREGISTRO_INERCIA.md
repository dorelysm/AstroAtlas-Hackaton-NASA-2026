# Preregistro: dimensión de inercia térmica (15 nov 2026, escrito ANTES de calcular ningún puntaje con ella)

**Motivo:** la validación ampliada ([VALIDACION_AMPLIADA.md](VALIDACION_AMPLIADA.md)) mostró que el modelo recupera los análogos áridos, volcánicos y de impacto pero falla con los fríos y de hielo, y que Marte no tiene térmica. La inercia térmica es una propiedad del suelo (qué tan rápido cambia su temperatura) y se mide en Marte con TES.
**Conjunto de prueba:** los 23 análogos congelados ([PREREGISTRO_ANALOGOS.md](PREREGISTRO_ANALOGOS.md)); no se modifica. **Modelo base:** el congelado (commit `0b8a0a2`).

## Definición (fijada)
- **Marte:** mapa nocturno de inercia térmica de MGS-TES (Putzig y Mellon 2007; PDS `mgs-m-tes-5-timap-v1`, unidades J·m⁻²·K⁻¹·s⁻¹ᐟ²), 7200 × 3600 píxeles, 20 píxeles/grado. Se usan solo píxeles no interpolados (máscara = 1) y con valor > 0. Para cada objetivo, **mediana** de los píxeles válidos en una ventana de ±25 km. Se convierte a **percentil** frente a todos los píxeles válidos de Marte con |latitud| ≤ 80°.
- **Tierra:** no hay un equivalente directo. Se usa un **proxy aparente sin albedo**: `1 / (T_día − T_noche)`, con el rango diurno medio de MODIS LST (ya calculado, `thermal__t_range_k`; un rango térmico pequeño equivale a inercia alta). Se convierte a **percentil** frente a las 951 celdas de la malla terrestre. Los 23 análogos usan el mismo percentil de referencia.
- **Comparación:** se comparan **percentiles dentro de cada cuerpo** («este sitio está en el X % más inerte de su planeta»). Es una analogía **relativa**: los valores absolutos de inercia no son comparables (otros horarios de observación, atmósfera, sensor), y se dice así en los resultados.
- **Luna:** sin dato (no hay un mapa de inercia comparable en este alcance). La dimensión no se aplica a la Luna.
- Se añade como una quinta dimensión, `inertia`, con peso igual a las demás.

## Evaluación (fijada)
Misma medida que la validación ampliada (u por análogo, ventanas de 50 km, bootstrap sobre los análogos), solo para **Marte**, comparando:
- **«todas + inercia»** frente a **«sin inercia»** (el modelo base de 4 dimensiones, que no usa inercia): **diferencia pareada por análogo** y su IC 95 % por bootstrap.
- **«solo inercia»**: u medio y su IC.
- Secundario (descriptivo): la variación de u en los análogos fríos (Valles Secos, Axel Heiberg, Svalbard, Eureka).

**Criterio de éxito:** la diferencia pareada «todas + inercia» − «sin inercia» es **positiva con límite inferior del IC > 0**, y el u de «todas + inercia» tiene límite inferior > 0,5. Si no se cumple, **no se adopta** la dimensión.
**Qué no se hace:** no se prueban otros percentiles de referencia, otras ventanas, el mapa diurno, ni versiones con albedo después de ver los resultados; si se hiciera, se reporta aparte como exploratorio.

## Límites conocidos de antemano
Sin albedo en el proxy terrestre; MODIS pasa a las 10:30 y 22:30 y TES a otras horas; el mapa de TES no es una sola época; los percentiles suponen que cada planeta cubre un rango comparable de «polvo a roca», lo cual no está demostrado; y solo aplica a Marte.

## Resultados (hash del preregistro `ce95183026ef90a5`; sin cambios al protocolo tras ver los números)
Marte, 20 análogos del conjunto congelado. u medio con IC 95 % por bootstrap sobre los análogos (0,5 = azar):

| Configuración | u medio | IC 95 % |
|---|---|---|
| Sin inercia (modelo base, 4 dimensiones) | 0,564 | 0,448 a 0,678 |
| **Todas + inercia (5 dimensiones)** | **0,483** | 0,400 a 0,574 |
| **Solo inercia** | **0,363** | 0,266 a 0,463 |
| Solo hielo (nieve), a modo de referencia | 0,633 | 0,507 a 0,751 |

- **Diferencia pareada «todas + inercia» − «sin inercia»: −0,081 (IC −0,133 a −0,025).** Es **negativa y su IC excluye el cero**: añadir la dimensión **empeora** el resultado.
- **«Todas + inercia» tiene u = 0,483 < 0,5.**
- **Veredicto: no se cumple el criterio. La dimensión de inercia térmica NO se adopta.** El modelo del proyecto no cambia. (El u del modelo base, 0,564, reproduce exactamente el de la validación ampliada.)

## Qué hizo la dimensión
«Solo inercia» **invierte** el orden de los análogos:
- **Mejora los fríos y de hielo:** Valles Secos 0,03 → 0,12, Axel Heiberg 0,10 → 0,21, Svalbard 0,18 → 0,33, Eureka 0,38 → 0,51 (con todas las dimensiones). Su u «solo inercia» es ≈ 0,67.
- **Empeora los cálidos y áridos:** Atacama 0,05, Salar Grande 0,05, Meteor Crater 0,07, Pinacate 0,08, Vredefort 0,17 («solo inercia»); con todas las dimensiones, Pinacate cae de 0,79 a 0,56, Atacama de 0,65 a 0,43, Meteor Crater de 0,69 a 0,48.
- **Por qué (hipótesis, no comprobada):** el proxy terrestre `1/(T_día − T_noche)` de MODIS depende mucho de la humedad, la nieve y la cobertura, no solo de las propiedades del suelo; los desiertos calientes tienen amplitudes diurnas grandes y salen con «baja inercia», lo contrario de lo que se esperaba. Además MODIS y TES observan a horas distintas y no hay albedo. Los percentiles dentro de cada cuerpo no resolvieron la falta de comparabilidad.
- **Observación (no probada):** el conjunto de análogos mezcla dos grupos, los cálidos y áridos (que el modelo base reconoce) y los fríos y de hielo (que reconoce «solo inercia» o «solo hielo»). Una sola similitud global no sirve a ambos; es un argumento a favor de evaluar por aspecto o por caso de uso, como hace el atlas.

## Lo que queda abierto (no hecho, por el protocolo)
Versión con albedo (MODIS MCD43), mapa diurno de TES, otra referencia de percentiles o un modelo térmico real. Cualquiera de ellas sería **exploratoria** y se reportaría aparte, sin sustituir este veredicto.
