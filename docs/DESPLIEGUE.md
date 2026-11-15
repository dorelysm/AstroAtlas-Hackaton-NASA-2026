# Despliegue de la app en Railway

La app (`app/streamlit_app.py`) corre sin descargar nada: si no existe `data/features/`, lee `demo_data/` (≈ 0,7 MB, versionado).

## Archivos de despliegue (en la raíz del repo)
| Archivo | Para qué |
|---|---|
| `requirements.txt` | solo las dependencias de la app (numpy, pandas, pyarrow, scipy, scikit-learn, streamlit, pydeck) |
| `railway.json` | comando de arranque, comprobación de salud (`/_stcore/health`) y reinicios |
| `.python-version` | Python 3.12 (hay ruedas precompiladas de todas las dependencias) |
| `.streamlit/config.toml` | modo headless, sin telemetría, tema oscuro |

## Pasos en Railway (hace falta tu cuenta; no se hizo desde aquí)
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

## Lo que no se ha probado
El despliegue real en Railway no se ha ejecutado (requiere tu cuenta y confirmación). Sí se probó la app en local sin `data/features/` leyendo solo `demo_data/`.
