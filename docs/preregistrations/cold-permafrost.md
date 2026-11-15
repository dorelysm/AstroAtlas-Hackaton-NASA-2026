# Preregistration: permafrost without ice sheets, for the cold use case (15 Nov 2026, written BEFORE computing anything with this rule)

**Reason:** [shallow-ice.md](shallow-ice.md) adopted the permafrost variable for the cold case only, but the six best cells came out in interior Antarctica and Greenland: **ice sheets, not permafrost**. The "probable permafrost" class (mean annual temperature < 271 K) does not tell them apart. Here a rule to exclude them is fixed, it is checked that the preregistered test still holds, and we see which cold candidates remain.

## Rule (fixed now; no other thresholds are tried)
- **Perennial snow / ice sheet:** MODIS mean annual snow (MOD10CM 2019, Earth `ice__water_frac`, fraction of the year with snow) **≥ 0.9**. It is a simple physical criterion (snow almost all year = glacial ice, not frozen ground); the 0.9 threshold is **arbitrary and fixed here**.
- **Class "permafrost without ice sheets" (PF2):** 1 if mean annual temperature < 271 K **and** mean annual snow < 0.9; 0 otherwise. It is applied **equally** to Earth cells and analog sites, with no exceptions. The Mars classes do not change (the 8 published-ice targets + Phoenix = 1; the others, the class already computed).

## Evaluation (fixed)
Same design as [shallow-ice.md](shallow-ice.md): 7 cold analogs (plus those meeting the rule of [cold-warm-groups.md](cold-warm-groups.md)) against the 9 ice targets, cold-model weights (ice 1, topography 0.5), identical base variant.
- **Q1:** mean u with PF2, lower bound of the 95 % CI (bootstrap over analogs) **> 0.5**.
- **Q2:** paired difference PF2 − base, lower bound **> 0**.
- **Q3 (credibility of the candidates):** the 6 best regions (≥ 500 km apart, `viable` and non-vegetated, more than 500 km from any known analog of the two sets, score = mean over the 9 ice targets) must have **snow < 0.9 and mean annual temperature < 271 K** (it is checked, not imposed when choosing) and **none can fall on a known ice sheet** (Antarctica south of 60° S or the Greenland interior north of 66° N with snow ≥ 0.9).
- **It is integrated into the cold use case only if Q1, Q2 and Q3 are met.** If Q1 or Q2 fail, the permafrost variable is **not used for any candidate** and the cold case is documented as without credible candidates. If only Q3 fails, it is reported and not integrated.
- **Novelty check of the candidates** (text, does not decide): for each of the first 3, two fixed searches: `<region> Mars analog permafrost ice` and `<region> planetary analogue cold desert`; positive control `Devon Island Mars analog permafrost`. Classification as in [novelty.md](novelty.md).
- **Descriptive:** how many cells go from class 1 to 0 because of the rule, and the snow value of each cold analog (if any is excluded by the rule, it is reported).

## What is not done
The snow threshold, the temperature one, the targets, the analogs or the criteria are not changed after seeing the results; any variant is reported separately as exploratory.

## Limits known beforehand
MODIS 2019 is a single year; mean annual snow ≥ 0.9 also includes very high plateaus with almost permanent snow; temperature and snow do not measure permafrost (there is no permafrost map in the project); the candidates are hypotheses, not measurements.

## Results (protocol hash `f5e36b4e33503e3c`; no changes to the protocol after seeing the numbers)
Code: `src/astroatlas/cold.py` (`python -m astroatlas.cold`).
**Descriptive:** the rule takes class 1 from 470 to **190 cells** (280 turn to 0 because of perennial snow). Among the 7 cold analogs, **the Antarctic Dry Valleys end up in class 0** (mean annual snow 1.00, the MODIS product sees them covered): the rule treats them as an ice sheet, which is a failure of the snow product in a dry valley; the other 6 stay in class 1 (Axel Heiberg 0.79, Svalbard 0.78, Haughton 0.63, Eureka 0.61, Tuktoyaktuk 0.60, Fairbanks 0.48).

| Criterion | Result | Met? |
|---|---|---|
| **Q1** mean u with PF2, lower bound > 0.5 | **0.778 (CI 0.558 to 0.908)** | **Yes** |
| **Q2** paired difference PF2 − base, lower bound > 0 | **+0.378 (CI +0.229 to +0.500)** | **Yes** |
| **Q3** the 6 candidates are permafrost and none falls on an ice sheet | **One falls in Antarctica** (−82.5°, 167.5° E, snow with no data) | **No** |

Per analog (base → PF2): Axel Heiberg 0.23 → 0.83; Fairbanks 0.41 → 0.86; **Dry Valleys 0.15 → 0.14 (no improvement: it ended in class 0)**; Eureka 0.52 → 0.91; Haughton 0.57 → 0.92; Svalbard 0.32 → 0.85; Tuktoyaktuk 0.61 → 0.94.
Preregistered candidates (6): five in Greenland or the Arctic (77.5° N −17.5° E; 82.5° N −22.5°; 67.5° N −67.5°; 72.5° N −22.5°; 72.5° N −102.5°) and one in Antarctica (−82.5° 167.5° E). **Three of them are in Greenland** (77.5° N −17.5°; 82.5° N −22.5°; 72.5° N −22.5°): although the protocol let them pass (the mean snow of their 500 km cell is < 0.9 because they mix ice-free coast and sheet), they are largely ice sheet.

**Preregistered verdict: Q1 and Q2 are met but Q3 is not; it is NOT INTEGRATED into the cold case.** The permafrost variable is **not used for any candidate** and the cold case is documented as **without credible candidates**.

### Honest reading
- **The analog test comes out better than before** (u 0.778 and +0.378), but that result is still partly by construction (a binary class that analogs share with the targets) and now rests on 6 analogs (the Dry Valleys do not count).
- **The failure is of the candidates, not of the rule itself:** the mean snow of a 500 km cell is not enough to separate ice sheet from permafrost when the cell mixes coast and glacier, and Antarctica with snow without data slipped through. An ice-sheet mask (e.g. a glacier map or land cover) would have been needed, which the project does not have.
- **Exploratory (after seeing Q3, not preregistered, decides nothing):** if all of Antarctica and Greenland are excluded by hand, the six best cells are: **Baffin Island (67.5° N, −67.5°), the Canadian Arctic (72.5° N, −102.5° and 77.5° N, −117.5°), northern Tibet/Kunlun (37.5° N, 87.5° E), the Pamir (37.5° N, 72.5° E) and the British Columbia coast (57.5° N, −132.5°)** (scores 0.83 to 0.69). They are **hypotheses to review**: the Canadian Arctic is the classic setting for Mars analogs (Devon and Axel Heiberg are nearby but were discarded for being within 500 km), and no novelty check was done nor was it verified that the Tibet and British Columbia cells are not glaciers.
- **The real next step:** an ice-sheet mask (glaciers or land cover) and a permafrost map, not more threshold adjustments (done in [permafrost-map.md](permafrost-map.md)).
