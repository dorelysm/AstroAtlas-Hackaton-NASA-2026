# PLAN: Buscador de análogos terrestres para Luna y Marte

> Borrador para discutir con el equipo. Todo lo marcado con (?) es una decisión abierta.

## 1. Idea en una frase

Un **índice de similitud multidimensional** que compara cada celda de la Tierra con sitios objetivo de la Luna y de Marte, **dimensión por dimensión** (terreno, térmico, agua/hielo, geología, polvo/viento, subsuelo). Lo validamos con análogos que la NASA ya usa y destacamos los **análogos poco conocidos** que salen bien rankeados. Cada resultado trae una ficha: *qué se parece, qué no y para qué serviría*.

Esto cubre lo que pide el reto: combinar datasets, ir más allá de los sitios conocidos, explicar dónde falla la analogía y conectar con la exploración.

## 2. Alcance (MVP primero)

| | MVP (obligatorio) | Extra si hay tiempo |
|---|---|---|
| Objetivos Luna | 3 sitios: región polar sur (borde de Shackleton/Faustini), Malapert, un sitio de mares (tubo de lava, p. ej. Mare Tranquillitatis) (?) | más candidatos Artemis |
| Objetivos Marte | 3 sitios: Jezero, Oxia Planum, Utopia/Arcadia (hielo subsuperficial) (?) | Gale, Hellas, Mawrth |
| Resolución Tierra | malla global ~0.25° (o H3 res 4) | zoom a ~1 km en el top-N |
| Dimensiones | 4: topografía, térmica, hidrología/hielo, geología | + polvo/viento, + subsuelo (cuevas, tubos de lava) |
| Salida | mapa interactivo + ranking + fichas | similitud por proceso, "Mars vs Moon" comparado |

## 3. Metodología

1. **Perfil del sitio objetivo**: para cada sitio de Luna/Marte, un vector de features por dimensión (media, desviación, percentiles).
2. **Perfil de cada celda terrestre**: mismas features, mismas definiciones y mismas unidades.
3. **Similitud por dimensión** (0-1): distancia de Mahalanobis o Gower sobre features estandarizadas, convertida a score.
4. **Score global** = media ponderada de las dimensiones. Los pesos dependen del objetivo y los fija el usuario con sliders (p. ej. "quiero el análogo térmico del polo lunar").
5. **ML (descubrimiento)**: UMAP + HDBSCAN/k-means sobre el espacio de features para agrupar tipos de terreno y encontrar clusters que contengan celdas poco estudiadas.
6. **Validación**: lista de análogos conocidos (Atacama, Haughton, Devon Island, Mauna Kea, Askja, Lanzarote, Dry Valleys, Río Tinto, Svalbard, Craters of the Moon, Death Valley...). Métricas: ¿qué rank tienen?, recall@k, AUC. Si la lista queda arriba, el modelo es creíble.
7. **Hallazgos nuevos**: top-N que **no** estén a menos de X km de un análogo conocido. Para cada uno, ficha detallada.
8. **Límites** (explícitos en la UI): gravedad, vacío, radiación, atmósfera. No los modelamos, los mostramos como "dónde falla la analogía".

### Riesgos metodológicos a decidir temprano
- **Comparabilidad entre cuerpos**: las features deben ser independientes de la escala y del planeta (pendiente en grados, rugosidad a una base fija de ~100 m–1 km, amplitud térmica, fracción de iluminación). Hay que fijar esa lista en la primera hora.
- **Circularidad de la validación**: si el modelo se ajusta con los análogos conocidos, no se pueden usar también para validar. Se usan solo para validar.
- **Resoluciones distintas** (Diviner ~240 m vs MODIS 1 km): reproyectar todo a la malla común y documentar la pérdida de detalle.

## 4. Fuentes de datos (a confirmar acceso en el hito 0)

| Dimensión | Tierra | Luna | Marte |
|---|---|---|---|
| Topografía | Copernicus DEM / SRTM / ASTER GDEM | LRO LOLA (DEM) | MGS MOLA (DEM), HRSC |
| Térmica | MODIS LST (Earthdata), ERA5 | LRO Diviner | MGS TES, THEMIS |
| Agua/hielo | precipitación (GPM/IMERG), aridez, permafrost, hielo | LEND (hidrógeno), Mini-RF, Diviner (trampas frías) | SHARAD/MARSIS, GRS, THEMIS |
| Geología/minerales | ASTER (índices minerales), mapas litológicos (GLiM) | LROC, Clementine/M3, mapas USGS | CRISM, TES, mapas USGS |
| Polvo/viento | MERRA-2 (aerosoles, viento) | n/a (polvo lunar: proxy por rugosidad/insolación) | opacidad de polvo (MCS/THEMIS) |
| Subsuelo | inventario de cuevas/tubos de lava | GRAIL (anomalías de gravedad) | catálogos de cuevas/pits |
| Iluminación | radiación solar (ERA5/CERES) | LOLA + modelo de iluminación | MOLA + modelo |

Las agencias socias del reto (ESA Copernicus, JAXA G-Portal, CSA RADARSAT) sirven para SAR (rugosidad, humedad superficial, hielo) y para cubrir huecos de Earth data. Los datos de Marte no están en `recursos.md`: hay que agregar PDS Geosciences, USGS Astrogeology y Mars Orbital Data Explorer.

## 5. Arquitectura

```
Fuentes (APIs/PDS/Earthdata)
        │  download scripts (idempotentes, con caché)
        ▼
data/raw/{earth,moon,mars}/            # no se versiona (.gitignore)
        │  procesamiento por cuerpo
        ▼
data/processed/{earth,moon,mars}/      # rasters reproyectados
        │  agregación a malla común (H3 / lat-lon)
        ▼
data/features/{earth,moon,mars}.parquet   ◄── CONTRATO ENTRE EQUIPOS
        │
        ▼
modelo: similitud + clustering + validación
        │
        ▼
data/results/{scores.parquet, clusters.parquet, ficha_*.json}
        │
        ▼
app (Streamlit + pydeck/folium): mapa, ranking, ficha del sitio
```

### Contrato de datos (lo único que todos deben respetar)
`features/{cuerpo}.parquet` con columnas:
`cell_id, body, lat, lon, <dim>__<feature>...` p. ej. `topo__slope_mean_deg`, `topo__rough_1km`, `thermal__t_max_k`, `thermal__t_range_k`, `ice__water_frac`, `geo__basalt_frac`.
Todas con unidades en el nombre o en `docs/features.md`. NaN = sin dato (el modelo lo trata, no se imputa en silencio).

### Estructura del repo
```
HackatonNASA/
├── PLAN.md  reto.md  ideas.md  recursos.md
├── README.md                 # cómo instalar y correr
├── pyproject.toml            # o requirements.txt + .venv
├── docs/
│   ├── features.md           # definición de cada feature y unidad
│   ├── sitios_objetivo.md    # lista Luna/Marte con coordenadas
│   └── analogos_conocidos.md # lista de validación con fuentes
├── src/analogos/
│   ├── data/{earth,moon,mars}.py   # descarga + proceso por cuerpo
│   ├── grid.py                     # malla común y reproyección
│   ├── features.py                 # cálculo de features
│   ├── similarity.py               # score por dimensión + global
│   ├── cluster.py                  # UMAP + HDBSCAN
│   ├── validate.py                 # métricas vs. análogos conocidos
│   └── report.py                   # genera fichas
├── app/streamlit_app.py
├── notebooks/                      # exploración, no lógica
├── tests/
└── data/                           # ignorado en git
```

### Stack Python
- Datos: `earthaccess`, `rasterio`, `xarray`, `geopandas`, `h3`, `pds4_tools` / `planetaryimage`, `pandas` + `pyarrow`.
- Modelo: `scikit-learn`, `umap-learn`, `hdbscan`, `scipy`.
- App: `streamlit` + `pydeck` o `folium` (decidir en el hito 1, (?)).
- Calidad: `ruff`, `pytest` (mínimo para `similarity.py` y `validate.py`).

## 6. Equipo (6 personas)

| # | Rol | Responsable de | Entrega principal |
|---|---|---|---|
| 1 | **Líder / ciencia y narrativa** | lista de análogos conocidos, sitios objetivo, límites de la analogía, pitch y reporte | `docs/*`, ficha-plantilla, presentación |
| 2 | **Datos Tierra** | descarga/proceso de Earth data | `features/earth.parquet` |
| 3 | **Datos Luna** | LOLA, Diviner, LEND, LROC | `features/moon.parquet` |
| 4 | **Datos Marte** | MOLA, THEMIS/TES, CRISM, SHARAD | `features/mars.parquet` |
| 5 | **Modelo / ML** (Mauxi) | similitud, clustering, validación, pesos | `scores.parquet`, métricas |
| 6 | **App / visualización** | mapa, ranking, ficha, sliders de pesos | `app/` desplegada |

Reglas: el 5 y el 6 arrancan desde el hito 1 con **datos sintéticos** que respeten el contrato, para no esperar a las descargas. Las personas 2-4 se apoyan entre sí en la parte de malla y reproyección (`grid.py`).

## 7. Cronograma

No conozco las fechas exactas; lo escribo en bloques relativos. Space Apps suele ser un hackatón de ~48 h, así que conviene adelantar el hito 0 **antes** del evento.

| Hito | Cuándo | Qué | Criterio de listo |
|---|---|---|---|
| **0. Preparación** | antes del evento | crear repo git, entorno Python compartido, probar acceso a Earthdata (cuenta), PDS, Copernicus; fijar lista de features v0, sitios objetivo y análogos conocidos | todos corren `make setup`; contrato de datos acordado |
| **1. Esqueleto** | horas 0-6 | malla común, 1 feature por dimensión por cuerpo, datos sintéticos, app con mapa vacío | pipeline de punta a punta con datos falsos |
| **2. Datos reales (MVP)** | horas 6-20 | 4 dimensiones reales en los 3 cuerpos; similitud por dimensión | `features/*.parquet` reales; ranking que no revienta |
| **3. Validación y ML** | horas 18-32 | métricas contra análogos conocidos, ajuste de features/pesos, clustering, primeros hallazgos nuevos | recall@k reportado; ≥5 candidatos novedosos |
| **4. Fichas y app** | horas 28-40 | fichas "similar / diferente / uso", sliders, comparación Luna vs Marte | demo navegable |
| **5. Pulido y entrega** | horas 40-48 | reporte escrito, video/pitch, README, despliegue, prueba de la demo en limpio | entregado con holgura |

**Congelar funcionalidades en la hora ~36.** Después solo arreglos y presentación.

## 8. Riesgos y mitigaciones

| Riesgo | Mitigación |
|---|---|
| Descargas grandes y lentas (DEM global, Diviner) | trabajar a baja resolución primero; descargar versiones agregadas/mosaicos; cachear; empezar en el hito 0 |
| Cuentas/credenciales (Earthdata) | crearlas antes; cada uno usa su propio token, nunca en el repo (`.env` ignorado) |
| Features no comparables entre cuerpos | definirlas en `docs/features.md` en el hito 0 y revisarlas con el líder |
| Validación débil o circular | lista de análogos conocidos fijada antes de ajustar el modelo |
| Integración tardía | contrato parquet + datos sintéticos desde el inicio; integrar cada ~6 h |
| Demasiado alcance | MVP definido arriba; las extras solo después del hito 3 |

## 9. Decisiones abiertas (?)

1. Lista final de sitios objetivo de Luna y Marte (propuesta en la sección 2).
2. Malla: lat-lon 0.25° o H3.
3. Streamlit vs. alternativa para la app y dónde se despliega.
4. Fecha y duración real del evento, para ajustar el cronograma.
5. Si se incluye SAR (RADARSAT/Sentinel-1) en el MVP o queda como extra.
