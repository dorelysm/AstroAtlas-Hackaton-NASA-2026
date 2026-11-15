# Documentation index

Start with the [report](report.md). Everything is in English.

| Folder | What is inside |
|---|---|
| [`report.md`](report.md) | Technical report: method, results, candidates, lessons, limits |
| [`challenge.md`](challenge.md) | Official challenge text |
| [`validation/`](validation/) | [validation](validation/validation.md) · [extended](validation/extended-validation.md) · [per aspect](validation/per-aspect-validation.md) · [ablation](validation/ablation.md) · [stability](validation/stability.md) · [analog search](validation/analog-search.md) · [coordinate verification](validation/coordinate-verification.md) |
| [`preregistrations/`](preregistrations/) | Protocols written before measuring, each with its result: analog sets (1–3), ice, polar ice, shallow ice, permafrost, thermal inertia, emissivity, multiscale topography, variability, groups, models, novelty, plains, missing dimensions (draft) |
| [`results/`](results/) | [Candidate profiles](results/candidate-profiles.md) · [aspect atlas](results/aspect-atlas.md) · [use cases](results/use-cases.md) |
| [`context/`](context/) | [Processes](context/processes.md) · [caves and lava tubes](context/caves-and-lava-tubes.md) · [dimensions not modelled](context/unmodeled-dimensions.md) |
| [`reference/`](reference/) | [Data sources](reference/data-sources.md) · [licences](reference/licenses.md) · [NASA APIs](reference/nasa-apis.md) · [feature contract](reference/feature-contract.md) |
| [`app/`](app/) | [Interface and accessibility](app/interface.md) · [Deployment](app/deployment.md) |
| [`catalog/`](catalog/) | CSV catalogues: targets, landings, analog sets (frozen, hashed) |

## Reproducing everything

```bash
pip install -e ".[app,dev]"        # core + app + tests
pip install -e ".[data]"           # only to regenerate raw features (geospatial libs); copy .env.example to .env
python -m astroatlas.pipeline      # scores, validation, candidates, clusters
```

Regenerate data (each module downloads, reduces and deletes the raw file):

```bash
python -m astroatlas.data.moon | mars | earth | earth_water | earth_thermal | earth_geology | usgs_analogs
python -m astroatlas.data.settlements | earth_vegetation | earth_dust_wind | caves
python -m astroatlas.places --build           # place names from Natural Earth
```

Validation and experiments (each documented in `preregistrations/`):

```bash
python -m astroatlas.validation_ext [--build]   # 23 analogs, frozen model
python -m astroatlas.validation2 [--build]      # second independent set
python -m astroatlas.validation3 [--build]      # ESA catalogue set
python -m astroatlas.ablation | aspect | aspect_usgs | stability | atlas | usecases | profiles | zoom
python -m astroatlas.shallow_ice [--build] | cold | permafrost_map | polar_ice | permafrost
python -m astroatlas.inertia | emissivity --phase1 | multiscale | variability [--build] | groups | models
python -m astroatlas.missing_data [--extended]   # gap handling: renormalize vs zero (draft protocol)
```

## Team rules

- The contract is `data/features/{body}.parquet` ([feature contract](reference/feature-contract.md)); new features are declared in `src/astroatlas/config.py` and documented.
- `data/` and `.env` are not versioned; a single branch, `main`.
- Known analogs only validate; labels and protocols are fixed before measuring and later corrections are reported separately.
- Every new data source is recorded in [data-sources](reference/data-sources.md) (origin, URL, licence, confidence).
- Synthetic data have no scientific value.
