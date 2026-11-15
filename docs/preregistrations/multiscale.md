# Preregistration B: multi-scale topography (15 Nov 2026, written BEFORE computing any score with it)

**Problem:** the topography dimension uses 16 highly correlated variables (the PCA summarises them in ~3 components) and, after controlling for flat terrain, it shows no signal ([plains.md](plains.md)). A description of **how roughness changes with scale** is a more stable property between bodies than absolute magnitudes.
**Test set:** the 23 frozen analogs ([analog-validation.md](analog-validation.md)) and the USGS layer with 185 craters and dunes against 200 controls. **Base model:** the frozen one (commit `0b8a0a2`).

## Variant B (fixed)
The 16 variables are replaced by **three derived from those that already exist** (no new data):
1. `H` = slope of the least-squares regression of ln(roughness_L) against ln(L), with L = 1, 2 and 5 km (`topo__rough_{1,2,5}km_m`; roughness is bounded below at 0.01 m). It is an apparent Hurst exponent.
2. `ln(roughness_1km)`.
3. `ln(mean slope in degrees + 0.1)`.
Then, whitened PCA fitted with the Earth cells (explained variance 0.90, maximum 3 components), like the base topography. The other dimensions do not change.

## Evaluation (fixed)
- **Primary:** paired difference per analog of the mean u of **"all"** between B and the base model, with a 95 % bootstrap CI over the analogs, separately for the Moon and Mars.
- **Secondary (reported, do not decide):** the same with "only topography", and the **slope-stratified AUC** of the USGS test (5 strata, same method as [plains.md](plains.md)) for the base model and for B.
- **Success criterion:** the lower bound of the paired difference of "all" is **> 0 in at least one body** and the upper bound is **not < 0 in any**. If it is not met, it is not adopted.
- If in addition B's stratified AUC has a lower bound > 0.5, it is noted as the first real topographic signal after the flatness control.

## What is not done
Other scales, other combinations of variables or other PCA thresholds are not tried after seeing the results; any variant is reported separately as exploratory.

## Limits known beforehand
There are only three scales (1, 2 and 5 km) over a 500 m baseline, so `H` is an apparent and noisy exponent; with 50 km windows the roughness at 5 km is estimated with few samples.

## Results (preregistration hash `82ddf50863e9d8c8`; no changes to the protocol after seeing the numbers)
Code: `src/astroatlas/multiscale.py` (`python -m astroatlas.multiscale`) with the common evaluator `variants.py`. With the base model the u of the extended validation (Moon 0.595; Mars 0.564) and the USGS stratified AUC (0.476 and 0.494) are reproduced, which checks that the comparison is clean.

| Body | Configuration | Base u | Variant u | Paired difference | 95 % CI |
|---|---|---|---|---|---|
| Moon | **all** (primary) | 0.595 | 0.592 | −0.003 | −0.043 to +0.036 |
| Mars | **all** (primary) | 0.564 | 0.566 | +0.002 | −0.054 to +0.055 |
| Moon | only topography | 0.602 | 0.613 | +0.012 | −0.048 to +0.074 |
| Mars | only topography | 0.520 | 0.517 | −0.003 | −0.091 to +0.085 |

USGS, slope-stratified AUC (craters and dunes against controls): base Moon 0.476 (0.418 to 0.534) and Mars 0.494 (0.436 to 0.552); **variant** Moon 0.500 (0.443 to 0.560) and Mars 0.494 (0.435 to 0.554). Neither exceeds chance.

**Verdict: the criterion is not met (no lower bound of "all" is > 0). The variant is NOT adopted and the model does not change.** The differences are of the order of ±0.01 with intervals of ±0.05: **there is no detectable difference**, either in favour or against. The variant's PCA reduces the three variables to 2 components that explain all the variance, so the three scalar variables carry the same information as the 16 as far as this test is concerned.
**Reading:** describing roughness by its scale exponent adds nothing measurable with three scales (1, 2 and 5 km) over a 500 m baseline. It is not evidence that the approach would not work with more scales or with higher-resolution DEMs, only that this design improves nothing.
