# Fichas de candidatos (15 nov 2026)

**Qué son:** celdas de la Tierra que el modelo propone como análogos nuevos (lejos de cualquier análogo conocido de ese cuerpo), con lo que se parece, lo que no y para qué podrían servir.
**Qué NO son:** hallazgos validados. La validación del modelo está cerca del azar ([VALIDACION.md](VALIDACION.md)), así que son **hipótesis para revisar con un experto**, no resultados.

## Cómo se eligieron (y un aviso de honestidad)
Regla (código en `src/analogos/fichas.py`): partir de `candidates_shortlist.csv` (celdas viables, sin vegetación y a más de 500 km de cualquier análogo conocido de ese cuerpo); contar en cuántos objetivos del cuerpo aparece cada celda en el top 10; quedarse con las 2 primeras separadas al menos 500 km.
**Aviso:** la regla se escribió **después** de ver una lista preliminar de celdas repetidas, no antes. Es una regla mecánica y simple (no se escogió a mano ninguna celda), pero no es un preregistro estricto.
Las dos marcas usadas para filtrar (`viable`, `vegetated`) no entran al score y no se aplican a la validación. El filtro de vegetación se añadió **porque** las primeras candidatas de Marte eran selvas de Nueva Guinea e Indonesia (el modelo no tiene dimensión de biología y la variable "hielo" vale ~0 igual que en Marte); eso se descubrió viendo los resultados, y se documenta aquí.

Cada celda es un punto de una malla de 5° y las variables se calculan en una **ventana de 50 × 50 km** alrededor de su centro, no en toda la región. Los nombres de región son una interpretación a partir de las coordenadas (por comprobar).

## Marte

### A. Meseta basáltica de Harrat ash-Shamah (sur de Siria / norte de Jordania) · `earth_24_43` · 32.5° N, 37.5° E
Aparece en el top 10 de **13 de los 14 objetivos de Marte** (puntaje medio 0.76).

| Dimensión | Puntaje | Valor en la Tierra | Lectura |
|---|---|---|---|
| Geología | 0.85 | 100 % de la ventana es basalto (GLiM) | **Parecido real**: Marte es un planeta basáltico |
| Topografía | 0.53 | pendiente media 0.74°, relieve local 242 m | Parecido moderado; llana pero con relieve |
| Hielo/agua | 0.90 | nieve media 0 | **Artefacto**: coincide solo por ausencia de nieve; no mide sequedad ni hielo subsuperficial |
| Térmica | sin dato | T máx. mensual 325 K, rango diurno 20 K | Marte no tiene térmica en el modelo |

- **Polvo y viento (solo contexto, MERRA-2 2019):** polvo en superficie 88 µg/m³ (alto), viento medio a 10 m 2.5 m/s. En Marte el polvo y las tormentas son un factor operativo clave, pero el modelo no los compara.
- **Vegetación:** NDVI máx. 0.12 (suelo casi desnudo). **Población:** el asentamiento de ≥ 1 000 hab. más cercano (As-Suwayda') está a 90 km. Análogo conocido más cercano: Río Tinto, a 4 012 km.
- **Qué podría aportar:** probar rovers y navegación sobre campo de lava con rocas sueltas y suelo desértico; práctica de muestreo geológico en terreno basáltico.
- **Dónde falla la analogía:** gravedad (0.38 g en Marte), atmósfera (0.6 % de la terrestre), radiación, y sobre todo **no sabemos si es seco como Marte**: el modelo no lo mide. Tiene clima árido, pero no es un análogo de hielo.
- **Riesgo práctico:** la zona está en una región con inseguridad y restricciones de acceso; antes de proponerla como sitio de campo habría que evaluar eso. El modelo no lo ve.

### B. Campo volcánico de Haruj (Libia) · `earth_23_39` · 27.5° N, 17.5° E
Aparece en **9 de 14** objetivos de Marte (puntaje medio 0.69).

| Dimensión | Puntaje | Valor en la Tierra | Lectura |
|---|---|---|---|
| Geología | 0.86 | 100 % basalto | **Parecido real** |
| Topografía | 0.32 | pendiente media 0.59°, relieve 368 m | **Parecido bajo**: es la dimensión más floja |
| Hielo/agua | 0.90 | nieve media 0 | **Artefacto** (igual que arriba) |
| Térmica | sin dato | T máx. 328 K, rango diurno 24 K | Sin comparar |

- **Polvo y viento (solo contexto, MERRA-2 2019):** polvo en superficie 187 µg/m³ (muy alto; es el Sahara), viento medio 2.4 m/s.
- **Vegetación:** NDVI máx. 0.09. **Población:** el asentamiento de ≥ 1 000 hab. más cercano (Waddan) está a 229 km, el más aislado de las dos. Análogo conocido más cercano: Río Tinto, a 2 512 km.
- **Qué podría aportar:** desierto hiperárido con campo volcánico extenso y aislado; un lugar para ensayos de autonomía donde las comunicaciones y el apoyo logístico son parte de la prueba.
- **Dónde falla:** igual que A, y su topografía solo se parece moderadamente.
- **Riesgo práctico:** acceso y seguridad en Libia; también habría que verificarlo.

## Luna

### C y D. Superficie helada de la Antártida (barrera de hielo de Ross y alrededores) · `earth_2_70` (−77.5°, 172.5° E) y `earth_1_0` (−82.5°, 177.5° O)
Aparecen en **7 de 21** objetivos lunares (puntaje medio 0.51 y 0.51).

- **Solo hay dato de topografía** (puntaje 0.51 en ambas): son superficies de hielo extremadamente llanas (pendiente media 0.06° y 0.04°). Térmica, hielo y geología no tienen dato válido en estas celdas (no se comprobó la causa exacta; es probable que sea la noche polar y el hielo), así que el puntaje **solo dice que son planas como un mar lunar**.
- **Valoración honesta:** **no son buenos análogos lunares.** Una barrera de hielo plana no se parece a un mar de basalto lunar en materiales, temperatura (la Luna llega a 390 K de día) ni procesos. Aparecen porque el modelo, sin otras dimensiones, premia lo llano. Se muestran por transparencia y como ejemplo del límite del método.
- **Polvo y viento (contexto):** casi sin polvo (0.3 µg/m³) y con viento medio de 5 a 7 m/s, de los más altos de la muestra: opuesto a las candidatas de Marte.
- **Sí tiene una lectura útil:** la logística polar (ensayos de operación en frío, rovers sobre superficie llana, comunicaciones a latitudes altas) se parece más a una base lunar polar que a un sitio de aterrizaje ecuatorial; pero eso es una idea nuestra, no algo que el modelo muestre.
- Una de las celdas (C) está a unos 250 km de los Valles Secos, que es un análogo conocido de Marte (no de la Luna), por eso no la excluye la regla de 500 km.

## Lo que estas fichas dicen sobre el método
1. Las **dos candidatas de Marte son campos volcánicos basálticos en desierto**: coincide con lo que se esperaría de un buen análogo geológico y es el resultado más defendible. Pero se parecen a **sitios ya estudiados** (hay análogos basálticos conocidos como Craters of the Moon o Lanzarote) y por topografía solo se parecen moderadamente.
2. Las candidatas lunares son un **artefacto de tener una sola dimensión con dato**. La dimensión faltante pesa mucho más que cualquier ajuste del modelo.
3. Sin la marca de vegetación, las primeras candidatas de Marte eran selvas. Esto confirma que **faltan dimensiones de contexto** (biología, cuevas, polvo y viento, iluminación) antes de poder confiar en el ranking.
4. Todo lo dicho sobre uso para la exploración es **plausible, no demostrado por los datos**.

## Datos de apoyo
`data/results/fichas_candidatos.{csv,json}` (no se versiona; se regenera con `python -m analogos.fichas`).
