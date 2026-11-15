# Deploying the app on Railway

The app (`app/streamlit_app.py`) runs without downloading anything: if `data/features/` does not exist, it reads `demo_data/` (≈ 0.7 MB, versioned).

## Deployment files (repository root)
| File | Purpose |
|---|---|
| `requirements.txt` | only the app's dependencies (numpy, pandas, pyarrow, scipy, scikit-learn, streamlit, pydeck) |
| `railway.json` | start command, health check (`/_stcore/health`) and restarts |
| `.python-version` | Python 3.12 (prebuilt wheels exist for all dependencies) |
| `.streamlit/config.toml` | headless mode, no telemetry, dark theme |

## Status (15 Nov 2026)
**Deployed** on Railway (project `astroatlas-nasa`, service `app`, branch `main`): https://app-production-6cc653bd.up.railway.app. The build finished successfully, the `/_stcore/health` route answers 200 and the app was opened and checked in the browser. Every push to `main` redeploys it.

## Steps on Railway (to repeat in another account)
1. *New Project → Deploy from GitHub repo* and choose `dorelysm/AstroAtlas-Hackaton-NASA-2026`, branch `main`.
2. Railway detects `requirements.txt` and `railway.json`; nothing else has to be configured. **No environment variables are needed** (no `.env` or Earthdata credentials are used).
3. In *Settings → Networking* click *Generate Domain* to get the public URL.
4. Check that `https://<domain>/_stcore/health` answers `ok` and open the app.

## Details that matter
- **The package is not installed, it is imported with `PYTHONPATH=src`** (it is in the start command). `config.py` computes the paths to `demo_data/` and `docs/` from the code's location; if the package were installed in `site-packages`, those paths would point elsewhere and the app would not find the data.
- **Port:** Railway passes `$PORT`; the command uses it.
- **Do not upload `.env` or `data/`**: they are in `.gitignore`. The app does not need them.
- **Attribution:** the app's footer already includes the source credits (see [../reference/licenses.md](../reference/licenses.md)).
- If the app starts slowly the first time, it is the warm-up of the PCA and of Streamlit's cache; every later session is fast.

## What was tested
The app locally without `data/features/` (only `demo_data/`) and the real deployment on Railway (health 200, page and map load, no console errors).
