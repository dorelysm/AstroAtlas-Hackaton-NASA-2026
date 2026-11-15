# Resumen del proyecto

**NASA Space Apps Challenge 2026 · reto "Permanent Moon Base Locations and Mars"**
Estado a 15 de noviembre de 2026. Prototipo con datos reales; la validación sale **cerca del azar** y así debe presentarse.

## 1. El reto en una línea
Usar datos abiertos de la Tierra, la Luna y Marte para **encontrar y caracterizar lugares de la Tierra que sirvan de análogo** de sitios de aterrizaje o de bases en la Luna y en Marte, explicando qué se parece, qué no y para qué serviría. Detalles en [reto.md](reto.md).

## 2. Nuestra idea
Un **índice de similitud multidimensional**. Para cada sitio objetivo (21 lunares y 14 marcianos) se calcula qué tan parecida es cada celda de la Tierra, **dimensión por dimensión**: topografía, térmica, agua/hielo y geología.

- Puntaje por dimensión = `exp(-RMS de la distancia z)`; la topografía (16 variables) se comprime con PCA blanqueada. Puntaje global = media ponderada de las dimensiones disponibles (las vacías se ignoran). Los pesos se eligen en la app.
- Se **valida** con análogos terrestres conocidos, que solo validan y nunca ajustan el modelo. Métrica: u = P(análogo > celda típica), 0,5 = azar, con bootstrap sobre los análogos.
- Se buscan **candidatos nuevos** lejos de los análogos conocidos, con ficha (qué se parece, qué no, límites).
- Cada celda lleva la marca **`viable`**: falso si hay un asentamiento de ≥ 1 000 hab. a menos de 50 km (NASA SEDAC GRUMP). Es una marca, no entra en el score ni en la validación.

## 3. Qué hay hecho

| Parte | Estado |
|---|---|
| Datos reales de la **Luna** | Topografía (LOLA), térmica (Diviner), hielo (LP-GRS); 21 sitios con coordenadas de las tablas LROC |
| Datos reales de **Marte** | Topografía (MOLA), hielo (Odyssey GRS), geología; **térmica vacía por decisión** (no hay un mapa comparable) |
| Datos reales de la **Tierra** | Topografía Copernicus GLO-90, térmica MODIS LST, nieve MODIS, geología GLiM (CC-BY, excepción aprobada por el equipo), asentamientos GRUMP. ASTER GED probado y rechazado |
| Pipeline y app | Features → scores → validación → resultados; app Streamlit con mapa, pesos y filtro de viabilidad; 125 tests |
| Ablación por dimensión y validación por aspecto | Hechas, con etiquetas y protocolos fijados antes de medir (hash registrado) |
| Marcas de contexto | `viable` (población) y `vegetated` (NDVI MODIS); no entran al score |
| Informe | [docs/INFORME.md](docs/INFORME.md): el relato del proyecto con sus resultados negativos |
| Polvo y viento | Solo contexto descriptivo (MERRA-2) en las fichas; sin contraparte en Marte no se puntúan |
| Paquete reducido `demo_data/` | La app corre sin descargar nada |
| Fichas de candidatos | 2 de Marte (campos basálticos de Harrat ash-Shamah y Haruj) y 2 de la Luna (Antártida, valoradas como pobres): [FICHAS_CANDIDATOS.md](docs/FICHAS_CANDIDATOS.md) |
| Capa de análogos del USGS | Cráteres y dunas frente a 200 controles aleatorios |

## 4. Resultados (todos negativos o débiles)
- **Validación global:** 35 objetivos, AUC por sitios 0,58 y recall 0,17; AUC por celdas 0,50. Casi azar. Detalle en [VALIDACION.md](docs/VALIDACION.md) y [ABLACION.md](docs/ABLACION.md).
- **Por aspecto** ([VALIDACION_ASPECTO.md](docs/VALIDACION_ASPECTO.md)): la geología va en la dirección correcta pero con 1 a 3 análogos por grupo; el hielo de Marte falla donde debía acertar (Valles Secos, −0,75) porque la nieve de la Tierra no mide sequedad; la geología de Marte se satura y no ayuda.
- **Hielo, variable alternativa** ([PREREGISTRO_HIELO.md](docs/PREREGISTRO_HIELO.md)): la humedad del suelo (GLDAS) no mejora (Marte 0,493 → 0,469), se mantiene la nieve.
- **Terreno llano** ([PREREGISTRO_LLANURA.md](docs/PREREGISTRO_LLANURA.md)): con control por pendiente, la señal de los cráteres en Marte desaparece (0,567 → 0,494). Era un efecto de planitud, no de forma de cráter.
- **Análogos nuevos** ([BUSQUEDA_ANALOGOS.md](docs/BUSQUEDA_ANALOGOS.md)): la búsqueda no encontró ninguno evaluable para térmica ni hielo.
- **Viabilidad:** 708 de 951 celdas viables. Cinco de los diez análogos conocidos quedarían inviables (Mauna Kea, Lanzarote, Río Tinto, Svalbard, Craters of the Moon), por eso la marca no se aplica a la validación.

## 5. Límites que hay que decir en la entrega
- **Candidatos:** son hipótesis; las dos de la Luna salen solo por topografía (el resto sin dato) y no son buenos análogos. El filtro de vegetación se añadió tras ver que las primeras candidatas de Marte eran selvas.
- **Verificación de coordenadas parcial:** ver [VERIFICACION_COORDENADAS.md](docs/VERIFICACION_COORDENADAS.md) (p. ej. Oxia Planum difiere ~19 km del valor del IAU). Licencias por comprobar: [LICENCIAS.md](docs/LICENCIAS.md).
- **Sin cubrir:** iluminación polar; polvo, viento y cuevas solo como contexto ([CUEVAS.md](docs/CUEVAS.md): pits lunares y 1 062 candidatas de Marte integrados, pero ningún objetivo está cerca de una cueva) ([DIMENSIONES_NO_MODELADAS.md](docs/DIMENSIONES_NO_MODELADAS.md)).
- **Pocos análogos** (4 a 8 por cuerpo): los intervalos son anchos y ninguna dimensión puede quedar validada de forma concluyente.
- **Semántica distinta entre cuerpos:** el hielo y la térmica de la Tierra no significan lo mismo que en la Luna o Marte; ningún lugar de la Tierra reproduce los cambios de temperatura diarios de Marte.
- **Confusión con terreno llano y estable** (cratones), que ayuda a los análogos sin ser el aspecto buscado.
- **Viabilidad:** GRUMP es de 1990-2010, le faltan pueblos pequeños (San Pedro de Atacama) y estaciones antárticas.
- **Coordenadas:** las de los análogos y casi todos los sitios objetivo vienen de Wikipedia o de las tablas LROC; las analogías de Mauna Kea, Askja y Svalbard no están comprobadas. Todo en [docs/FUENTES.md](docs/FUENTES.md); abrir el `source_url` antes de citar.
- **No presentar el ranking como predictivo:** lo defendible es el método, los preregistros y los resultados negativos.

## 6. Cómo ejecutarlo (Windows PowerShell)

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e ".[app,dev]"
pip install -e ".[data]"          # solo para regenerar datos; con Python 3.14 usar --only-binary=:all:
# copia .env.example a .env con tus credenciales de Earthdata

python -m analogos.pipeline         # scores, validación, candidatos y clusters
streamlit run app/streamlit_app.py
pytest                              # 152 tests
```

`data/` no se versiona. Los módulos para regenerar los datos están en el [README](README.md).

## 7. Mapa del repo

| Ruta | Qué hay |
|---|---|
| `src/analogos/` | `similarity`, `validate`, `pipeline`, `ablation`, `aspect`, `aspect_usgs`, `topography`, `cluster`, `report` |
| `src/analogos/data/` | descarga y features por fuente (Copernicus, MODIS, GLiM, LOLA, MOLA, ODE, GRUMP, USGS) |
| `app/streamlit_app.py` | la aplicación |
| `docs/` | contrato de datos, procedencia, APIs, ablación, validaciones, preregistros y CSV de sitios |
| `PLAN.md` | arquitectura, equipo de 6 personas y cronograma |

## 8. Siguientes pasos posibles
1. **Más análogos con fuente:** leer bibliografía completa (no solo búsquedas) y fijar antes de medir qué objetivos son relevantes para cada aspecto (p. ej. térmica lunar solo en los polares).
2. **Marte, térmica:** dejarla vacía y decirlo, o buscar otra fuente si el equipo la quiere.
3. **Viabilidad:** complementar GRUMP con densidad de población (GPWv4) o luces nocturnas.
4. **Entrega:** escribir el informe y las fichas centrados en el método y en los límites; comprobar visualmente el mapa de la app.
