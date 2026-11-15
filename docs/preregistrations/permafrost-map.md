# Preregistration: a real permafrost map instead of the temperature rule (15 Nov 2026, written BEFORE computing any class with this map)

**Reason:** [cold-permafrost.md](cold-permafrost.md) showed that the "probable permafrost" class based on temperature (< 271 K) and snow does not separate permafrost from ice sheets and leaves little-credible candidates. Here it is replaced by a **permafrost map modelled and validated with boreholes**: Obu, Westermann, Kääb and Bartsch (2018), *Ground Temperature Map, 2000-2016, Northern Hemisphere Permafrost*, PANGAEA, [doi:10.1594/PANGAEA.888600](https://doi.org/10.1594/PANGAEA.888600) (CC-BY 3.0 licence; ESA GlobPermafrost project). File used: `UiO_PEX_5.0_20181127_2000_2016_25km.nc` (25 km; variable `PerProb`, permafrost probability 0-1, only over **ice-free emerged land**, from 25° N to 84° N).

## Class (fixed now; no other thresholds are tried)
**PF3 = 1** if the mean `PerProb` of the valid pixels whose centre is within ≤ 25 km of the centre of the cell or site (the same 25 km window as MODIS) is **≥ 0.5**; if no pixel falls in the window the nearest is used if it is within ≤ 30 km. **PF3 = 0** in any other case, including: ice sheets and glaciers (the map has no data), the southern hemisphere and latitudes < 25° N (outside the coverage), the sea and cells without a valid pixel. It is applied **equally** to Earth cells and analog sites. The Mars classes do not change (the 8 published-ice targets + Phoenix = 1).
**Consequence known beforehand:** the Dry Valleys (Antarctica) end up in class 0, as with the earlier rule.

## Evaluation (fixed)
Same design as [cold-permafrost.md](cold-permafrost.md): cold-model weights (ice 1, topography 0.5), 9 ice targets, identical base variant. **Cold analogs:** those meeting the rule of [cold-warm-groups.md](cold-warm-groups.md) (maximum monthly daytime temperature < 295 K) among **the 45 analogs** of the three sets (the subset of the 7 of the earlier test is also reported).
- **R1:** mean u with PF3, lower bound of the 95 % CI (bootstrap over analogs) **> 0.5**.
- **R2:** paired difference PF3 − base, lower bound **> 0**.
- **R3 (credibility of the candidates):** the 6 best regions (≥ 500 km apart, `viable`, non-vegetated, more than 500 km from any of the 45 analogs, score = mean over the 9 ice targets) must have **PF3 = 1**, lie outside Antarctica and the Greenland ice sheet, and not be a lone pixel (the mean `PerProb` of their window ≥ 0.5 by definition of PF3).
- **It is integrated into the cold use case only if R1, R2 and R3 are met.** If R1 or R2 fails the permafrost variable is discarded for candidates; if only R3 fails it is reported and not integrated.
- **Descriptive:** how many cells have class 1 with the map (against 190 with the temperature-and-snow rule and 470 with temperature alone); the agreement between the rules; the `PerProb` value of each cold analog.
- **Novelty check** (text, does not decide), only if integrated: two fixed searches per region for the first 3 (`<region> Mars analog permafrost ice`, `<region> planetary analogue cold desert`) and positive control `Devon Island Mars analog permafrost`.

## What is not done
The 0.5 threshold, the window, the targets, the analogs or the criteria are not changed after seeing the results; any variant is reported separately as exploratory.

## Limits known beforehand
The map is a **model** (root-mean-square error of 2 °C against boreholes) at 25 km, which does not see small mountain permafrost nor that of the southern hemisphere; it does not distinguish ground ice from dry permafrost; the binary class loses information; the Dry Valleys and the rest of the southern hemisphere stay without data; the candidates are hypotheses, not measurements.

## Results (protocol hash `d5d333c504413cb2`; no changes to the protocol after seeing the numbers)
Code: `src/astroatlas/permafrost_map.py` (`python -m astroatlas.permafrost_map`). Map: Obu et al. (2018), 25 km, CC-BY 3.0 (a 15 MB download in `data/raw/permafrost/`, not versioned).
**Descriptive:** with the map there are **144 cells** of class 1 (against 190 with the temperature-and-snow rule and 470 with temperature alone); of the 470 by temperature, **331 are not permafrost according to the map** (the temperature rule overestimated). Cold analogs (14, maximum-temperature rule < 295 K over the 45 analogs): class 1 at Axel Heiberg, Svalbard, Bockfjord, Murchison Fjord, Eureka, Haughton, Tuktoyaktuk and Golden Deposit (`PerProb` 0.95 to 1.00); **class 0 at Fairbanks (0.28), Eyjafjallajökull, Krýsuvík, Pavilion Lake, Yellowstone (≈ 0) and the Dry Valleys (no data)**.

| Criterion | Result | Met? |
|---|---|---|
| **R1** mean u with PF3, lower bound > 0.5 | **0.683 (CI 0.512 to 0.840)** | **Yes** (narrowly) |
| **R2** paired difference PF3 − base, lower bound > 0 | **+0.244 (CI +0.100 to +0.391)** | **Yes** |
| **R3** the 6 candidates are PF3 = 1, outside Antarctica and ice sheets | all 6 with `PerProb` = 1.0 | **Yes** |
| (subset of the 7 cold analogs of the earlier test) | u 0.726 (0.482 to 0.928); diff +0.326 (+0.140 to +0.505) | descriptive |

Per analog (base → PF3): Axel Heiberg 0.23 → 0.87; Svalbard 0.32 → 0.89; Bockfjord 0.26 → 0.88; Eureka 0.52 → 0.94; Haughton 0.57 → 0.95; Tuktoyaktuk 0.61 → 0.95; Golden Deposit 0.60 → 0.96; Murchison 0.58 → 0.97; **they drop** Pavilion Lake 0.30 → 0.12, Fairbanks 0.41 → 0.34, Eyjafjallajökull 0.42 → 0.36; unchanged Krýsuvík, Yellowstone and Dry Valleys.
**Preregistered verdict: R1, R2 and R3 are met; IT IS INTEGRATED INTO THE COLD USE CASE** (new case "Ground ice and permafrost (Mars), with permafrost map" in `usecases.csv` and in the app). **The global score of the model does not change.**

### Candidates (6 regions, score 0.86 to 0.82)
North-east Greenland (77.5° N, −17.5°), north Greenland / Peary Land (82.5° N, −22.5°), Baffin Island (67.5° N, −67.5°), east Greenland (72.5° N, −22.5°), west Greenland (72.5° N, −52.5°) and the Canadian Arctic (72.5° N, −102.5°). All are **ice-free land with probable permafrost according to the map** (not ice sheet), more than 500 km from any of the 45 analogs. They are not new sites for science: the Canadian Arctic (Devon, Axel Heiberg) is the classic setting and western Greenland has already been used (Kangerlussuaq, Paatuut).

### Novelty check (preregistered, text; valid method: the Devon Island positive control came out "studied")
- **North-east Greenland:** **studied as an analog, partially**: the Grottedal caves (Kronprins Christian Land) are presented as a polar-desert setting with features in common with Mars and an astrobiological test bed.
- **Peary Land:** **mentioned in passing**: it is studied as a cold desert (microbiology of crusts and permafrost), but no source frames it as a planetary analog.
- **Baffin Island:** **mentioned in passing**: one source cites the high Arctic around Baffin and Victoria as good Mars analogs, without specific studies of Baffin.
A "no evidence" does not prove that no literature exists (standard US web search, no paid databases).

### Honest reading
- **The improvement is now larger and cleaner than with the temperature rule**, and the candidates stopped being ice sheets. But **it is still partly by construction**: with a binary class the real-permafrost analogs coincide in ice with the 9 targets, and only 144 of 934 cells have class 1; the 0.683 mostly measures that **having real permafrost is enough to rise**.
- **The set of "cold analogs" is defined by temperature, not by ice**, so it includes cold sites without permafrost (Iceland, Yellowstone, Pavilion Lake) that, correctly, drop or do not rise; that drags the mean and the lower bound (0.512) is tight.
- **The candidates are regions of real, known permafrost, not discoveries:** they serve as a list of where to look for shallow-ice analogs, not as a prediction of something unknown. The map only covers the northern hemisphere, so **the Dry Valleys and everything in the south are lost**.
- **It is not integrated into the global score** (the global effect of the permafrost variable was negative in [shallow-ice.md](shallow-ice.md)): it only changes the cold use case.
