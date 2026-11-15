# Preregistration A: calibrate the distance with the target's variability (15 Nov 2026, written BEFORE reading any additional window or computing any score with it)

**Problem:** today a Moon or Mars site is a single 50 km window and the distance is scaled with the Earth's dispersion. It is not known how "similar" is similar enough: a heterogeneous site tolerates more difference than a very uniform one.
**Test set and base model:** the same as in [multiscale.md](multiscale.md).

## Method (fixed)
- **Additional windows per target:** a 3 × 3 grid of 50 km windows centred at offsets of −25, 0 and +25 km (north-south and east-west over the body's surface; windows overlapping by 50 %), with the same DEMs, the same 500 m baseline and the same 16 topographic variables as the central window. Targets with |latitude| ≥ 85° (the polar ones): only the 3 north-south offsets. Windows with less than 50 % valid pixels are discarded.
- **Variability:** the valid windows are projected onto the Earth's whitened principal components (those of the base model) and the **sample standard deviation** `s_k` of each component across the target's windows is taken. A target with fewer than 5 valid windows (fewer than 3 for the polar ones) is **not calibrated** (`s_k = 0`).
- **Calibrated distance (topography only):** the difference in each component is divided by `√(1 + s_k²)` (variance of the Earth measure, 1 after whitening, plus that of the target). It is implemented with a PCA model of its own per target whose scale is multiplied by `√(1 + s_k²)`. Thermal, ice and geology do not change (they only have one value per site).

## Evaluation (fixed)
As in B: paired difference of **"all"** (primary) with a 95 % bootstrap CI over the analogs, per body; secondary: "only topography" and the slope-stratified USGS AUC. **Success criterion:** lower bound > 0 in at least one body and no upper bound < 0.

## What is not done
The offsets, the minimum number of windows, the way of combining variances or the set of components are not changed after seeing the results; any variant is reported separately.

## Limits known beforehand
Variability measures the **heterogeneity of the terrain around the site at a 25 km scale**, not the landing ellipse nor the variability of the Earth cell (which is not modelled). With 9 overlapping windows the standard deviation is a noisy estimate. It only calibrates topography.

## Results (preregistration hash `ddb02975a17bf101`; no changes to the protocol after seeing the numbers)
Windows read: Moon 177 (21 targets) and Mars 126 (14 targets), all with data; **all 35 targets were calibrated**. Mean variability between windows, in units of the whitened component: Moon s₁ = 0.37, s₂ = 0.58, s₃ = 1.01; Mars s₁ = 0.22, s₂ = 0.54, s₃ = 0.60. Code: `src/astroatlas/variability.py` with the common evaluator `variants.py`; the base model reproduces the u of the extended validation and the USGS stratified AUC.

| Body | Configuration | Base u | Variant u | Paired difference | 95 % CI |
|---|---|---|---|---|---|
| Moon | **all** (primary) | 0.595 | 0.579 | **−0.016** | −0.026 to −0.005 |
| Mars | **all** (primary) | 0.564 | 0.560 | **−0.005** | −0.008 to −0.001 |
| Moon | only topography | 0.602 | 0.602 | +0.001 | −0.015 to +0.015 |
| Mars | only topography | 0.520 | 0.520 | −0.001 | −0.008 to +0.006 |

USGS, slope-stratified AUC: base Moon 0.476 and Mars 0.494; **variant** Moon 0.482 (0.425 to 0.538) and Mars 0.495 (0.436 to 0.552). Neither exceeds chance.

**Verdict: the criterion is not met. In both bodies the upper bound of "all" is < 0 (it worsens, although by very little). The calibration is NOT adopted and the model does not change.**
**Reading:** with "only topography" the difference is practically zero (±0.001): dividing the difference by `√(1 + s²)` with s between 0.2 and 1.0 is almost equivalent to a uniform rescaling of each target's distances, which **does not change the order of the cells**. What changes is the **balance between dimensions**: the topography of a heterogeneous target gains score relative to thermal, ice and geology, and that worsens the global result slightly. Heterogeneity at a 25 km scale, measured with 9 overlapping windows, adds no information that helps order the analogs better.
**Limits of the conclusion:** only spatial heterogeneity around the site was measured, not the landing ellipse nor the variability of the Earth cell; and it only calibrates topography.
