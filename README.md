# Análogos terrestres para la Luna y Marte

NASA Space Apps 2026 · reto *Permanent Moon Base Locations and Mars*.
Ranking de lugares de la Tierra por similitud multidimensional con sitios de la Luna y Marte (topografía, térmica, hielo/agua, geología), validado contra análogos terrestres conocidos.

**App en línea: https://app-production-6cc653bd.up.railway.app** · **Empieza por el [resumen del proyecto](RESUMEN.md) ([PDF](RESUMEN.pdf)).**

Documentos: [reto](reto.md) · [ideas](ideas.md) · [recursos](recursos.md) · **[plan](PLAN.md)** · [plan de la Tierra](docs/PLAN_TIERRA.md) · [features](docs/features.md) · [procedencia de los datos](docs/FUENTES.md) · [APIs de NASA](docs/APIS.md) · [ablación por dimensión](docs/ABLACION.md) · [validación](docs/VALIDACION.md) · [validación por aspecto](docs/VALIDACION_ASPECTO.md) · **[informe](docs/INFORME.md)** · **[fichas de candidatos](docs/FICHAS_CANDIDATOS.md)** · [licencias](docs/LICENCIAS.md) · [coordenadas verificadas](docs/VERIFICACION_COORDENADAS.md) · [dimensiones no modeladas](docs/DIMENSIONES_NO_MODELADAS.md) · [cuevas y tubos de lava](docs/CUEVAS.md) · [despliegue en Railway](docs/DESPLIEGUE.md) · [casos de uso](docs/CASOS_DE_USO.md) · [atlas por aspecto](docs/ATLAS_ASPECTOS.md) · [procesos](docs/PROCESOS.md) · [validación ampliada](docs/VALIDACION_AMPLIADA.md) · [estabilidad](docs/ESTABILIDAD.md) · [multiescala](docs/PREREGISTRO_MULTIESCALA.md) · [variabilidad](docs/PREREGISTRO_VARIABILIDAD.md) · [grupos](docs/PREREGISTRO_GRUPOS.md) · [modelos](docs/PREREGISTRO_MODELOS.md) · [hielo polar](docs/PREREGISTRO_HIELO_POLAR.md)

## Cómo funciona

- **Score por dimensión** = exp(−distancia z cuadrática media) entre el perfil del sitio lunar/marciano y cada celda de la Tierra (la topografía se comprime con PCA blanqueada). **Score global** = media ponderada de las dimensiones disponibles.
- **Datos reales** (ventana de 50 km, base común de 500 m): Luna (LOLA, Diviner, LP-GRS), Marte (MOLA, Odyssey GRS; térmica vacía por decisión), Tierra (Copernicus GLO-90, MODIS LST y nieve, GLiM litología). Detalle y licencias en [docs/FUENTES.md](docs/FUENTES.md).
- **Validación**: los análogos conocidos solo validan, nunca ajustan el modelo. Métricas: AUC y recall con bootstrap sobre los análogos.
- **Marcas de contexto** (no entran al score ni a la validación): `viable` (≥ 1 000 hab. a < 50 km, SEDAC GRUMP) y `vegetated` (NDVI máx. ≥ 0,2, MODIS MOD13C2). Evitan, por ejemplo, proponer selvas como análogos de Marte.
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
pytest                               # 180 tests
```

**Sin descargar nada:** si no existe `data/features/`, la app y el pipeline usan `demo_data/` (≈ 0,6 MB, valores derivados ya calculados). Con datos propios, estos tienen prioridad.

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
python -m analogos.data.earth_vegetation # marca de vegetación (MODIS NDVI)
python -m analogos.data.earth_dust_wind  # polvo y viento, solo contexto (MERRA-2)
python -m analogos.data.caves            # pits lunares como contexto (Zenodo, CC BY 4.0)
python -m analogos.fichas                # selección de candidatos para las fichas
python -m analogos.validation_ext --build   # características de los análogos nuevos (descarga MODIS)
python -m analogos.validation_ext           # validación con 23 análogos (modelo congelado)
python -m analogos.validation2 --build      # características del segundo conjunto independiente (9 sitios; descarga MODIS)
python -m analogos.validation2              # evalúa V1 (modelo base), V2 (unión A o B) y V3 (permafrost) en ese conjunto
python -m analogos.hielo_somero --build     # características de los 8 objetivos de hielo somero (MOLA)
python -m analogos.hielo_somero             # P1/P2: permafrost con análogos fríos frente a objetivos con hielo publicado
python -m analogos.frio                     # permafrost sin capas de hielo: Q1/Q2/Q3 y candidatas frías
python -m analogos.validation3 --build      # características del tercer conjunto (13 sitios del catálogo CAFE de la ESA)
python -m analogos.validation3              # evalúa V1/V2 en ese conjunto
python -m analogos.lugares --build              # nombres de lugar y país en español e inglés (desde Natural Earth; ver docs/INTERFAZ.md)
python -m analogos.permafrost_mapa          # clase de permafrost con el mapa de Obu et al. 2018 (necesita data/raw/permafrost/UiO_PEX_25km.nc); añade el caso frío a usecases.csv
python -m analogos.inertia                  # experimento de inercia térmica (no adoptado)
python -m analogos.emissivity --phase1      # experimento de emisividad (fase 1, descartado)
python -m analogos.multiscale                # experimento: topografía a varias escalas (no adoptado)
python -m analogos.variability --build      # experimento: ventanas adicionales por objetivo (red)
python -m analogos.variability              # experimento: calibración con la variabilidad (no adoptado)
python -m analogos.grupos                   # experimento: grupos frío y cálido (no adoptado)
python -m analogos.modelos                  # modelo Tierra-Tierra y consenso (no adoptados)
python -m analogos.polar_ice                # hielo polar de Marte con neutrones de Odyssey (descarga ~33 MB)
python -m analogos.permafrost               # variable de permafrost (no adoptada)
python -m analogos.stability                # estabilidad de las predicciones
python -m analogos.atlas                # atlas por aspecto con confianza
python -m analogos.usecases             # recomendaciones por caso de uso
python -m analogos.zoom --name harrat --lat 29 36 --lon 34 42   # zoom topográfico a 0.25° sobre una región
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
