# Challenge dimensions the model does not cover (15 Nov 2026)

The challenge suggests several dimensions. Status of each:

| Challenge dimension | Status | What exists |
|---|---|---|
| Geology and materials | Modelled (weak) | `geo__basalt_frac` (GLiM 0.5°, a single rock type) |
| Topography | Modelled | 16 variables, whitened PCA |
| Temperature | Modelled (limited) | Monthly LST; Earth does not reproduce Mars' daily extremes; Mars empty |
| Water and ice | Modelled (poor) | Snow; it does not measure dryness or subsurface ice (GLDAS tested, does not improve) |
| **Biology / habitability** | **Context flag** | `vegetated` (MODIS NDVI): hides rainforests and forests. It does not measure extremophiles or biosignatures |
| Settlements / logistics | Context flag | `viable` (GRUMP). It does not measure accessibility or safety |
| **Dust, wind and erosion** | **Descriptive context only** | `dust_surface_ugm3`, `dust_column_mgm2` and `wind10m_ms` (MERRA-2, 2019, 0.5° × 0.625° grid) in `earth*.parquet` and in the profiles. **There is no counterpart** on Mars (it would need the dust opacity from MCS/TES) or on the Moon, so no similarity is scored |
| **Caves and lava tubes** | **Context only** | Lunar pits (LROC, 278) integrated in `moon.parquet`; terrestrial Pyroduct tubes by region only (no coordinates); Mars catalogue (USGS, 1,062 candidates) integrated in `mars.parquet`; no Mars target has a cave within 50 km. See [caves-and-lava-tubes.md](caves-and-lava-tubes.md) |
| **Polar illumination** | **Not covered** | LOLA publishes illumination maps for the Moon, but Earth has no comparable equivalent (terrestrial polar night depends on axial tilt, not relief) |
| Processes (not just places) | Not covered | The method compares places, not processes |

## Why no more were added
Dust/wind and caves need a source on **both** bodies and a validation with analogs labelled for those dimensions, and today we have neither. Adding variables without a counterpart or without validation would increase the appearance of rigour without the rigour. What was done is the vegetation flag, which fixes a real failure (rainforests as candidates) with an open NASA source.
Dust and wind were added only as descriptive context (15 Nov 2026). To score them the Martian counterpart would be needed; it is the next step if the team wants it.
