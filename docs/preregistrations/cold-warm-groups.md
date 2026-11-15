# Preregistration: two analog groups, cold and warm (15 Nov 2026, written BEFORE computing anything with groups)

## How the idea arises (and an honesty note)
The extended validation ([../validation/extended-validation.md](../validation/extended-validation.md)) and the inertia experiment ([thermal-inertia.md](thermal-inertia.md)) showed that the model recovers the **warm and arid** analogs and fails on the **cold and ice** ones. **That split was seen by looking at the results, not planned beforehand**, so it is a hypothesis generated with the test data. To limit the bias: (1) the group rule uses only one Earth climate variable, not the scores; (2) everything is fixed here before computing; (3) the cold model reuses weights defined before this analysis (`usecases.py`); (4) the result is declared up front **probably not conclusive** because of the size of the cold group (5 analogs). The distribution of `thermal__t_max_k` of the 23 analogs was seen when fixing the threshold, but no u.

**Test set:** the 23 frozen analogs ([analog-validation.md](analog-validation.md)). **Base model:** the frozen one (commit `0b8a0a2`).

## Groups (fixed)
- **Mars analogs (`analog_of` contains "mars"):** *cold* if `thermal__t_max_k` (monthly maximum of the daytime surface temperature, MODIS) is **< 295 K** (≈ 22 °C); *warm* otherwise. This gives **5 cold** (Dry Valleys, Haughton, Svalbard, Axel Heiberg, Eureka) and 15 warm.
- **Mars targets:** *cold* if |latitude| ≥ 45° (Arcadia Planitia, Viking 2, Phoenix); *warm* the other 11.
- **Moon:** not evaluated (only 2 polar targets and 1 cold analog).

## Models (fixed; no tuning)
- **Warm model:** the base ("all", four dimensions with equal weights).
- **Cold model:** weights `{ice: 1, topography: 0.5, thermal: 0, geology: 0}` (those of the use case "ice and permafrost in northern Mars" in `usecases.py`, defined earlier). Thermal is left out because Mars does not have it.

## Evaluation (fixed)
Same measures as the extended validation (u per analog with 50 km windows, bootstrap over the analogs), Mars only.
- **E1, primary:** **cold** analogs against **cold** targets: paired difference per analog of the mean u between the **cold model** and the **base ("all")** over those same targets (n = 5), with a 95 % bootstrap CI and an exact sign-flip test (one-sided).
  **Success criterion:** lower bound of the CI of the difference **> 0** and u of the cold model with lower bound **> 0.5**.
- **E2, descriptive (does not decide):** "system by groups": each analog is evaluated with its group's model over its group's targets (warm ones with the base over the 11 warm targets; cold ones with the cold model over the 3 cold ones). The u of the system over the 20 analogs is reported with its CI and the paired difference against the base over the 14 targets (0.564), **warning that the targets used are not the same**.

## What would be done if it is met
Present the project's output in two classes ("cold-climate analogs" and "warm and arid analogs") in the atlas and the app, with the cold model for the first group. **If it is not met, it is not adopted** and the result is documented.

## What is not done
The 295 K threshold, the 45° one, the cold-model weights or the groups are not changed after seeing the results; any variant is reported separately as exploratory.

## Limits known beforehand
Only 5 cold analogs (a bootstrap interval with 5 elements is very wide: that is expected); the cold group includes ice, permafrost and polar analogs that are not equivalent to each other; the MODIS surface temperature is monthly means; only 3 Mars targets are cold, and 2 of them (Arcadia, Phoenix) are the only ones with known shallow ice; and Earth "snow" still does not measure the same as Mars ice, so the cold model inherits that defect.

## Results (preregistration hash `97f2baf653687789`; no changes to the protocol after seeing the numbers)
Code: `src/astroatlas/groups.py` (`python -m astroatlas.groups`). Cold targets: Arcadia Planitia, Phoenix and Viking 2. Cold analogs: Dry Valleys, Haughton, Svalbard, Axel Heiberg and Eureka.

**E1, cold analogs against cold targets (n = 5):**

| Analog | Base model | Cold model | Difference |
|---|---|---|---|
| Axel Heiberg | 0.102 | 0.140 | +0.038 |
| Dry Valleys | 0.052 | 0.059 | +0.007 |
| Eureka | 0.472 | 0.495 | +0.023 |
| Haughton | 0.581 | 0.599 | +0.018 |
| Svalbard | 0.227 | 0.256 | +0.029 |

- Mean paired difference **+0.023 (95 % CI +0.014 to +0.032; exact one-sided p 0.031)**: the cold model improves **all five**, but only slightly.
- **u of the cold model = 0.310 (CI 0.131 to 0.489)**: still **below chance** (0.5). With the base model, 0.287.
- **Criterion (lower CI of the difference > 0 and cold u with lower CI > 0.5): NOT met** (the first part is met, not the second). **The groups are NOT adopted as a model** and the project's output does not change.

**E2, descriptive:** the "system by groups" gives u = 0.614 (CI 0.495 to 0.727) against 0.564 for the base over the 14 targets (paired difference +0.050, CI +0.025 to +0.074). **It must not be read as a real improvement:** the warm analogs are evaluated only over the 11 warm targets and leave out the 3 cold ones, where they score worse; the difference comes largely from changing the targets, as was warned beforehand.

## What it teaches
- **Separating the groups corrects an averaging problem, not the underlying problem.** Even comparing the cold analogs only with polar targets and using weights designed for them, **four of five remain below chance or close to it**; only Haughton (0.60) and Eureka (0.50) are around 0.5 or above.
- **CORRECTION (15 Nov, later): what followed about the ice variable was wrong.** It was written that Phoenix and Arcadia have a moderate water content according to Odyssey and that the magnitudes were not comparable; in reality **Phoenix and Arcadia have no ice data (NaN)**: the Odyssey map used does not cover beyond ≈ 57° latitude. The cold model only had those targets' topography and Viking 2's ice, so this experiment **could not** succeed with the cold analogs and its result says nothing about the snow variable. See [models.md](models.md) (Phase 0).
- **Practical conclusion:** for the cold and ice analogs **there is no model improvement available with the current data**; the honest thing is to say so and present that part as the main limitation of the method.
