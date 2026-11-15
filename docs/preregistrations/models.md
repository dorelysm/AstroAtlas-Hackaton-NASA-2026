# Preregistration: Earth-to-Earth analog model, consensus between models and permafrost variable (15 Nov 2026, written BEFORE computing any of this)

**Test set:** the 23 frozen analogs ([analog-validation.md](analog-validation.md)). **Model A (the current, frozen one):** commit `0b8a0a2`.

## Phase 0: a finding that changes the approach (diagnostic, no protocol)
While preparing the permafrost variable it was found that **the polar Mars targets have no ice data**: the Odyssey hydrogen map we use (`h2o_sr_5x5.tab`) has no values between ≈ 57° and 90° latitude in either hemisphere and has gaps between 42° and 57° N. **Phoenix (68.2° N) and Arcadia Planitia (47.25° N) come out with `ice__water_frac = NaN`**; Viking 2 (47.7° N) does have a value (0.046). Consequences:
- For the only two targets with known shallow ice, the model compares **topography only** (the ice dimension is ignored).
- The other 12 targets with ice data have between 0.03 and 0.07 of water: all **dry**. **No target in our set represents what the cold analogs imitate (permafrost, shallow ice).**
- That is why the failure with the cold analogs and the results of the groups experiment **cannot be attributed to the Earth ice variable** (snow): the test had nowhere to succeed. This corrects what was written earlier (see [cold-warm-groups.md](cold-warm-groups.md)).
**Permafrost variable (E3):** it **cannot be honestly tested** while Mars has no ice data at the poles; with the 12 dry targets it would only measure "absence of permafrost", the same as snow measures today. It is noted as the next step (a Mars polar hydrogen product is needed, e.g. from the Odyssey spectrometer neutron maps) and **it is not run**.

## E1: analog model (Earth to Earth)
It scores each Earth cell by its similarity to **the body's known analogs**, all measured with Earth variables (it does not use the Moon or Mars). It removes the comparability between bodies and does not depend on the targets' ice data.
- **References:** the analogs with `analog_of` containing the body (Moon 12, Mars 20), with their terrestrial features (whitened-PCA topography, thermal, snow, GLiM geology), exactly the same as model A, with equal weights.
- **Similarity** of a cell `c` to an analog `a`: the same global score of the model (mean of `exp(−RMS z)` per dimension, ignoring the missing ones) using the features of `a` as the profile. **Cell score = maximum over the references** (nearest neighbour).
- **Evaluation (leave one out):** for each analog `a`, `a` and **all analogs within 500 km** of `a` are removed from the references (so neighbours do not leak); `u(a)` = fraction of grid cells with a score lower than that of `a`, with the same reference rule. Mean per body with a 95 % bootstrap CI over the analogs.
- **Success criterion:** lower bound of the CI of the mean u **> 0.5** in each body (the same criterion as the extended validation). The paired difference against the equivalent statistic of model A (see below) and the cold/warm groups are also reported.

## E2: consensus between the two models
- **Model A, comparable statistic:** `A(c)` = mean, over the body's targets, of the cell's global score with the base model. `P_A` = percentile of `A` among the cells (0-1). For an analog, `P_A` is computed with its `A` against the cells.
- **Model B:** that of E1, with its `P_B` (in the evaluation, with the leave-one-out rule).
- **Consensus:** `s(c) = min(P_A(c), P_B(c))` (the cell is good only if it is good in both).
- **Evaluation:** `u` of each analog with `s` (same rule as E1); mean with CI. **Success criterion:** lower bound of the CI of the mean u **> 0.5** and the paired difference with `P_A` with a lower bound **> 0 in at least one body** and no upper bound < 0.
- **Output:** the cells of highest consensus (viable, non-vegetated and more than 500 km from any known analog), with model B using **all** the analogs as a reference (only to propose candidates, not to evaluate).

## What is not done
The aggregation (maximum), the exclusion radius (500 km), the way of combining (minimum) or the dimensions are not changed after seeing the results; any variant is reported separately.

## Limits known beforehand
With 12 and 20 references, model B only rediscovers what the analogs have in common and does not use the target site's information; the test set is the same one that serves as a reference (mitigated with the leave-one-out rule and the spatial exclusion, but it is not equivalent to an independent set); the Moon's analogs are few (12) and 8 of them are "Moon and Mars"; and model B inherits the defects of the Earth data (snow, monthly thermal, GLiM).

## Results (preregistration hash `947e23b621db661f`; no changes to the protocol after seeing the numbers)
Code: `src/astroatlas/models.py` (`python -m astroatlas.models`). `P_A` is the statistic of model A comparable with B (percentile of the mean score over the targets); that is why it differs from the u of the extended validation (Moon 0.595, Mars 0.564), which averages the u of each target.

| Body | Model | Mean u | 95 % CI | Met (lower bound > 0.5)? |
|---|---|---|---|---|
| Mars (20) | A (`P_A`) | 0.551 | 0.427 to 0.672 | No (already known) |
| Mars (20) | **E1: B, Earth-to-Earth analogs** | **0.499** | 0.371 to 0.631 | **No** |
| Mars (20) | **E2: consensus (minimum)** | **0.452** | 0.334 to 0.578 | **No** |
| Moon (12) | A (`P_A`) | 0.699 | 0.545 to 0.839 | Yes |
| Moon (12) | **E1: B** | **0.465** | 0.326 to 0.621 | **No** |
| Moon (12) | **E2: consensus** | **0.509** | 0.389 to 0.643 | **No** |

Paired difference against A: E1 Mars −0.052 (−0.230 to +0.125) and Moon −0.234 (−0.457 to −0.016); **E2 Mars −0.099 (−0.202 to −0.010) and Moon −0.190 (−0.390 to −0.003)**: the minimum consensus **worsens** in both bodies.
**Verdict: no criterion is met. Neither model B nor the consensus is adopted. E3 was not run** (see Phase 0). The project's model does not change.

## What it did show (preregistered secondary result: cold and warm groups)
| Mars | n | Model A (`P_A`) | Model B |
|---|---|---|---|
| **Cold** analogs (Dry Valleys, Haughton, Svalbard, Axel Heiberg, Eureka) | 5 | **0.191** (0.071 to 0.316) | **0.743** (0.541 to 0.851) |
| **Warm** analogs | 15 | **0.671** (0.571 to 0.767) | **0.418** (0.282 to 0.563) |

- **The two models are complementary:** A recognises the warm ones and B recognises the cold ones. Model B, which uses no Mars data, **does recover the cold analogs** (four of five with u ≥ 0.83; the Dry Valleys with 0.34), which confirms that model A's failure with them comes from **comparing with targets that do not represent that kind of place** (Phase 0) and not from the cold analogs being unreachable.
- Why B works with the cold ones: they are places similar to each other (all polar and permafrost) and, when comparing Earth with Earth, the comparability between bodies and the targets' lack of ice data disappear.
- Why it does not work overall: with warm and arid ones B is below chance (0.418), because those analogs are very different from each other (sand seas, volcanoes, craters, salt flats) and an analog does not resemble the others much.
- **Exploratory (NOT preregistered, decides nothing):** the union ("good in A or in B", `maximum` of the percentiles) gives on Mars u = 0.601 (CI 0.503 to 0.700), difference with A +0.050 (−0.056 to +0.169), and on the Moon 0.675 (0.510 to 0.829), −0.024 (−0.090 to +0.063). It suggests that combining by "either of the two" recovers both groups, but **it is not significant and was chosen after seeing the results**; it would have to be preregistered and evaluated with an independent set.

## What changes in our conclusions (corrections)
- It had been written that the problem with the cold analogs was that Earth "snow" does not measure the same as Mars ice. **That cannot be claimed:** the two polar targets had no ice data and the other 12 are dry. The correct conclusion is that **the target set includes no shallow-ice site with data**, so the validation of the cold analogs with model A is not informative.
- [cold-warm-groups.md](cold-warm-groups.md), [../report.md](../report.md), [../validation/extended-validation.md](../validation/extended-validation.md) and [../reference/data-sources.md](../reference/data-sources.md) were corrected.

## Next step that does make sense
1. **(Done on 15 Nov: see [polar-ice.md](polar-ice.md); the permafrost variable is not adopted, an inconclusive result.)** **Obtain ice data for the Mars poles** (e.g. the epithermal neutron maps of the Odyssey spectrometer, from the PDS itself) for Phoenix and Arcadia; only then can a terrestrial permafrost variable (E3) be tested against targets with ice.
2. **(Done on 15 Nov: see [validation-set-2.md](validation-set-2.md) and [validation-set-3.md](validation-set-3.md); the A-or-B union is not adopted, +0.006 against A with CI −0.079 to +0.118 on 8 independent Mars analogs.)** Preregister the A-or-B union and evaluate it with an independent set of analogs.
