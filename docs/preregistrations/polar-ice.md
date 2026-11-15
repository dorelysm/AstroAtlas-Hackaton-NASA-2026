# Preregistration: Mars polar ice data and permafrost variable (15 Nov 2026, written BEFORE downloading or computing anything with these data)

**Reason:** [models.md](models.md) (Phase 0) showed that Phoenix and Arcadia Planitia have no ice data (the Odyssey hydrogen map we use does not cover beyond ≈ 57° latitude), so no target with known shallow ice could test the ice variable. Here we try to obtain that data and, if valid, finally test a terrestrial permafrost variable.
**Test set:** the 23 frozen analogs ([analog-validation.md](analog-validation.md)). **Base model:** the frozen one (commit `0b8a0a2`).

## Phase 1: a relative hydrogen index for all Mars targets
**Data:** NASA PDS, Mars Odyssey GRS, *Averaged Neutron Data* v2.0 (`ODY-M-GRS-5-AND-V2.0`, DOI 10.17189/1522868): 5° × 5° binary tables (2,592 cells, pole-to-pole coverage) with the **epithermal** neutron count rate (`CEPI`) per 15° interval of solar longitude (Ls) and Odyssey year (≈ 290 files of ≈ 114 kB, about 33 MB). Fewer epithermal neutrons = more hydrogen (water) in the top metre of soil. **It is not converted to water equivalent** (there is no published calibration in a gridded PDS product that I can use rigorously).
**Season rule (seasonal CO₂ frost also shields neutrons):** for |latitude| ≥ 40° only the Ls intervals **entirely within** [105°, 165°] (northern hemisphere, summer) or [285°, 345°] (south) are used; for |latitude| < 40°, all intervals. Cells with `CEPI` ≤ 0 or without data are ignored.
**Value per cell:** median of `CEPI` over the selected intervals and years.
**Index:** `H = −ln(CEPI / CEPI_ref)`, with `CEPI_ref` the median of the cells with |latitude| < 30°. More positive = more hydrogen than the equator. Each target takes the value of the 5° cell that contains it.
**Validity gate (if it fails, it stops and there is no Phase 2):** Spearman correlation between `H` and the already-measured hydrogen (`h2o_sr_5x5`) in cells with |latitude| < 42° where both exist: **ρ ≥ 0.6**.

## Phase 2: "ground ice" variable comparable between bodies
- **Mars:** binary class *ice-rich* if `H` ≥ ln(1.5) (the epithermal rate is at least a third lower than the equator's). The threshold is **arbitrary and fixed here**; no others are tried.
- **Earth:** binary class *probable permafrost* if the mean annual surface temperature is **< 271 K** (≈ −2 °C), computed as the mean over the 12 months of (daytime LST + night-time LST)/2 of MODIS 2019 (the same data already reduced; no new downloads). It is a **substitute** for a permafrost map, not the map.
- These two classes replace `ice__water_frac` (which today is water on Mars and snow on Earth) in the ice dimension; the rest of the model does not change. The Moon is not touched.
**Evaluation (Mars, 20 frozen analogs; same measures as [../validation/extended-validation.md](../validation/extended-validation.md)):**
- **Primary:** paired difference per analog of the mean u of "all" between the model with the classes and the base, with a 95 % bootstrap CI over the analogs. **Success criterion: lower bound > 0.**
- **Secondary (also decides):** **cold** analogs (rule of [cold-warm-groups.md](cold-warm-groups.md)) against cold targets (|lat| ≥ 45°) with the cold-model weights (ice 1, topography 0.5): u with lower bound **> 0.5**.
**It is adopted only if both the primary and the secondary are met.** Otherwise, it is not adopted.

## What is not done
The `H` threshold, the 271 K one, the season rule, the validity gate or the equatorial reference are not changed after seeing the results; any variant is reported separately as exploratory.

## Limits known beforehand
`H` is a **relative** index and not a water content; CO₂ frost and Earth snow are not corrected beyond the season rule; the terrestrial permafrost substitute only uses the mean annual surface temperature (not snow, moisture or soil type); the target's 5° cell mixes terrain different from that of the 50 km window; and the binary class loses information (the signal's intensity).

## Results (preregistration hash `48118c278237c3dd`; no changes to the protocol after seeing the numbers)

### Phase 1: Mars polar ice data, obtained
287 PDS tables were downloaded (about 33 MB; retries had to be added because the server dropped the connection once). **The validity gate is met: Spearman ρ = 0.816 (minimum 0.6) between `H` and the already-measured hydrogen, over 1,152 cells with |latitude| < 42°.** The index follows hydrogen where there was data, so it is usable.
`H` per target (equatorial reference CEPI 7.36; "ice-rich" threshold `H` ≥ 0.405):

| Target | Latitude | `H` | Ice-rich? |
|---|---|---|---|
| **Phoenix** | 68.2° | **1.299** | **Yes** |
| **Arcadia Planitia** | 47.3° | **0.390** | No (**0.015** below the threshold) |
| Spirit | −14.6° | 0.326 | No |
| Viking 2 | 47.7° | 0.206 | No |
| The other 10 targets | | 0.170 to −0.353 | No |

- **Phoenix goes from "no data" to clearly ice-rich** (the epithermal rate is 3.7 times lower than the equatorial one), which matches what is known about that site.
- **Arcadia comes out at 0.390, the second highest value and just below the threshold.** By the protocol the threshold is not changed: it is classified "not rich". It is a borderline case and the binary class loses information there.
- Only **one** target (Phoenix) is "ice-rich" with the preregistered rule.

### Phase 2: permafrost variable
Earth: **470 of 934 cells** with probable permafrost (mean annual temperature < 271 K); **all 5 cold analogs** (Dry Valleys, Haughton, Svalbard, Axel Heiberg, Eureka) fall in that class.

| Test | Result | Met? |
|---|---|---|
| **Primary:** Mars "all", paired difference with the classes against the base | 0.564 → 0.589; **+0.025 (CI −0.026 to +0.087)** | **No** (lower bound < 0) |
| **Secondary:** cold analogs against cold targets with cold-model weights, u with lower bound > 0.5 | u = **0.370 (CI 0.257 to 0.483)**; difference with the base **+0.060 (CI −0.017 to +0.127)** | **No** |

Per cold analog (base u → variant): Axel Heiberg 0.14 → 0.25; Dry Valleys 0.06 → 0.21; Svalbard 0.26 → 0.37; Eureka 0.50 → 0.49; Haughton 0.60 → 0.53.
**Preregistered verdict: neither the primary nor the secondary is met; the variable is NOT adopted and the model does not change.**

### Reading
- **It improves in the expected direction, but it is not conclusive:** three of the five cold analogs rise considerably (the Dry Valleys from 0.06 to 0.21), one stays the same and Haughton drops; the mean effect (+0.060) has an interval that includes zero and with 5 analogs it could not be otherwise.
- **It remains below chance (0.370):** of the three "cold" targets only Phoenix is ice-rich; Arcadia is a borderline case and Viking 2 is not. With a single clear ice target, the test has little to recognise.
- **Conclusion:** obtaining polar ice data **was the right step** (the validity gate is met and the classes match what is expected: Phoenix rich, the 5 cold analogs in permafrost), but with the current set of targets and analogs **an improvement cannot be demonstrated**. What would be needed is **more shallow-ice targets on Mars** (those of the SWIM mission, for example) and a larger set of cold analogs. **(Done on 15 Nov: see [shallow-ice.md](shallow-ice.md); with 8 targets of published ice the variable meets its criterion, for the cold case only.)**
