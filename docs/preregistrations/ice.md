# Preregistration: Earth ice/water variable (14 Nov 2026, written BEFORE measuring)

Variants of `ice__water_frac` on Earth, without touching the Moon or Mars:
- **A (current):** mean annual snow cover (MODIS MOD10CM).
- **B:** mean annual soil moisture 0-10 cm (GLDAS Noah 0.25°, 2019), `ice_soil_moisture_m3m3`.

Metric: ablation by dimension (`astroatlas.ablation`), u = P(analog > typical cell), CI by bootstrap over analogs.
**Criterion (fixed before seeing results):** B is adopted only if, for the Moon and Mars, u("all") with B is greater than with A
and u("only ice") with B is > 0.5. If not, A is kept and it is reported that B did not help. No more variants are tried after seeing the numbers.

## Result (same session; preregistration hash `805c751d6e61d88d`)

Mean u (95 % CI by bootstrap over analogs), 0.5 = chance:

| Body | Config | A snow | B soil moisture |
|---|---|---|---|
| Moon | all | 0.637 [0.555-0.682] | 0.642 [0.563-0.687] |
| Moon | only ice | 0.684 [0.332-0.870] | 0.669 [0.354-0.985] |
| Mars | all | 0.493 [0.305-0.679] | 0.469 [0.302-0.626] |
| Mars | only ice | 0.623 [0.368-0.859] | 0.578 [0.230-0.864] |

**Verdict:** the criterion required improving on the Moon AND Mars; on Mars "all" worsens (0.493 → 0.469). **A (snow) is kept.**
The differences are much smaller than the CIs (4-8 analogs), so there is no evidence either that B is worse: it simply does not help.
GLDAS stays in `earth*.parquet` as diagnostic columns (`ice_soil_moisture_m3m3`, `ice_swe_kg_m2`; the latter is dominated by the ice caps) and does not enter the model.
