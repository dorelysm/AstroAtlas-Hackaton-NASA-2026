# Interfaz de la app (AstroAtlas)

La app se adaptó a la propuesta de diseño **«AstroAtlas — Propuesta de interfaz»** (archivo de Figma compartido por el equipo). **Solo cambia cómo se muestran los resultados: el modelo, los datos y las cifras de validación no cambian.** Código: `app/streamlit_app.py`; textos y reglas de presentación: `src/analogos/presentacion.py`; nombres de lugar: `src/analogos/lugares.py`; tema: `.streamlit/config.toml`.

## Qué se aplicó de la propuesta
| Propuesta | En la app |
|---|---|
| 1 · Nombres claros | `topo`, `thermal`, `ice`, `geo` se muestran como **Relieve, Temperatura, Hielo o agua, Geología**, cada uno con una frase que lo explica. Los pesos pasan a **«No importa / Importa poco / Importa algo / Importa mucho»** (pesos 0, 0,33, 0,66 y 1 en el modelo) |
| 2 · Lugares con nombre | En vez de `earth_24_43` se muestra el **lugar y el país** (por ejemplo «Harrat ash-Shamah, Siria / Jordania»). Los nombres salen de Natural Earth 1:110m (dominio público) con dos nombres propios curados (Harrat ash-Shamah y Haruj); no hay servicios externos. Al pasar el cursor sobre el mapa se ve el nombre y el parecido |
| 3 · Guía de 3 pasos | Tres tarjetas arriba: elige un sitio, mira el mapa, lee la ficha |
| 4 · Métricas explicadas | Un aviso «Son pistas, no certezas» con el acierto del método (≈ 58 % en la Luna, ≈ 60 % en Marte; 50 % = adivinar) y un panel «¿Qué tan confiable es para …?» con etiqueta de confianza. El AUC y el recall quedan en «Detalles técnicos y validación» |
| 5 · Datos que faltan | Si un aspecto no tiene dato (p. ej. la temperatura de Marte) la tarjeta dice «Sin dato / No se pudo comparar» y explica por qué; la ficha dice «Calculado con N de 4 aspectos» |
| 6 · Parecido en porcentaje | La nota de 0 a 1 se muestra como porcentaje (0,82 → 82 %), con la etiqueta «Muy parecido / Parecido medio / Poco parecido» por aspecto |

Además: la tabla «Los más parecidos» (con el puesto en la lista completa), la ficha con un texto por aspecto y «Lo que la Tierra no puede imitar» como etiquetas. Los desplegables de candidatos, atlas por aspecto, casos de uso (incluido el caso frío con el mapa de permafrost) y créditos siguen debajo.

## De dónde salen las cifras de confiabilidad
Son constantes de `presentacion.py` (`CONFIABILIDAD`) tomadas de la validación con los tres conjuntos de análogos juntos ([PREREGISTRO_VALIDACION3.md](PREREGISTRO_VALIDACION3.md), descriptivo): **Luna 58 % (entre 55 % y 62 %; 20 análogos) y Marte 60 % (entre 52 % y 67 %; 40 análogos)**. Si cambia la validación hay que actualizarlas a mano; una prueba comprueba que sean coherentes (el valor dentro de su intervalo y por encima del 50 %). La maqueta usaba 60 % y 56 % de versiones anteriores.

## Diferencias respecto de la maqueta
- Las explicaciones por aspecto salen de los datos de cada celda (por ejemplo, «algo más llano que en Jezero» o «más rugoso» según la pendiente), así que pueden diferir de las frases de ejemplo de la maqueta.
- Los nombres de lugar son los de Natural Earth a escala 1:110m, más gruesos que los de la maqueta: muchas celdas del Sáhara salen como «Sahara (Sudán)» en vez de «Costa del mar Rojo» o «Desierto Oriental»; las que caen en zonas sin región nombrada salen como «Zona de <país>». Añadir nombres propios más finos es un cambio pequeño (`NOMBRES_CURADOS`).
- **Colores:** se sacaron de la maqueta (muestreando la imagen) y están en `.streamlit/config.toml`: fondo `#0E1117`, barra lateral `#161A23`, superficies `#1B2030`, borde `#242A3B`, acento naranja `#FF8C42`, ámbar `#FBBF24` (parecido medio, confianza baja), verde `#34D399` (muy parecido) y azul `#4C8DF6` (análogos conocidos y límites). Se usó el tema oscuro nativo de Streamlit, sin CSS propio.
- **Lo que Streamlit no permite sin CSS:** las tarjetas de la maqueta tienen relleno `#1B2030` y aquí son solo un recuadro con borde; las barras de progreso son todas del color de acento (naranja) en vez de ámbar o verde según el nivel; y en la maqueta los controles de la barra lateral salen rojos porque son los de Streamlit por defecto, mientras que aquí son naranjas para ir con el acento. Cambiar a rojo es una línea (`primaryColor = "#FF4B4B"`).
- El filtro «Solo lugares nuevos» y los de pueblos y vegetación se mantienen; «Lugares a mostrar» pasó a «Opciones avanzadas».
