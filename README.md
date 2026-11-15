# Análogos terrestres para la Luna y Marte

NASA Space Apps 2026 · reto *Permanent Moon Base Locations and Mars*.
Ranking de lugares de la Tierra por similitud multidimensional con sitios de la Luna y Marte (topografía, térmica, hielo/agua, geología), validado contra análogos terrestres conocidos.

**Empieza por el [resumen del proyecto](RESUMEN.md).**

Documentos: [reto](reto.md) · [ideas](ideas.md) · [recursos](recursos.md) · **[plan](PLAN.md)** · [plan de la Tierra](docs/PLAN_TIERRA.md) · [features](docs/features.md) · [procedencia de los datos](docs/FUENTES.md) · [APIs de NASA](docs/APIS.md) · [ablación por dimensión](docs/ABLACION.md) · [validación](docs/VALIDACION.md) · [validación por aspecto](docs/VALIDACION_ASPECTO.md)

## Cómo funciona

- **Score por dimensión** = exp(−distancia z cuadrática media) entre el perfil del sitio lunar/marciano y cada celda de la Tierra (la topografía se comprime con PCA blanqueada). **Score global** = media ponderada de las dimensiones disponibles.
- **Datos reales** (ventana de 50 km, base común de 500 m): Luna (LOLA, Diviner, LP-GRS), Marte (MOLA, Odyssey GRS; térmica vacía por decisión), Tierra (Copernicus GLO-90, MODIS LST y nieve, GLiM litología). Detalle y licencias en [docs/FUENTES.md](docs/FUENTES.md).
- **Validación**: los análogos conocidos solo validan, nunca ajustan el modelo. Métricas: AUC y recall con bootstrap sobre los análogos.
- **Viabilidad**: cada celda de la Tierra lleva la marca `viable` (falso si hay un asentamiento de ≥ 1 000 hab. a < 50 km, NASA SEDAC GRUMP). Es una marca, no entra en el score ni en la validación.

## Estado de los resultados

La validación está cerca del azar (35 objetivos: AUC por sitios 0,58, recall 0,17). Limitaciones conocidas: pocos análogos, confusión con terreno llano de cratón, hielo/térmica no comparables entre cuerpos, geología de Marte saturada. Ver [validación](docs/VALIDACION.md), [ablación](docs/ABLACION.md) y [por aspecto](docs/VALIDACION_ASPECTO.md). No presentar el ranking como predictivo.

## Instalación (Windows PowerShell)

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e ".[app,dev]"        # núcleo + app + tests
pip install -e ".[data]"           # solo para regenerar datos: librerías geoespaciales y de descarga
# copia .env.example a .env y pon tus credenciales de Earthdata
```

## Uso

```powershell
python -m analogos.pipeline          # scores, validación, candidatos (candidates_viable.csv) y clusters en data/results/
streamlit run app/streamlit_app.py   # mapa, ranking, pesos, filtro de viabilidad y ficha
pytest                               # 125 tests
```

`data/` no se versiona: hay que generar las features con los módulos de abajo (o `python -m analogos.synthetic` para datos de prueba sin valor científico).

### Regenerar los datos

Cada módulo descarga, reduce y borra el archivo bruto.

```powershell
python -m analogos.data.moon
python -m analogos.data.mars
python -m analogos.data.earth            # topografía Copernicus
python -m analogos.data.earth_water      # nieve MODIS
python -m analogos.data.earth_thermal    # temperatura MODIS LST
python -m analogos.data.earth_geology    # GLiM
python -m analogos.data.usgs_analogs     # capa de análogos del USGS
python -m analogos.data.settlements      # viabilidad por población (GRUMP)
python -m analogos.ablation              # ablación por dimensión
python -m analogos.aspect                # validación por aspecto
```

## Estructura

| Ruta | Qué hay |
|---|---|
| `src/analogos/data/` | descarga y features por cuerpo (Copernicus, MODIS, GLiM, LOLA, MOLA, PDS/ODE, GRUMP, USGS) |
| `src/analogos/topography.py`, `grid.py`, `features.py` | variables de topografía por ventana y contrato de features |
| `src/analogos/similarity.py` | score por dimensión y global |
| `src/analogos/validate.py` | AUC / recall contra análogos conocidos, candidatos nuevos (con filtro de viabilidad) |
| `src/analogos/{ablation,aspect,aspect_usgs}.py` | ablación y validación por aspecto |
| `src/analogos/pipeline.py` | features → scores → validación → resultados |
| `src/analogos/cluster.py`, `report.py` | PCA + HDBSCAN; fichas "similar / distinto / límites" |
| `src/analogos/synthetic.py` | datos falsos que respetan el contrato |
| `app/streamlit_app.py` | app |
| `docs/` | documentación y CSV de sitios objetivo, aterrizajes y análogos conocidos |
| `tests/` | pruebas |

## Reglas del equipo

- El **contrato** es `data/features/{body}.parquet` (ver `docs/features.md`). Quien añada una feature la declara en `config.py` y en la doc.
- `data/` y `.env` no se versionan; una sola rama, `main`.
- Los análogos conocidos solo validan; no se usan para ajustar el modelo. Etiquetas y protocolos se fijan antes de medir; las correcciones posteriores se reportan aparte.
- Todo dato nuevo se registra en `docs/FUENTES.md` (origen, URL, licencia, nivel de confianza).
- Los datos sintéticos no tienen valor científico.
