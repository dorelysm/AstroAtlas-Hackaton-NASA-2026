# Preregistro: conjunto ampliado de análogos de validación (15 nov 2026, escrito ANTES de buscar)

**Por qué:** con 10 análogos (4 a 8 por cuerpo) ninguna medida puede ser concluyente, y cualquier mejora que se pruebe sobre ellos sería ajustar al test. Se construye un conjunto mayor, se **congela** y solo después se mide.
**Modelo congelado:** el del commit `0b8a0a2` (puntaje por dimensión `exp(−RMS z)`, PCA blanqueada de la topografía, pesos iguales). **No se cambia nada del modelo al ver estos resultados**; cualquier mejora posterior se prueba contra este conjunto ya fijo y se reporta aparte.

## Criterios de inclusión (todos obligatorios)
1. Una fuente abierta **nombra el sitio como análogo terrestre de la Luna y/o de Marte**: página de agencia (NASA, ESA, USGS, JAXA...), artículo o resumen revisado de congreso (LPSC, AGU...), o página de un instituto o universidad dedicado a análogos.
2. Es un **sitio localizable** (un campo de lava, cráter, valle, salar...), no un desierto entero. Hace falta una coordenada con incertidumbre razonable (≈ ≤ 10 km), de la propia fuente o de Wikipedia/gazetteer, con su origen anotado.
3. **No se consulta ningún resultado del modelo** para decidir qué sitios entran.
4. **Independencia:** si dos sitios candidatos están a menos de 100 km, entra solo el de fuente más fuerte (agencia > artículo > universidad > otro).
5. Los 10 análogos actuales **se conservan** y se reportan por separado (originales / nuevos / todos).

## Búsquedas (fijadas; no se añaden consultas para buscar más sitios después de ver los resultados)
(1) `basaltic lava field terrestrial analog Mars field site NASA` · (2) `Mars analog cold desert permafrost field site Axel Heiberg Devon Island Dry Valleys` · (3) `hyperarid desert Mars analog field site Atacama Yungay Salar` · (4) `impact crater terrestrial analog Moon Mars field site Meteor Crater Ries` · (5) `lunar analog terrestrial field site volcanic ash regolith simulant` · (6) `Mars analog acidic evaporite salt flat field site Danakil Uyuni Rio Tinto` · (7) `Mars analog dunes aeolian field site Namib Qaidam` · (8) `lava tube cave planetary analog field site Lava Beds Undara`.
Solo se hacen consultas de seguimiento para **obtener coordenadas o la razón citada** de sitios ya encontrados.

## Etiquetas de aspecto
Una etiqueta de aspecto (topo, thermal, ice, geo, cuevas, eólico) solo se asigna si el texto de la fuente nombra ese aspecto. Niveles: *fuente* (el texto lo dice) o *nota* (lo dice nuestra nota). Si no hay aspecto nombrado, el sitio entra a la validación global pero a ninguna por aspecto.

## Plan de evaluación (fijado)
- Mismas métricas que antes: u = P(análogo > celda típica) con ventanas de 50 km (`validate.evaluate_sites`), **bootstrap sobre los análogos**, una medida por cuerpo y por conjunto (originales / nuevos / todos).
- **Criterio de éxito:** el límite inferior del intervalo de confianza del u medio ("todas las dimensiones") es **> 0,5** en cada cuerpo con al menos 8 análogos. Se reportan además los intervalos por aspecto cuando haya ≥ 3 análogos por grupo.
- Las dimensiones que el sitio no tenga (p. ej. térmica de Marte) se ignoran, igual que en el modelo.
- **Límite:** se calcularán las características de los sitios nuevos solo con topografía (Copernicus), térmica y nieve (MODIS) y geología (GLiM), para no repetir toda la descarga de contexto; las marcas de población y vegetación no se aplican a la validación.

## Lista congelada (anexo, escrito después de las 8 búsquedas y ANTES de calcular ninguna característica ni ningún puntaje)
- `docs/analogos_ampliado.csv` (13 sitios nuevos), sha256 `0f234908cd16ce94`; `docs/aspectos_analogos_ampliado.csv` (10 etiquetas), sha256 `3cc33c3ddf4c8a6f`. Con los 10 originales suman **23 análogos**. Ningún par de sitios está a menos de 100 km.
- **No se llegó a los ~30 previstos:** las 8 consultas fijadas produjeron 13 sitios que cumplen los criterios, y el protocolo no permite añadir consultas para buscar más.
- **Excluidos y por qué:** Mauna Ulu/Kilauea, Mauna Loa y Snake River Plain (a < 100 km de Mauna Kea y de Craters of the Moon, que se conservan); Yungay y Salar de Pajonales (a < 100 km del punto de Atacama); Steinheim (a < 100 km de Ries); Beacon Valley (en la misma celda de los Valles Secos); Undara (la búsqueda no lo presenta como análogo); Qaidam (la fuente propone la cuenca entera, no un sitio localizable, y excluirlo evita reforzar el resultado de movilidad que ya salió); Eifel (región, no sitio); Merriam Crater/Cinder Lake (a < 100 km de Meteor Crater). Wudalianchi apareció en otra búsqueda (la del control de novedad), no en las 8 de este protocolo, y queda para una segunda versión.
- **Coordenadas:** todas las de los sitios nuevos vienen de conocimiento general o Wikipedia y están marcadas **POR VERIFICAR** en el CSV. Un error de decenas de kilómetros cambiaría poco el resultado (ventana de 50 km), pero no está comprobado.
- **Sesgo conocido de la selección:** abundan los cráteres de impacto (5 de 13) porque un artículo puntúa 11 estructuras; eso da peso al aspecto topográfico.
