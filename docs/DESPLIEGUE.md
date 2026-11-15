# Despliegue de la app en Railway

La app (`app/streamlit_app.py`) corre sin descargar nada: si no existe `data/features/`, lee `demo_data/` (≈ 0,7 MB, versionado).

## Archivos de despliegue (en la raíz del repo)
| Archivo | Para qué |
|---|---|
| `requirements.txt` | solo las dependencias de la app (numpy, pandas, pyarrow, scipy, scikit-learn, streamlit, pydeck) |
| `railway.json` | comando de arranque, comprobación de salud (`/_stcore/health`) y reinicios |
| `.python-version` | Python 3.12 (hay ruedas precompiladas de todas las dependencias) |
| `.streamlit/config.toml` | modo headless, sin telemetría, tema oscuro |

## Estado (15 nov 2026)
**Desplegada** en Railway (proyecto `astroatlas-nasa`, servicio `app`, rama `main`): https://app-production-6cc653bd.up.railway.app. La compilación terminó con éxito, la ruta `/_stcore/health` responde 200 y la app se abrió y se revisó en el navegador. Cada push a `main` la redespliega.

## Pasos en Railway (para repetirlo en otra cuenta)
1. *New Project → Deploy from GitHub repo* y elegir `dorelysm/AstroAtlas-Hackaton-NASA-2026`, rama `main`.
2. Railway detecta `requirements.txt` y `railway.json`; no hay que configurar nada más. **No hacen falta variables de entorno** (no se usa `.env` ni credenciales de Earthdata).
3. En *Settings → Networking* pulsar *Generate Domain* para obtener la URL pública.
4. Comprobar que `https://<dominio>/_stcore/health` responde `ok` y abrir la app.

## Detalles que importan
- **El paquete no se instala, se importa con `PYTHONPATH=src`** (está en el comando de arranque). `config.py` calcula las rutas a `demo_data/` y `docs/` desde la ubicación del código; si el paquete se instalara en `site-packages`, esas rutas apuntarían a otro sitio y la app no encontraría los datos.
- **Puerto:** Railway pasa `$PORT`; el comando lo usa.
- **No subir `.env` ni `data/`**: están en `.gitignore`. La app no los necesita.
- **Atribución:** el pie de la app ya incluye los créditos de las fuentes (ver `docs/LICENCIAS.md`).
- Si la app arranca lenta la primera vez, es el calentamiento de la PCA y de la caché de Streamlit; cada sesión posterior es rápida.

## Lo que se probó
La app en local sin `data/features/` (solo `demo_data/`) y el despliegue real en Railway (salud 200, página y mapa cargan, sin errores de consola).
