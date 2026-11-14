# Resumen del proyecto

**NASA Space Apps Challenge 2026 · reto "Permanent Moon Base Locations and Mars"**
Estado a 14 de noviembre de 2026. Es un prototipo en desarrollo, no una entrega final.

## 1. El reto en una línea
Usar datos abiertos de la Tierra, la Luna y Marte para **encontrar y caracterizar lugares de la Tierra que sirvan de análogo** de sitios de aterrizaje o de bases en la Luna y en Marte. Hay que explicar qué se parece, qué no y para qué serviría, y buscar más allá de los análogos ya conocidos (Atacama, Antártida, Islandia, Hawái). Detalles en [reto.md](reto.md).

## 2. Nuestra idea
Un **índice de similitud multidimensional**. Para cada sitio objetivo de la Luna o de Marte se calcula qué tan parecida es cada celda de la Tierra, **dimensión por dimensión**: terreno, térmica, agua/hielo y geología. Después:

1. Se **valida** el modelo con análogos que la NASA ya usa. Si salen bien rankeados, el modelo es creíble.
2. Se buscan los **candidatos nuevos**: celdas con buen puntaje que estén lejos de cualquier análogo conocido.
3. Cada candidato lleva una **ficha** con lo que se parece, lo que no, y los límites de la analogía (gravedad, vacío, radiación, atmósfera).

El puntaje por dimensión es `exp(-distancia)` sobre variables estandarizadas, y el global es una media ponderada. Los pesos los elige el usuario con sliders en la app. La idea de partida es de Mauxi ([ideas.md](ideas.md)); el plan completo está en [PLAN.md](PLAN.md).

## 3. Qué hay hecho

| Parte | Estado |
|---|---|
| Esqueleto Python (`src/analogos/`): similitud, validación, clustering (PCA + HDBSCAN), fichas, pipeline | Hecho; 29 tests pasan |
| App Streamlit: mapa, ranking, sliders de pesos, métricas, ficha | Hecha; cargó sin errores, **el mapa no se pudo comprobar visualmente** |
| Contrato de datos ([docs/features.md](docs/features.md)) | Hecho: 16 variables de topografía y 5 más de otras dimensiones |
| **Topografía de Luna y Marte** (pendiente, percentiles, rugosidad a 1, 2 y 5 km, TRI, TPI, curvaturas, orientación, parche llano) | **Datos reales** de 3 sitios lunares y 3 marcianos, leídos de los DEM del USGS (LOLA 118 m, MOLA 463 m). Elevaciones comprobadas contra puntos conocidos |
| Termal de la Tierra (prototipo con POWER) y búsqueda en CMR | Funciona, pero es temperatura del **aire**, no de superficie |
| Cliente de ODE (PDS Geosciences) para localizar productos de Luna y Marte | Funciona; solo devuelve enlaces, no valores |
| Listas de datos: sitios objetivo, análogos conocidos, aterrizajes conocidos | Hechas; coordenadas verificadas en parte (ver sección 5) |

## 4. Qué falta (y por qué los resultados aún no significan nada)
- **La Tierra no tiene datos reales de topografía ni de geología.** `data/features/earth.parquet` es **sintético**, así que el AUC (~0.5) es el de un modelo aleatorio.
- **Luna y Marte solo tienen topografía.** Faltan temperatura de superficie (Diviner, TES/THEMIS), agua/hielo (LEND, SHARAD, GRS) y minerales (M3, CRISM).
- **Termal de la Tierra:** hay que sustituir POWER (aire) por MODIS LST (superficie). Exige login gratuito de Earthdata.
- **`ice__water_frac`** de la Tierra es un proxy provisional de precipitación; no mide hielo en el suelo.
- **Una sola ventana de 50 × 50 km por sitio.** El perfil de cada sitio es una fila.
- **Faltan** la iluminación en los polos, los cráteres y los tubos de lava, que serían los que distinguen candidatos de base lunar.
- Los umbrales de 5° y 15° para las fracciones de pendiente están por confirmar con una fuente.

## 5. De dónde salen los datos (y cuánto fiarse)
Todo está registrado en [docs/FUENTES.md](docs/FUENTES.md).

- **Verificados contra una página abierta:** coordenadas de Apolo, Surveyor, Viking, Pathfinder, Spirit, Opportunity, Phoenix, Curiosity y otros, desde NSSDCA y el Mars Orbital Data Explorer ([docs/aterrizajes_conocidos.csv](docs/aterrizajes_conocidos.csv)).
- **Orientativos:** las coordenadas de los análogos terrestres y de casi todos los sitios objetivo vienen de Wikipedia, que no cita fuente primaria. Hay que sustituirlas por fuentes oficiales antes de citarlas.
- **No verificados:** Chandrayaan-3, SLIM, Zhurong, Oxia Planum y las regiones de Artemis III (NASA no publica sus coordenadas), entre otros. La analogía de Mauna Kea, Askja y Svalbard tampoco está comprobada.
- La búsqueda la hicieron agentes de IA; antes de citar un dato en la entrega hay que abrir su `source_url`.
- Las APIs de NASA y lo que se probó en vivo están en [docs/APIS.md](docs/APIS.md).

## 6. Cómo ejecutarlo (Windows PowerShell)

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e ".[app,dev]"
pip install --only-binary=:all: rasterio     # para leer los DEM (Luna y Marte)

python -m analogos.synthetic        # datos sintéticos (Tierra y objetivos)
python -m analogos.data.moon        # topografía real de la Luna
python -m analogos.data.mars        # topografía real de Marte
python -m analogos.pipeline         # scores, validación y clusters
streamlit run app/streamlit_app.py
pytest
```

Nota: con Python 3.14 el `pip install` completo se atascó resolviendo dependencias; funcionó instalando las ruedas precompiladas (`--only-binary=:all:`).

## 7. Mapa del repo

| Ruta | Qué hay |
|---|---|
| `src/analogos/` | `topography.py` (pendiente y rugosidad), `similarity.py`, `validate.py`, `cluster.py`, `report.py`, `pipeline.py`, `synthetic.py` |
| `src/analogos/data/` | `dem.py` (lectura remota de DEM), `moon.py`, `mars.py`, `earth.py` (POWER y CMR), `ode.py`, `http.py` |
| `app/streamlit_app.py` | la aplicación |
| `docs/` | contrato de datos, procedencia, APIs, CSV de sitios |
| `data/` | no se versiona: `features/`, `results/` y `raw/cache/` |
| `PLAN.md` | arquitectura, equipo de 6 personas y cronograma |

## 8. Siguientes pasos recomendados
1. **Topografía de la Tierra** con un DEM global (Copernicus de 90 m, porque NASADEM no cubre los polos), con el mismo `window_features`. Es lo que desbloquea la primera comparación real.
2. **Termal de superficie:** MODIS LST para la Tierra y Diviner para la Luna (necesita cuenta de Earthdata).
3. **Validación con datos reales:** fijar la lista de análogos conocidos con fuentes oficiales y medir AUC y recall.
4. Añadir **iluminación** para los sitios polares y **cráteres**.
5. Escribir el informe y las fichas para la entrega.
