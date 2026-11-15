# Análogos terrestres para bases en la Luna y Marte: un método reproducible y sus límites

NASA Space Apps Challenge 2026 · reto *Permanent Moon Base Locations and Mars* · estado a 15 de noviembre de 2026

## Resumen
Construimos un **índice de similitud multidimensional** que compara celdas de la Tierra con 35 sitios de la Luna (21) y Marte (14) usando datos abiertos de NASA y otras agencias, y lo **validamos contra análogos terrestres conocidos**. El método funciona de punta a punta y es reproducible, pero **su poder para recuperar análogos conocidos es casi nulo** (AUC por sitios 0,58 y recall 0,17, con 0,5 y 0,05 como azar). Lo presentamos como un **método y un conjunto de resultados negativos documentados**, no como un mapa de hallazgos. Las candidatas que propone son hipótesis para revisar con expertos.

## 1. Idea
Para cada sitio objetivo se calcula qué tan parecida es cada celda de la Tierra, dimensión por dimensión: **topografía, térmica, agua/hielo y geología**. El puntaje por dimensión es `exp(−distancia)` entre variables estandarizadas (la topografía, con 16 variables, se comprime con PCA); el global es una media ponderada de las dimensiones disponibles. Cada celda lleva además dos **marcas de contexto** que no entran al puntaje: población cercana (`viable`) y vegetación (`vegetated`).

## 2. Datos (todos abiertos)
| | Topografía | Térmica | Hielo / agua | Geología |
|---|---|---|---|---|
| **Luna** | LOLA | Diviner | Lunar Prospector GRS (solo 2 objetivos polares con dato) | sí, proxy de FeO (Lunar Prospector GRS) |
| **Marte** | MOLA | vacía (decisión) | Odyssey GRS | sí |
| **Tierra** | Copernicus GLO-90 | MODIS LST | MODIS nieve | GLiM (no NASA, CC-BY) |

Línea base común: 500 m y ventana de 50 km. Cada descarga se reduce y se borra (por ejemplo, 1,2 GB de NDVI quedan en unos pocos MB). Procedencia y licencias: [FUENTES.md](FUENTES.md), [LICENCIAS.md](LICENCIAS.md).

## 3. Cómo validamos
Los análogos conocidos (10, más una capa del USGS con 185 cráteres y dunas y 200 controles) **solo validan, nunca ajustan el modelo**. La métrica es *u* = probabilidad de que un análogo puntúe más que una celda típica (0,5 = azar), con bootstrap sobre los análogos porque son la unidad independiente. **Etiquetas, protocolos y criterios se fijaron antes de medir** y se registró su huella; las correcciones posteriores se reportan aparte.

## 4. Resultados
1. **Validación global cerca del azar.** AUC por sitios 0,58 (rango 0,27 a 0,89 según el objetivo); recall en el 5 % superior 0,17. [VALIDACION.md](VALIDACION.md)
2. **Ninguna dimensión queda validada de forma concluyente.** Con 1 a 3 análogos por grupo, el p mínimo alcanzable es 0,20. La geología va en la dirección correcta en Luna (+0,53) y Marte (+0,97), con muy pocos casos. [VALIDACION_ASPECTO.md](VALIDACION_ASPECTO.md)
3. **El hielo de Marte falla donde debía acertar** (Valles Secos, −0,75): la nieve de la Tierra no mide sequedad. Probamos humedad del suelo (GLDAS) con un criterio fijado antes; no mejora. [PREREGISTRO_HIELO.md](PREREGISTRO_HIELO.md)
4. **La poca señal de la topografía era terreno llano.** Con cráteres y controles igual de llanos, el AUC de Marte baja de 0,567 a 0,494. [PREREGISTRO_LLANURA.md](PREREGISTRO_LLANURA.md)
5. **La búsqueda de más análogos para térmica e hielo no añadió ninguno evaluable.** [BUSQUEDA_ANALOGOS.md](BUSQUEDA_ANALOGOS.md)

## 5. Candidatos
Aplicando las marcas de población y vegetación y alejándonos de los análogos conocidos, salen **dos campos volcánicos basálticos en desierto para Marte** (Harrat ash-Shamah y Haruj), con coincidencia geológica real y topografía solo moderada, y **dos celdas antárticas para la Luna** que solo salen por ser planas y valoramos como malos análogos. [FICHAS_CANDIDATOS.md](FICHAS_CANDIDATOS.md) detalla qué se parece, qué no y los límites (gravedad, atmósfera, radiación).

## 6. Casos de uso
En vez de un solo ranking, seis perfiles de uso ([CASOS_DE_USO.md](CASOS_DE_USO.md)): solo el terreno basáltico de Marte da una recomendación defendible (las candidatas de las fichas); movilidad da parecidos moderados y los casos de frío y hielo muestran los límites de la Tierra como análogo.

## 6a. Atlas por aspecto y procesos
[ATLAS_ASPECTOS.md](ATLAS_ASPECTOS.md) evalúa cada dimensión por separado con una etiqueta de confianza que sale de los resultados medidos (ninguna llega a "alta"). [PROCESOS.md](PROCESOS.md) trata tres procesos (vulcanismo y tubos de lava, transporte eólico, hielo subsuperficial) como estudios de caso cualitativos: solo el volcánico conecta con nuestros resultados.

## 6b. Lo que aprendimos
- **Falta dimensión de contexto, no ajuste fino:** sin vegetación, las primeras candidatas de Marte eran selvas.
- **Las variables no significan lo mismo entre cuerpos:** nieve ≠ hielo subsuperficial; la temperatura mensual terrestre no reproduce los extremos diarios de Marte.
- **Con 4 a 8 análogos por cuerpo, ningún resultado puede ser concluyente**; el cuello de botella es la validación, no el cálculo.
- **El rigor fue el aporte:** protocolos fijados antes de medir, controles contra el sesgo de terreno llano, y resultados negativos reportados.

## 7. Límites
Pocos análogos; confusión con terreno llano y estable; semántica distinta entre cuerpos; Marte sin térmica; polvo/viento, cuevas e iluminación sin cubrir ([DIMENSIONES_NO_MODELADAS.md](DIMENSIONES_NO_MODELADAS.md)); datos de población de 1990-2010; coordenadas de varios análogos sin fuente primaria ([VERIFICACION_COORDENADAS.md](VERIFICACION_COORDENADAS.md)). La Tierra tampoco reproduce la gravedad reducida, el vacío lunar, la atmósfera tenue de Marte ni su radiación.

## 8. Cómo reproducirlo
`pip install -e ".[app,dev]"`, `python -m analogos.pipeline` y `streamlit run app/streamlit_app.py`. La app corre sin descargar nada gracias a `demo_data/`. Detalle en el [README](../README.md).

## 9. Próximos pasos
Ampliar la lista de análogos con fuentes primarias y definir antes de medir qué objetivos aplican a cada aspecto; resolver Marte térmica; añadir una variable de sequedad con contraparte marciana; comprobar las coordenadas y licencias pendientes.
