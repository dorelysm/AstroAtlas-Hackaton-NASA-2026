# 🌍🌕🔴 AstroAtlas — finding Earth analogs for Moon and Mars bases

**NASA Space Apps Challenge 2026 · *Permanent Moon Base Locations and Mars***

AstroAtlas ranks places on Earth by how closely they resemble candidate sites on the Moon and Mars — terrain, temperature, ice/water and geology — and then **tests itself, honestly, against terrestrial analogs that scientists already use**. The result is a reproducible method, a public web app, and a clear map of where the method works and where it does not.

### 👉 [Open the live app](https://app-production-6cc653bd.up.railway.app/?lang=en) · available in English and Spanish

![AstroAtlas pipeline](docs/images/pipeline.svg)

---

## The idea in 60 seconds

| | |
|---|---|
| **Question** | Which places on Earth are good analogs for a Moon or Mars site, in *which aspects*, and where does the analogy break down? |
| **Method** | 35 target sites (21 Moon, 14 Mars) and 951 Earth cells are described with the same four aspects, over the same 50 km window and 500 m baseline. Similarity per aspect = `exp(−RMS z)`; the global score is a weighted mean of the aspects that have data. |
| **Honesty** | Known analogs only **validate**, never tune. Protocols and success criteria are **preregistered** (written, hashed and frozen before measuring). Negative results are published. |
| **Output** | A ranked, explained map for any target site, orbital imagery side by side (NASA), per-aspect confidence labels, use-case profiles and candidate profiles. |

---

## How AstroAtlas answers the five judging criteria

### 🌍 Impact
- **Gives mission teams a transparent shortlist tool**, not a black box: pick a Moon or Mars site, see the most similar Earth places, and read *what is similar, what is not, which data are missing and where the analogy fails* (gravity, atmosphere, radiation).
- **Tells users how far to trust it.** Pooled over 40 Mars and 20 Moon analogs the method ranks a known analog above a typical Earth cell **≈ 60 % / 58 % of the time (50 % = chance)**: better than chance, not by much. The app shows that number and its interval next to every result.
- **Reusable assets:** a frozen validation set of 45 analogs with provenance, a data contract for Earth/Moon/Mars features, and every experiment with its verdict — useful to anyone who wants to improve analog selection.

### 💡 Creativity
- **Multi-aspect, not one score.** The challenge says a place can be a great geological analog and a poor thermal one; AstroAtlas scores and labels each aspect separately (the *aspect atlas*).
- **Same data recipe on three bodies**, and a visual comparison built live from NASA services: Mars (Viking MDIM) or Moon (LRO WAC) next to the Earth place (MODIS / Blue Marble), at the same 150 km scale.
- **Self-auditing science:** eleven improvement ideas were preregistered and tested; only one survived, and only for the cold use case. Two candidate flaws were found by the project itself (rainforests proposed as "Mars-like"; flat ice sheets proposed as "Moon-like") and fixed or flagged.

### ✅ Validity
- **Three independent analog sets (45 sites):** a first set (23), a second set fixed before measuring (9), and 13 sites taken mechanically from the **ESA expert catalogue of planetary analogues**.
- **Preregistered, frozen-model evaluation** with bootstrap intervals over the analogs (the independent unit). Hashes of the protocols and lists are recorded in the documents.
- **Controls against known biases:** a flat-terrain control showed that an apparent topographic signal was just "craters sit on flat cratons"; a novelty check shows Harrat ash-Shamah is *already* studied as a planetary-pit analog.
- **Limits stated up front**: few analogs, snow ≠ subsurface ice, no Mars thermal data, unverified coordinates for some analogs, and some licences still to check ([licenses](docs/reference/licenses.md)).
- **189 automated tests**; the app runs from versioned demo data with no downloads.

![Validation results](docs/images/results.svg)

| Pooled validation (3 sets) | Mean u | 95 % CI | Reading |
|---|---|---|---|
| Moon (20 analogs) | 0.583 | 0.545 – 0.619 | slightly above chance |
| Mars (40 analogs) | 0.595 | 0.515 – 0.670 | slightly above chance; one set alone (ESA catalogue) does not pass |

Strong on **arid, volcanic and impact** analogs (Lanzarote 0.96, Pinacate 0.79, Atacama 0.65); weak on **cold, ice, hydrothermal and lake** analogs (Dry Valleys 0.04, Svalbard 0.18) — and we explain why.

### 🪐 Relevance
Directly built on the challenge text: open NASA Earth/Moon/Mars data (LOLA, MOLA, Diviner, Lunar Prospector & Odyssey GRS, MODIS, MERRA-2, SEDAC) plus ESA Copernicus DEM, USGS and open catalogues; **several dimensions of analogy** (topography, temperature, ice/water, geology, plus context on vegetation, settlements, dust/wind, caves and lava tubes); **scale awareness** (50 km windows and a 0.25° zoom); a **systematic search** beyond famous sites; and explicit **limits of Earth as an analog**.

**Two candidates for Mars**, with caveats: **Harrat ash-Shamah** (Syria/Jordan) — basaltic plateau, 8 documented lava tubes in the same region, previously studied for planetary pits — and **Haruj** (Libya) — a ~45,000 km² volcanic field with no analog study found in our preregistered search. Both are *hypotheses for expert review*, not discoveries. For the Moon the method finds no credible candidates, and says so.

### 🎤 Presentation
- A guided three-step app: *choose a site → read the map → read the profile*, with a plain-language glossary, percentages instead of raw scores, and accessibility fixes (language attribute, headings, contrast, keyboard, mobile layout).
- Everything is documented in English: [report](docs/report.md), [challenge text](docs/challenge.md), methods, results and every experiment.
- Bilingual interface (English / Spanish) with a sidebar selector and shareable `?lang=` links.

---

## What the app shows

1. **Pick a Moon or Mars site** and set how much each aspect matters.
2. **See an interactive map** of the most similar Earth places (named, with country), the known analogs for comparison, and a confidence panel.
3. **Open a place profile:** match per aspect with a one-line explanation, side-by-side NASA orbital views, and *what Earth cannot imitate*.
4. **Go deeper:** aspect atlas, use-case profiles (mobility, cold operations, ice, basaltic terrain, lava tubes), technical details and credits.

## Quick start

```bash
git clone https://github.com/dorelysm/AstroAtlas-Hackaton-NASA-2026.git
cd AstroAtlas-Hackaton-NASA-2026
python -m venv .venv && source .venv/bin/activate        # Windows: .venv\Scripts\Activate.ps1
pip install -e ".[app,dev]"
streamlit run app/streamlit_app.py                        # runs on the versioned demo_data/, no downloads
pytest                                                    # 189 tests
```

Reproduce the results: `python -m astroatlas.pipeline` (scores, validation, candidates). Regenerating the raw features needs the `[data]` extra and an Earthdata account (`.env.example`); every data module and experiment is listed in [docs/README.md](docs/README.md#reproducing-everything).

## Repository layout

| Path | Contents |
|---|---|
| `app/` | Streamlit app (`streamlit_app.py`) |
| `src/astroatlas/` | Package: similarity model, validation, experiments, i18n, imagery |
| `src/astroatlas/data/` | Data readers per body (PDS, Copernicus, MODIS, GLiM, SEDAC…) |
| `tests/` | 189 automated tests |
| `demo_data/` | Small versioned features and results so the app runs anywhere |
| `docs/` | [Documentation index](docs/README.md): report, validation, preregistrations, data sources, licences, catalogues |
| `docs/catalog/` | CSV catalogues of targets, landings and analog sets (frozen lists with hashes) |
| `.streamlit/`, `railway.json` | Theme and deployment configuration |

## Documentation highlights

- 📄 [Full technical report](docs/report.md)
- 🧪 [All preregistered experiments](docs/preregistrations/) and [validation](docs/validation/)
- 🗺️ [Candidate profiles](docs/results/candidate-profiles.md) · [Aspect atlas](docs/results/aspect-atlas.md) · [Use cases](docs/results/use-cases.md)
- 📚 [Data provenance](docs/reference/data-sources.md) · [Licences](docs/reference/licenses.md)
- 🖥️ [Interface, accessibility and deployment](docs/app/interface.md)

## Honest limitations

Few analogs per body (confidence intervals are wide) · "snow" is not subsurface ice · Mars has no thermal dimension · coordinates of several analogs come from Wikipedia and are unverified · some data licences are marked *to check* · Earth cannot reproduce reduced gravity, lunar vacuum, Mars' thin atmosphere or radiation. Parts of the literature search and code were produced with **AI assistants** and reviewed by the team.

## Credits

Developed by the **AstroAtlas team** for the **NASA Space Apps Challenge 2026**. Data and imagery: NASA (PDS, MODIS, MERRA-2, SEDAC, GIBS, Trek), ESA (Copernicus DEM, CAFE catalogue), USGS, GLiM (Hartmann & Moosdorf 2012), Obu et al. (2018), Natural Earth, Zenodo catalogues. This project is not endorsed by NASA.
