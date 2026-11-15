# Resumen del proyecto (versión para no técnicos)

**NASA Space Apps Challenge 2026 · reto «Permanent Moon Base Locations and Mars»**
Estado a 15 de noviembre de 2026. Este documento está pensado para que el equipo saque de aquí las ideas para las diapositivas y la descripción del proyecto. Cada cifra tiene su fuente en `docs/` (los enlaces están al final).

**App en línea (se puede abrir y probar): https://app-production-6cc653bd.up.railway.app**
Código: https://github.com/dorelysm/AstroAtlas-Hackaton-NASA-2026

---

## 1. En una frase
Construimos un **buscador de lugares de la Tierra que se parecen a lugares de la Luna y de Marte**, y lo evaluamos con honestidad contra lugares que los científicos ya usan para entrenar. El resultado es un **método reproducible y unas pistas concretas**, no una lista de sitios garantizados.

## 2. Qué pedía el reto
Usar datos abiertos de la NASA y de otras agencias para **encontrar y explicar lugares de la Tierra que sirvan de análogo** (un «ensayo general») de bases o sitios de aterrizaje en la Luna y en Marte: qué se parece, qué no, y para qué serviría. El reto insiste en **no limitarse a los sitios ya famosos** (Atacama, Antártida, Islandia, Hawái) y en explicar **dónde falla la analogía**.

## 3. Qué hicimos, explicado sin tecnicismos
1. **Elegimos 35 sitios objetivo:** 21 en la Luna (los de las misiones Apolo, Luna, Surveyor y Chang'e, más dos del polo sur) y 14 en Marte (Jezero, Gale, Oxia Planum, Phoenix...).
2. **Dividimos la Tierra en 951 zonas** de unos 500 km y medimos en cada una cuatro cosas, con los mismos datos que se usan en Luna y Marte:
   - **Relieve** (qué tan llano, rugoso o inclinado es el terreno).
   - **Temperatura** de la superficie.
   - **Hielo o agua.**
   - **Geología** (si hay roca volcánica, el basalto, que es lo que cubre Marte y los mares lunares).
3. **Calculamos el parecido** de cada zona de la Tierra con cada sitio de la Luna o de Marte, aspecto por aspecto, y lo combinamos en una nota de 0 a 1.
4. **Comprobamos si funciona:** vimos si el método reconoce a 23 lugares de la Tierra que los científicos ya usan como análogos (Atacama, Lanzarote, Pinacate, Meteor Crater...). **Esa lista la fijamos antes de medir, para no hacernos trampa.**
5. **Añadimos filtros de realismo:** una zona se marca si hay un pueblo cerca (≥ 1 000 habitantes a menos de 50 km) o si tiene vegetación, porque un análogo con selva no sirve para Marte. Estos filtros no cambian la nota, solo se muestran.

## 4. ¿Funciona? La respuesta honesta
Para medir el acierto usamos una cifra sencilla: **«si tomo un lugar que sabemos que es un buen análogo, ¿con qué frecuencia puntúa más alto que una zona cualquiera de la Tierra?»** Si fuera al azar, sería el 50 %.

| | Resultado | Cómo leerlo |
|---|---|---|
| **Luna** | **60 %** (entre 55 % y 64 %) | Supera el azar, pero por poco |
| **Marte** | **56 %** (entre 45 % y 68 %) | **No se puede afirmar que funcione**: el margen incluye el azar |

**Lo que sí hace bien:** reconoce los análogos **áridos, volcánicos y de impacto** (Lanzarote 96 %, Pinacate 79 %, Atacama 65 %, el cráter de Ries 75 %...).
**Lo que no hace bien:** los análogos **fríos y de hielo** (Valles Secos de la Antártida 4 %, Axel Heiberg 10 %, Svalbard 18 %). La razón principal es que **la «nieve» de la Tierra no mide lo mismo que el hielo bajo el suelo de Marte**, y no tenemos todavía un dato terrestre equivalente.
**El único aspecto con señal clara es la geología** (si el terreno es volcánico), aunque descansa en pocos casos.

> **Mensaje clave para las diapositivas:** «Construimos un método transparente, lo sometimos a pruebas con criterios fijados de antemano, y sabemos exactamente dónde funciona (terreno árido y volcánico) y dónde no (hielo y frío)».

## 5. Los lugares que propone el método
Aplicando los filtros (sin pueblos cercanos, sin vegetación, lejos de los análogos famosos) salen **dos candidatos para Marte**:

| Candidato | Dónde | Por qué | Qué hay de nuevo |
|---|---|---|---|
| **Harrat ash-Shamah** | Sur de Siria y norte de Jordania (32,5° N, 37,5° E) | Meseta de roca volcánica (basalto), como gran parte de Marte | Ya se usó como análogo de **hoyos y cuevas planetarios**; hay **8 tubos de lava documentados** en la parte jordana |
| **Haruj** | Libia central (27,5° N, 17,5° E) | Campo volcánico enorme (~45 000 km², unos 150 volcanes), en pleno desierto | **No encontramos ningún estudio que lo use como análogo** de Marte o de la Luna: es el menos estudiado |

**Fuerza del resultado:** al probar el método miles de veces cambiando los parámetros, Harrat ash-Shamah queda entre los mejores **el 100 % de las veces** y Haruj el 79 %. **Pero ser estable no significa ser correcto.**
**Límites que hay que decir:** ambos tienen problemas de acceso y seguridad; el parecido de relieve es solo moderado; y no sabemos si los tubos de lava están dentro de la zona exacta.
**Para la Luna** el método no encuentra candidatos creíbles: las zonas que salen (Antártida) solo se parecen por ser llanas.

## 6. Qué más ofrece el proyecto
- **Atlas por aspecto:** en vez de una sola nota, muestra qué lugares se parecen **en relieve, en geología, en temperatura o en hielo por separado**, con una etiqueta de **confianza** que sale de los resultados medidos (ninguno llega a «alta»). El reto pide justamente esto: un lugar puede ser un gran análogo geológico y uno malo en temperatura.
- **Recomendaciones por caso de uso:** probar el movimiento de un rover, operar en frío, buscar terreno volcánico... Solo el caso volcánico de Marte da una recomendación defendible.
- **Contexto de procesos:** cuevas y tubos de lava, polvo y viento, y hielo bajo el suelo, con lo que dice la literatura científica y qué parte cubrimos nosotros.
- **Una app web** donde se elige un sitio de la Luna o de Marte y se ve el mapa de zonas parecidas, con una ficha que dice **qué se parece, qué no y los límites de la analogía** (gravedad, atmósfera, radiación).

## 7. Por qué la forma de trabajar también es un resultado
Casi todo lo que probamos lo **preregistramos**: escribimos el criterio de éxito **antes** de mirar los números y lo dejamos registrado. Así probamos **seis ideas para mejorar el método** y las seis salieron mal o sin efecto:

| Idea | Resultado |
|---|---|
| Cambiar la variable de hielo por humedad del suelo | No mejora |
| Añadir la inercia térmica (qué tan rápido cambia de temperatura el suelo) | Empeora |
| Usar la emisividad infrarroja para detectar basalto | No funciona (detecta arena de cuarzo, no basalto) |
| Describir la rugosidad a varias escalas | Sin efecto |
| Ajustar la tolerancia según lo variable que sea cada sitio | Empeora un poco |
| Separar análogos fríos y cálidos | Mejora los fríos, pero siguen por debajo del azar |

También **corregimos errores propios a la vista** (por ejemplo, descubrimos que una «señal» del relieve en Marte se debía solo a que los cráteres están en zonas llanas, y que las primeras candidatas eran selvas). Esta transparencia es un punto fuerte frente a un jurado.

> **Mensaje clave:** «No solo buscamos qué funciona: medimos qué no funciona y lo dejamos documentado».

## 8. Qué NO conviene afirmar
- ❌ «Encontramos los mejores lugares de la Tierra para entrenar para Marte.» → Son **hipótesis** para revisar con expertos.
- ❌ «El método predice análogos.» → Con Marte no se distingue del azar; con la Luna, por poco.
- ❌ «Haruj es un análogo desconocido.» → Solo decimos que **en nuestra búsqueda no apareció** un estudio; no prueba que no exista.
- ❌ «El método encuentra análogos de cuevas o tubos de lava.» → **No**: el modelo no ve los tubos. Solo aportamos contexto (hay 8 tubos documentados en la región de Harrat ash-Shamah, y ningún dato en Haruj, que no está cubierto por el catálogo).
- ✅ Sí: «Método transparente y reproducible», «sabemos dónde falla», «candidatas concretas con sus límites», «geología como aspecto más fiable».

## 9. Limitaciones, dichas con claridad
- **Pocos análogos para comprobar** (23): los márgenes son anchos.
- **El hielo y el frío son el punto débil:** no hay un dato terrestre equivalente al hielo de Marte.
- **Marte no tiene dato de temperatura** en nuestro modelo (no hay un mapa comparable).
- **Las coordenadas de varios análogos vienen de Wikipedia o de memoria** y no están verificadas en fuente primaria; hay que revisarlas a mano.
- **Algunas licencias de datos están «por comprobar»** (Copernicus, SEDAC, MODIS, PDS): hay que abrir sus páginas y copiar la atribución exacta.
- **La Tierra no reproduce** la gravedad reducida, el vacío lunar, la atmósfera tenue de Marte ni su radiación.
- Parte de la búsqueda de fuentes y del código se hizo con **asistentes de IA** y lo revisó el equipo. Conviene declararlo si el concurso lo pide.

## 10. De dónde salen los datos (para la diapositiva de fuentes)
- **NASA:** altimetría láser de la Luna (LOLA) y de Marte (MOLA), temperatura lunar (Diviner), composición (Lunar Prospector y Mars Odyssey), temperatura, nieve y vegetación de la Tierra (MODIS), población (SEDAC), polvo y viento (MERRA-2), humedad del suelo (GLDAS).
- **ESA:** relieve de la Tierra (Copernicus DEM).
- **USGS:** capa de sitios análogos y catálogo de cuevas de Marte.
- **Otros abiertos:** mapa de rocas de la Tierra (GLiM, CC BY), pits lunares (LROC, vía Zenodo, CC BY), catálogo de tubos de lava (Pyroduct, CC BY).
- Procedencia completa: `docs/FUENTES.md`. Licencias: `docs/LICENCIAS.md`.

## 11. Cifras para tener a mano
- **35** sitios objetivo (21 Luna, 14 Marte) · **951** zonas de la Tierra · **4** aspectos medidos.
- **23** análogos de validación (10 originales + 13 nuevos) · **6** ideas probadas, todas documentadas.
- **60 %** de acierto en la Luna, **56 %** en Marte (50 % = azar).
- **100 %** de estabilidad de Harrat ash-Shamah, **79 %** de Haruj.
- **152** pruebas automáticas · una sola rama de código (`main`) · app desplegada.

## 12. Mini-glosario
- **Análogo:** lugar de la Tierra parecido a otro mundo, usado para ensayar.
- **Basalto:** roca volcánica oscura que cubre buena parte de Marte y de los «mares» lunares.
- **Tubo de lava:** cueva que deja la lava al enfriarse; podría proteger a futuros astronautas.
- **Preregistro:** escribir el criterio de éxito antes de ver los resultados, para no ajustarlo a posteriori.
- **«Azar» (50 %):** lo que saldría si el método no supiera nada.

## 13. Dónde profundizar
| Quiero saber... | Leer |
|---|---|
| El informe completo | `docs/INFORME.md` |
| Cómo de bien funciona | `docs/VALIDACION_AMPLIADA.md` |
| Los dos candidatos | `docs/FICHAS_CANDIDATOS.md` |
| Qué se parece en cada aspecto | `docs/ATLAS_ASPECTOS.md` |
| Para qué sirve cada lugar | `docs/CASOS_DE_USO.md` |
| Procesos (cuevas, polvo, hielo) | `docs/PROCESOS.md` y `docs/CUEVAS.md` |
| Lo que no funcionó | `docs/PREREGISTRO_*.md` |
| Cómo correrlo | `README.md` y `docs/DESPLIEGUE.md` |
