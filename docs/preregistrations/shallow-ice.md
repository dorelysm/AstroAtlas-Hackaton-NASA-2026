# Preregistration: shallow-ice targets with published evidence and permafrost variable (15 Nov 2026, written BEFORE computing the features or any score of these targets)

**Reason:** [validation-set-2.md](validation-set-2.md) and [polar-ice.md](polar-ice.md) left the permafrost variable without a fair test: only Phoenix was a clearly ice-rich target. Here shallow-ice targets **with published evidence independent of our data** are added and it is tested again, once, with the same design.

## New targets (8) and their provenance
List fixed in `docs/catalog/dundas_ice_targets.csv` (sha256 `02867f4eecc514ad`). All coordinates (planetocentric latitude, east longitude) are read **from the text, the figures and Table 1** of the open-access article by Dundas et al. (2021), *Widespread Exposures of Extensive Clean Shallow Ice in the Mid-Latitudes of Mars*, JGR Planets 126, e2020JE006617 (open copy: HAL hal-03186594): the **Milankovič** scarp cluster (54.5 N, 213.5 E), the **S6 scarp** (56.9 S, 96.3 E), a **crater with exposed ice** (69.3 N, 142.2 E) and the **5 sites of Table 1** (impacts with icy colour). They are sites where **exposed ice is seen**; they do not depend on the neutron index.
**Why only 8:** the full scarp catalogue (USGS data release, DOI 10.5066/P9Y8FR1R) is behind a ScienceBase anti-bot check that cannot and should not be bypassed; only the coordinates the article itself gives are used. Tables S1 and S4 of the supplement are not in the open copy.
**Excluded** are the sites in the article that are not confirmed ice-exposing (e.g. the "uncoloured" scarp of Fig. 2B and the "marginal" one of Fig. 2A). None of the 8 is within 15 km of an existing target (the nearest is 541 km away).

## Variable (unchanged from [polar-ice.md](polar-ice.md))
- **Mars:** class *ice-rich* = 1 for the 8 new ones (published evidence) and for **Phoenix** (neutron index `H` ≥ ln 1.5, rule already fixed); for the other targets, the already-computed `ice_rich` class (Arcadia remains "no", by the fixed rule).
- **Earth:** *probable permafrost* if the mean annual temperature < 271 K (MODIS 2019, as before).
- These classes replace `ice__water_frac` only in the "permafrost" variant. The **base** variant uses the current `ice__water_frac` (with the hydrogen of `h2o_sr_5x5`, which has gaps or NaN beyond ≈ 42-57°). The topography of the new targets is computed with MOLA (50 km window, like the others); there is no thermal or geology for Mars.

## Evaluation (fixed)
**Ice targets (9):** the 8 new ones + Phoenix. **Cold analogs:** those of the rule of [cold-warm-groups.md](cold-warm-groups.md) (maximum monthly daytime temperature < 295 K) among the 23 + the 9 of the second set (expected: 5 + 2 = 7). **Cold-model weights:** ice 1, topography 0.5, rest 0.
- **P1 (primary):** mean u of the cold analogs against the 9 ice targets with the permafrost variant; 95 % bootstrap CI over the analogs. **Criterion: lower bound > 0.5.**
- **P2 (primary):** paired difference per cold analog (permafrost variant − base) with a 95 % CI. **Criterion: lower bound > 0.**
- **It is adopted only if P1 and P2 are met.** Otherwise, the permafrost variable is not adopted and the model does not change.
- **Secondary (they do not decide):** (a) the 2 new cold analogs separately; (b) the u of the base variant against the 9 ice targets (does the current model recognise them with these targets?); (c) effect on the mean u of "all" on Mars if the 8 targets are added to the set of 14 (paired difference); (d) how many of the 8 are "rich" according to the neutron index `H` (consistency of the index with the published evidence; it changes no class).

## What is not done
Thresholds, the list of targets, the cold analogs, the weights or the criteria are not changed after seeing the numbers; any variant is reported separately as exploratory.

## Limits known beforehand
Only 7 cold analogs (5 already used in earlier tests, 2 independent), so power is low; the targets are points of local evidence (a scarp, a crater) and the 50 km window mixes different terrain; no Mars thermal; the coordinates come from the article (planetocentric) and were not checked against USGS primary data; the `H` index has 5° resolution and may not flag all as rich.

## Results (protocol hash `7513849a4b115d53`; list `02867f4eecc514ad`; no changes to the protocol after seeing the numbers)
Code: `src/astroatlas/shallow_ice.py` (`python -m astroatlas.shallow_ice --build`, then without `--build`). Cold analogs (7): Axel Heiberg, Fairbanks, Dry Valleys, Eureka, Haughton, Svalbard, Tuktoyaktuk. Ice targets (9): the 8 new ones + Phoenix.

| Cold analog | Base u | Permafrost u | Difference |
|---|---|---|---|
| Axel Heiberg | 0.233 | 0.631 | +0.398 |
| Fairbanks (new) | 0.411 | 0.755 | +0.344 |
| Dry Valleys | 0.150 | 0.589 | +0.439 |
| Eureka | 0.515 | 0.840 | +0.325 |
| Haughton | 0.572 | 0.855 | +0.283 |
| Svalbard | 0.315 | 0.716 | +0.401 |
| Tuktoyaktuk (new) | 0.607 | 0.883 | +0.276 |

| Criterion | Result | Met? |
|---|---|---|
| **P1** mean u with permafrost, lower bound > 0.5 | **0.753 (CI 0.672 to 0.829)** | **Yes** |
| **P2** paired difference with the base, lower bound > 0 | **+0.352 (CI +0.309 to +0.394)** | **Yes** |
| (b) base u against the ice targets | 0.400 (0.281 to 0.520) | (does not decide) |
| (a) the 2 new cold ones | Fairbanks 0.41 → 0.76; Tuktoyaktuk 0.61 → 0.88 | (does not decide) |
| (c) "all" on Mars with the 22 targets | base 14 → base 22: −0.012 (−0.025 to +0.001); **base 14 → permafrost 22: −0.087 (−0.147 to −0.023)** | (does not decide) |
| (d) neutron index `H` at the 8 sites | **4 of 8** "rich" (Milankovič 0.62, S6 0.98, crater 69° N 0.92, T1-c 0.43); T1-a, T1-b, T1-d and T1-e not (−0.04 to 0.20) | (does not decide) |

**Preregistered verdict: P1 and P2 are met, so the permafrost variable IS ADOPTED.** It is the first idea of the series that meets its criterion.

### Scope of the adoption (decision taken AFTER seeing the numbers; the protocol did not fix it)
- **Only for the "cold / shallow ice" use case** (weights ice 1, topography 0.5), **not** for the global score: secondary (c) shows that with the 22 targets and the permafrost class the u of "all" on Mars **worsens (−0.087, CI −0.147 to −0.023)**, and the earlier independent test ([validation-set-2.md](validation-set-2.md), V3) also gave a negative global effect. The global model does not change.
- **It was not yet integrated** into `usecases.py`, the atlas or the app at this point (later done with a real permafrost map: [permafrost-map.md](permafrost-map.md)).

### Honest reading (why this result has to be read with care)
- **Part of the effect is by construction.** With a binary class, the 7 cold analogs (all of "permafrost" class) coincide exactly in the ice dimension with the 9 targets (all "ice-rich"), and half of the Earth cells (470 of 934) are also "permafrost" by temperature; the result mostly measures that **being in the right class is enough to rise in the ranking**, not that the model distinguishes permafrost from other cold terrain.
- **The test confirms it: the cold candidates are the ice sheets**, not permafrost (exploratory, does not decide): the six highest-scoring cells are interior Antarctica and Greenland (e.g. −82.5°, −102.5° and 77.5°, −17.5°), so **there are no credible candidates** for the cold case with this variable. It is the same flat-terrain problem already seen with topography.
- **The neutron index only recognises 4 of the 8 sites** with published ice: it is a 5° measure of the shallow part, and it says "not rich" at four sites where exposed ice is seen. This suggests the neutron class underestimates ice at the other targets (e.g. Arcadia, which was 0.015 below the threshold); in this experiment the 8 were fixed as rich by published evidence, not by `H`.
- **Low power and partial independence:** only 7 cold analogs, 5 of them already used in earlier tests (although none was used to tune anything); the 2 new ones (Fairbanks, Tuktoyaktuk) rise just like the rest.
- **Follow-up:** see [cold-permafrost.md](cold-permafrost.md) (a rule to remove the ice sheets improves the test but does not pass the candidate credibility check).
- **The 8 targets come from a single article** (which chooses sites where ice is exposed) and their coordinates were not checked against the USGS catalogue (inaccessible because of the anti-bot check).
