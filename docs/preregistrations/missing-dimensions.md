# Preregistration (DRAFT): cells without data in a dimension (15 Nov 2026)

**Status: DRAFT, not frozen.** Nothing here changes the published model: the option is off by default (`missing="renormalize"`). Whoever freezes it should read the disclosure below, agree the criterion, record the hash and only then measure.

## Observation (measured on `demo_data`, reproducible with `python -m astroatlas.missing_data`)
The global score averages each cell over the dimensions it **has data for** (`global_score`), so a gap is never penalised, while a cell with data that does not match scores near 0 in that dimension.
- 244 of 951 Earth cells (26 %) lack at least one whole dimension (239 without geology, 17 without temperature and ice).
- Among the 50 best cells, **Apollo 11 has 42 with a gap, Mare Tranquillitatis pit 48, Luna 21 40, Surveyor 5 37**. If gaps did not matter, about 13 would be expected.
- This is consistent with the flaw already documented in the report (flat ice sheets proposed as "Moon-like"); the link was not tested.
- Related, **not part of this change**: for the 21 lunar targets the temperature score is at most 0.000003 on every Earth cell (the lunar day/night range is about 44 standard deviations above the Earth's). Its measured effect in the ablation (−0.02 without it) may come from the gap rule above and not from matching temperatures. This deserves its own preregistration (range-aware matching).

## Question
Does scoring a gap as "no similarity" (`missing="zero"`) recover the known analogs better than ignoring it (`missing="renormalize"`, the published model)?

`zero`: every dimension in which the **target** has data counts for every cell; a cell without data in it scores 0 there. A cell with no score at all stays NaN. Everything else (features, standardisation, topography PCA, weights, windows) is unchanged.

## Disclosure of what was already looked at
Both variants were run on the **10 original analogs** (`earth_sites.parquet`), which the project had already seen. The baseline reproduces the published numbers exactly.

| Body | Analogs | Published | `zero` | Change |
|---|---|---|---|---|
| Moon | 4 | 0.637 | 0.684 | +0.047 |
| Mars | 8 | 0.493 | 0.510 | +0.017 |

With 4 and 8 analogs these differences are **inside the noise**, and the original set cannot be used as confirmation. A variant that fills a gap with the median score of the cells was also tried (Moon 0.641, Mars 0.506), and "only cells with all dimensions" (Moon 0.630, Mars 0.413, worse); neither is proposed. `zero` may over-correct: with it the best cells of many targets contain almost no gap cells (0 to 5 of 50), which is below the 13 expected by chance.

## Proposed test (to be agreed before measuring)
- **Data:** the frozen sets not used in the exploration above: set 2 and set 3 (`validation-set-2.md`, `validation-set-3.md`), with the same 21 + 14 targets and the same windows. Run `python -m astroatlas.missing_data --extended` (or `--sites/--known` for each frozen list).
- **Metric:** u of each analog averaged over the body's targets; paired change `zero − renormalize` with a 95 % bootstrap CI over the analogs (the independent unit).
- **Proposed criterion:** adopt `zero` for a body only if the lower bound of the CI of the change is > 0 with at least 8 analogs; report it as harmful if the upper bound is < 0. If neither, keep the published model and publish the result.
- **Diagnostic (not a criterion):** gaps among the top 50 cells, before and after.

## Result
_Not measured._
