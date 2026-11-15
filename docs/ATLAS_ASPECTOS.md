# Atlas por aspecto (15 nov 2026)

El reto dice que un lugar puede ser un excelente análogo geológico y uno pobre en temperatura. Un ranking global mezcla todo, así que aquí **cada aspecto se evalúa por separado** y lleva una **etiqueta de confianza que sale de resultados ya medidos**, no de una opinión.
Código: `src/analogos/atlas.py` (`python -m analogos.atlas`). Puntaje de una celda = media, sobre los objetivos del cuerpo con dato en ese aspecto, de su similitud **solo en esa dimensión**. Solo celdas viables y sin vegetación; regiones separadas ≥ 500 km; no se lista nada por debajo de 0,10 de parecido.

## Confianza por aspecto y por qué
| Cuerpo | Aspecto | Confianza | Resultado medido que la justifica |
|---|---|---|---|
| Luna | Topografía | baja | Capa del USGS con control por terreno llano: AUC 0,48. Por análogos etiquetados, +0,14 con intervalo que incluye el cero ([PREREGISTRO_LLANURA.md](PREREGISTRO_LLANURA.md)) |
| Marte | Topografía | baja | La ventaja inicial (0,567) desaparece al controlar la planitud (0,494). Por análogos, +0,15, no concluyente |
| Luna | Geología | **media** | Dirección correcta (+0,64) con 1 a 3 análogos por grupo; p mínimo alcanzable 0,25. El proxy lunar (FeO) y la roca basáltica terrestre no miden lo mismo |
| Marte | Geología | **media** | Dirección correcta (+0,97) con un solo análogo (Craters of the Moon); la geología de Marte satura |
| Luna | Térmica | muy baja | En contra (−0,48), una sola referencia polar; la térmica terrestre son medias mensuales. **Ninguna celda supera 0,10 de parecido: no se recomienda nada** |
| Marte | Térmica | sin datos | Marte no tiene térmica en el modelo |
| Luna | Hielo | muy baja | Solo 2 objetivos polares tienen dato; ningún análogo lleva la etiqueta: no evaluable |
| Marte | Hielo | muy baja | Falla en los Valles Secos (−0,75): la nieve no mide sequedad; la humedad del suelo no mejora ([PREREGISTRO_HIELO.md](PREREGISTRO_HIELO.md)) |

Ningún aspecto llega a "alta": con 4 a 8 análogos por cuerpo ninguno se puede validar de forma concluyente. La etiqueta "media" de la geología es la más alta que los datos permiten.

## Mejores regiones por aspecto (de `data/results/atlas_regiones.csv`)
- **Geología, Marte (media):** 27.5° N 17.5° E (Haruj), 32.5° N 37.5° E (Harrat ash-Shamah) y dos celdas antárticas (−77.5°, 167.5° E y −77.5°, 127.5° O), todas con 0,85. **Ojo con las antárticas:** GLiM da la roca subglaciar, no la superficie visible; son un artefacto de la fuente. Las dos primeras son las candidatas de [FICHAS_CANDIDATOS.md](FICHAS_CANDIDATOS.md).
- **Geología, Luna (media):** las mismas celdas, con puntaje bajo (0,23): el basalto terrestre no se parece mucho al perfil de FeO lunar.
- **Topografía, Marte (baja):** 32.5° N 37.5° E, 37.5° N 92.5° E (cuenca de Qaidam), 17.5° N 52.5° E, 22.5° N 22.5° E y 22.5° N 17.5° E, todas ≈ 0,53: terreno llano de desierto.
- **Topografía, Luna (baja):** puntajes ≈ 0,43; entre ellas hay hielo polar llano.
- **Hielo, Marte (muy baja):** 42.5° N 102.5° E (Gobi), 37.5° N 117.5° O (cerca de Death Valley), Atacama y desiertos de Asia central, con 0,93 a 0,97. Son desiertos sin nieve: lo que mide es "no hay nieve", no hielo subsuperficial.
- **Hielo, Luna (muy baja):** celdas árticas, una de ellas a 327 km de Haughton, el único análogo polar conocido.

## Cómo usarlo
Como una guía de **qué aspecto se parece dónde**, no como una lista de análogos recomendados. La app lo muestra en la sección «Atlas por aspecto», con la confianza al lado de cada tabla.
