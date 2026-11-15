# Model validation (first round)

Status as of 14 November 2026, with the real data available that day. **The results are preliminary and almost all within noise**; they must not be presented as a successful validation. The later, larger validations are in [extended-validation.md](extended-validation.md) and [../preregistrations/validation-set-3.md](../preregistrations/validation-set-3.md).

## What was changed
1. **Whitened PCA of the topography** (`similarity.fit_topo_model`). The 16 `topo__*` variables are strongly correlated (mean |r| ≈ 0.74 on Earth). With the mean of z-scores, a single property (roughness, for example) counted up to 15 times. They are now summarised in the principal components that explain ≥ 90 % of the variance (today 3 components, 93.6 %) and the distance is measured there. The PCA is fitted **only with Earth cells**.
2. **Validation by analog type** (`validate.known_for_body`). The `analog_of` column of `docs/catalog/known_analogs.csv` says whether an analog serves the Moon, Mars or both. A Mars target is no longer scored against Mauna Kea, nor a lunar one against Atacama.
3. **95 % confidence intervals** (`validate.evaluate(..., n_boot=500)`), resampling the known analogs. There are only 4 to 8 per type, so without an interval the mean misleads.
4. **Validation without the coarse grid** (`validate.evaluate_sites`). The known analogs themselves are scored with the 50 km windows of `earth_sites.parquet` (the same as the targets) and we look at which percentile they fall in among all Earth cells. This avoids depending on a 5° cell (~550 km) being "near" the analog.

The earlier results can be reproduced with `python -m astroatlas.pipeline --no-pca --all-analogs`.

## Results (29 targets: 15 lunar and 14 Martian)
Mean [min–max] across targets. 0.5 = chance.

| | Cell AUC | Site AUC (50 km) | Site recall @5 % |
|---|---|---|---|
| Before (no PCA, all analogs) | 0.45 [0.34–0.64] | 0.45 [0.18–0.88] | 0.07 |
| **After** (PCA + by type) | 0.47 [0.36–0.89] | **0.57** [0.37–0.82] | 0.06 |
| After, Moon | 0.51 | 0.63 | 0.08 |
| After, Mars | 0.43 | 0.51 | 0.04 |

Note: the mean "before" AUC quoted the day before (0.52) came from a `metrics.json` of an earlier run; recomputed today with the current data it gives 0.45.

## How to read it
- **A real but small improvement.** The site AUC rises from 0.45 to 0.57. Before, some targets scored *worse than chance* (for example Apollo 11: 0.24) because they were compared with analogs that do not apply to them.
- **Still almost all noise.** The range across targets is huge and recall @5 % is ≈ 0.06 (chance would be 0.05). Mars does not improve (0.51).
- **Very few analogs.** There are 4 lunar and 8 Martian analogs, and only 2 of the 4 lunar ones fall in grid cells. The intervals are wide (for example Jezero: cell AUC 0.47, 95 % CI 0.35–0.78).
- **One case that does look coherent:** Shackleton (cell AUC 0.89, CI 0.73–0.97) scores high at Haughton and Askja, two cold sites. But only 2 analogs are covered, so it is a hint, not proof.
- **The Dry Valleys come out far away for Mars** (percentile 87–92 with Jezero and Oxia). Probable cause: landing sites are flat *by design* (Jezero 2.9°, Oxia 0.8°) while the Dry Valleys are mountain relief (~11°). Topography measures landing suitability, and classic analogs are chosen for climate, ice and geology. **The two purposes should be separated** instead of mixed in one score.

## What limits the results today
- **Empty or weak dimensions:** Earth geology is empty, Mars thermal too, and Earth thermal is **air** temperature (POWER), not surface temperature. Earth `ice__water_frac` is a precipitation proxy. (These were fixed in later rounds; see [../reference/data-sources.md](../reference/data-sources.md).)
- **Few positives** and analog coordinates that come from Wikipedia (see [coordinate-verification.md](coordinate-verification.md)).
- **Scale:** Earth cells are 5°; how the topography is sampled in each had not been checked.

## Next steps for the validation to count
1. Fill the empty dimensions (MODIS LST, geology, Mars thermal).
2. Separate the **landing suitability** score (topography) from the **environmental analog** score (climate, ice, geology) and validate each with its own list.
3. Expand the list of known analogs with official sources.
4. Consider regularised Mahalanobis for all dimensions and a PU model for suitability.
