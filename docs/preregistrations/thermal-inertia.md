# Preregistration: thermal-inertia dimension (15 Nov 2026, written BEFORE computing any score with it)

**Reason:** the extended validation ([../validation/extended-validation.md](../validation/extended-validation.md)) showed that the model recovers arid, volcanic and impact analogs but fails on cold and ice ones, and that Mars has no thermal data. Thermal inertia is a soil property (how fast its temperature changes) and is measured on Mars with TES.
**Test set:** the 23 frozen analogs ([analog-validation.md](analog-validation.md)); it is not modified. **Base model:** the frozen one (commit `0b8a0a2`).

## Definition (fixed)
- **Mars:** MGS-TES night-time thermal-inertia map (Putzig and Mellon 2007; PDS `mgs-m-tes-5-timap-v1`, units J·m⁻²·K⁻¹·s⁻¹ᐟ²), 7200 × 3600 pixels, 20 pixels/degree. Only non-interpolated pixels (mask = 1) with value > 0 are used. For each target, **median** of the valid pixels in a ±25 km window. It is converted to a **percentile** against all valid Mars pixels with |latitude| ≤ 80°.
- **Earth:** there is no direct equivalent. An **albedo-free apparent proxy** is used: `1 / (T_day − T_night)`, with the mean diurnal range of MODIS LST (already computed, `thermal__t_range_k`; a small thermal range is equivalent to high inertia). It is converted to a **percentile** against the 951 cells of the Earth grid. The 23 analogs use the same reference percentile.
- **Comparison:** **percentiles within each body** are compared ("this site is in the X % most inert of its planet"). It is a **relative** analogy: absolute inertia values are not comparable (other observation times, atmosphere, sensor), and that is said so in the results.
- **Moon:** no data (there is no comparable inertia map in this scope). The dimension does not apply to the Moon.
- It is added as a fifth dimension, `inertia`, with the same weight as the others.

## Evaluation (fixed)
Same measure as the extended validation (u per analog, 50 km windows, bootstrap over the analogs), for **Mars** only, comparing:
- **"all + inertia"** against **"without inertia"** (the 4-dimension base model, which does not use inertia): **paired difference per analog** and its 95 % bootstrap CI.
- **"only inertia"**: mean u and its CI.
- Secondary (descriptive): the variation of u in the cold analogs (Dry Valleys, Axel Heiberg, Svalbard, Eureka).

**Success criterion:** the paired difference "all + inertia" − "without inertia" is **positive with a CI lower bound > 0**, and the u of "all + inertia" has a lower bound > 0.5. If it is not met, the dimension is **not adopted**.
**What is not done:** other reference percentiles, other windows, the day map, or albedo versions are not tried after seeing the results; if done, it is reported separately as exploratory.

## Limits known beforehand
No albedo in the Earth proxy; MODIS passes at 10:30 and 22:30 and TES at other times; the TES map is not a single epoch; the percentiles assume each planet covers a comparable range from "dust to rock", which is not demonstrated; and it only applies to Mars.

## Results (preregistration hash `ce95183026ef90a5`; no changes to the protocol after seeing the numbers)
Mars, 20 analogs of the frozen set. Mean u with 95 % bootstrap CI over the analogs (0.5 = chance):

| Configuration | Mean u | 95 % CI |
|---|---|---|
| Without inertia (base model, 4 dimensions) | 0.564 | 0.448 to 0.678 |
| **All + inertia (5 dimensions)** | **0.483** | 0.400 to 0.574 |
| **Only inertia** | **0.363** | 0.266 to 0.463 |
| Only ice (snow), for reference | 0.633 | 0.507 to 0.751 |

- **Paired difference "all + inertia" − "without inertia": −0.081 (CI −0.133 to −0.025).** It is **negative and its CI excludes zero**: adding the dimension **worsens** the result.
- **"All + inertia" has u = 0.483 < 0.5.**
- **Verdict: the criterion is not met. The thermal-inertia dimension is NOT adopted.** The project's model does not change. (The base model's u, 0.564, reproduces exactly that of the extended validation.)

## What the dimension did
"Only inertia" **inverts** the order of the analogs:
- **It improves the cold and ice ones:** Dry Valleys 0.03 → 0.12, Axel Heiberg 0.10 → 0.21, Svalbard 0.18 → 0.33, Eureka 0.38 → 0.51 (with all dimensions). Its "only inertia" u is ≈ 0.67.
- **It worsens the warm and arid ones:** Atacama 0.05, Salar Grande 0.05, Meteor Crater 0.07, Pinacate 0.08, Vredefort 0.17 ("only inertia"); with all dimensions, Pinacate falls from 0.79 to 0.56, Atacama from 0.65 to 0.43, Meteor Crater from 0.69 to 0.48.
- **Why (hypothesis, not checked):** the MODIS terrestrial proxy `1/(T_day − T_night)` depends strongly on moisture, snow and cover, not only on soil properties; hot deserts have large diurnal amplitudes and come out with "low inertia", the opposite of what was expected. In addition MODIS and TES observe at different times and there is no albedo. Percentiles within each body did not solve the lack of comparability.
- **Observation (not proven):** the analog set mixes two groups, warm and arid (which the base model recognises) and cold and ice (which "only inertia" or "only ice" recognises). A single global similarity does not serve both; it is an argument for evaluating by aspect or by use case, as the atlas does.

## What remains open (not done, by the protocol)
A version with albedo (MODIS MCD43), the TES day map, another percentile reference or a real thermal model. Any of them would be **exploratory** and reported separately, without replacing this verdict.
