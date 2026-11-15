# Análogos terrestres para la Luna y Marte

NASA Space Apps 2026 · reto *Permanent Moon Base Locations and Mars*.
Índice de similitud multidimensional entre la Tierra y sitios de la Luna/Marte, validado contra análogos conocidos.

**Empieza por el [resumen del proyecto](RESUMEN.md).**

Documentos: [reto](reto.md) · [ideas](ideas.md) · [recursos](recursos.md) · **[plan](PLAN.md)** · [features](docs/features.md) · [procedencia de los datos](docs/FUENTES.md) · [APIs de NASA](docs/APIS.md) · [ablación por dimensión](docs/ABLACION.md) · [validación por aspecto](docs/VALIDACION_ASPECTO.md) · [validación](docs/VALIDACION.md)

## Instalación (Windows PowerShell)

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e ".[app,dev]"        # núcleo + app + tests
# pip install -e ".[data]"         # persona 2-4: librerías geoespaciales/descarga
# copia .env.example a .env y pon tus credenciales de Earthdata
```

## Uso

```powershell
python -m analogos.synthetic       # genera datos de prueba en data/features/
python -m analogos.pipeline        # scores, validación y clusters en data/results/
streamlit run app/streamlit_app.py
pytest
```

## Estructura

| Ruta | Qué hay |
|---|---|
| `src/analogos/data/{earth,moon,mars}.py` | descarga y features por cuerpo (**por implementar**) |
| `src/analogos/similarity.py` | score por dimensión y global |
| `src/analogos/validate.py` | AUC / recall contra análogos conocidos, candidatos nuevos |
| `src/analogos/cluster.py` | PCA + HDBSCAN (UMAP opcional) |
| `src/analogos/report.py` | fichas "similar / distinto / límites" |
| `src/analogos/synthetic.py` | datos falsos que respetan el contrato |
| `app/streamlit_app.py` | mapa, ranking, sliders de pesos, ficha |
| `docs/` | contrato de features, sitios objetivo y análogos conocidos (CSV) |

## Reglas del equipo

- El **contrato** es `data/features/{body}.parquet` (ver `docs/features.md`). Quien añada una feature la declara en `config.py` y en la doc.
- `data/` y `.env` no se versionan.
- Los análogos conocidos solo validan; no se usan para ajustar el modelo.
- Todo dato nuevo se registra en `docs/FUENTES.md` (origen, URL, nivel de confianza).
- Los datos sintéticos no tienen valor científico: sustitúyelos en cuanto haya datos reales.
