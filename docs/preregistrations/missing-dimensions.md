# Preregistration (DRAFT): cells without data in a dimension (15 Nov 2026)

**Status: DRAFT, not frozen; exploratory result recorded below.** Nothing here changes the published model: the option is off by default (`missing="renormalize"`). Whoever freezes it should read the disclosure below, agree the criterion, record the hash and only then measure.

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

## Result (exploratory, 15 Nov 2026)
Run on the frozen sets 2 and 3 with the proposed criterion, **before the draft was agreed or frozen**, so it is reported as exploratory. Baseline numbers reproduce the published ones (Mars set 3: 0.577; Moon with 8 analogs: 0.565). Nothing in the published model changed.

| Body | Analogs | `renormalize` (published) | `zero` | Change (95 % CI) | Proposed criterion |
|---|---|---|---|---|---|
| **Moon** (7 of set 3 + Teide of set 2) | 8 | 0.565 | 0.614 | **+0.049 (0.038 to 0.061)** | **Met** (lower bound > 0, at least 8 analogs) |
| Mars (sets 2 + 3) | 20 | 0.625 | 0.643 | +0.018 (-0.012 to 0.039) | Inconclusive (interval includes 0); keep the published model |

By set: set 3 Moon (7 analogs) +0.051 (0.039 to 0.063) and Mars (12) +0.034 (0.018 to 0.050); set 2 Mars (8) -0.007 (-0.070 to 0.034). The Moon gain has the same sign in the original 10 analogs (+0.047), in set 3 and in the pooled sets.

**Decision:** `renormalize` stays the default. The Moon result is encouraging and consistent, but the Moon criterion is met narrowly (8 analogs, 7 from one set), Mars is inconclusive, the criterion was not frozen before measuring, and sets 2 and 3 can no longer serve as confirmation.

**Next step (future work):** agree and freeze a per-body criterion, then measure on a new independent set with more lunar analogs before changing any default; keep checking that `zero` does not over-correct (0 to 5 gap cells in the top 50, against about 13 expected).

## Confirmation protocol (DRAFT, to be agreed and frozen before any measurement)
Proposed by Mauxy Salcedo, written with Claude. **Every number below is a proposal, not a computed value.** Nothing here changes the published model.

**1. What is tested.** `missing="zero"` against `missing="renormalize"`, one body at a time. The Moon is the primary test. Mars is decided separately, with its own set. The independent unit is the analog.

**2. Frozen model.** `missing="zero"` exactly as released in v1.0.1. No other variant (median fill, complete cases only) may be tried on the new set. Features, weights, windows and the 21 + 14 targets stay as they are.

**3. New set.**
- No analog from the original 10, set 2 or set 3, and none within 50 km of one of them.
- The source must be independent of the ones already used (the ESA CAFE catalogue went into set 3). The selection rule is a mechanical filter over the whole source, written before the list is made, never a hand pick.
- Size: **Moon at least 12 new analogs. Mars at least 20.**
- Coordinates from the primary source, each with its URL. The list and this protocol are hashed before anything is computed, as in the other preregistrations.

**4. Sample-size check, before measuring.** From the exploratory runs on sets 2 and 3, take `s`, the standard deviation across analogs of the paired change (`python -m astroatlas.missing_data`). The analogs needed to resolve a change of 0.03 are about `(1.96 · s / 0.03)²`. If that is more than 12 for the Moon, use it. If the source cannot supply it, report the test as underpowered and do not adopt.

**5. Decision rule, per body.**
- **Adopt** `zero` as the default for that body only if the lower bound of the 95 % paired bootstrap CI of the change is > 0 **and** the point change is at least **+0.02**.
- **Reject** (report as harmful) if the upper bound is < 0.
- Otherwise keep `renormalize` and publish the result.
- Why a floor of +0.02: the Moon's +0.049 was measured after `zero` had already been chosen from the first look, so it is probably inflated. The floor avoids adopting a change that is real but trivial.
- If `zero` is adopted for one body only, the default becomes body-specific. That needs its own code change and PR.

**6. Diagnostic, not a criterion.** Gap cells among the 50 best, before and after, to keep checking that `zero` does not over-correct (0 to 5 of 50, against about 13 expected by chance).

**7. What this will not settle.** The quality of the analog coordinates. And the lunar temperature score, which is about 0 on every Earth cell: part of the Moon gain may come from how gap cells are ordered rather than from matching temperatures. That deserves its own preregistration (range-aware matching).

## Confirmation result
_Not measured._
