# Terrestrial analogs for Moon and Mars bases: a reproducible method and its limits

NASA Space Apps Challenge 2026 · challenge *Permanent Moon Base Locations and Mars* · status as of 15 November 2026

## Summary
We built a **multidimensional similarity index** that compares Earth cells with 35 sites on the Moon (21) and Mars (14) using open data from NASA and other agencies, and we **validated it against known terrestrial analogs**. The method works end to end and is reproducible, but **its power to recover known analogs is small**: the pooled hit rate over three independent analog sets is about 60 % (50 % = chance). We present it as a **method plus a set of documented negative results**, not as a map of discoveries. The candidates it proposes are hypotheses for expert review.

## 1. Idea
For each target site we compute how similar every Earth cell is, dimension by dimension: **topography, thermal, water/ice and geology**. The per-dimension score is `exp(−distance)` between standardised variables (topography, with 16 variables, is compressed with PCA); the global score is a weighted mean of the available dimensions. Each cell also carries two **context flags** that do not enter the score: nearby population (`viable`) and vegetation (`vegetated`).

## 2. Data (all open)
| | Topography | Thermal | Ice / water | Geology |
|---|---|---|---|---|
| **Moon** | LOLA | Diviner | Lunar Prospector GRS (only 2 polar targets have data) | yes, FeO proxy (Lunar Prospector GRS) |
| **Mars** | MOLA | empty (decision) | Odyssey GRS | yes |
| **Earth** | Copernicus GLO-90 | MODIS LST | MODIS snow | GLiM (not NASA, CC-BY) |

Common baseline: 500 m and a 50 km window. Every download is reduced and deleted (for example 1.2 GB of NDVI end up as a few MB). Provenance and licences: [reference/data-sources.md](reference/data-sources.md), [reference/licenses.md](reference/licenses.md).

## 3. How we validated
The known analogs (the original 10, plus a USGS layer with 185 craters and dunes and 200 controls) **only validate, they never tune the model**. The metric is *u* = probability that an analog scores higher than a typical cell (0.5 = chance), with a bootstrap over the analogs because they are the independent unit. **Labels, protocols and criteria were fixed before measuring** and their fingerprint was recorded; later corrections are reported separately.

## 4. Results
1. **Global validation close to chance.** Per-site AUC 0.58 (range 0.27 to 0.89 depending on the target); recall in the top 5 % 0.17. [validation/validation.md](validation/validation.md)
2. **No dimension is conclusively validated.** With 1 to 3 analogs per group, the minimum attainable p is 0.20. Geology points in the right direction on the Moon (+0.53) and Mars (+0.97), with very few cases. [validation/per-aspect-validation.md](validation/per-aspect-validation.md)
3. **Mars ice fails where it should succeed** (Dry Valleys, −0.75): Earth snow does not measure dryness. We tested soil moisture (GLDAS) with a criterion fixed beforehand; it does not improve. [preregistrations/ice.md](preregistrations/ice.md)
4. **The little topographic signal was flat terrain.** With craters and equally flat controls, the Mars AUC drops from 0.567 to 0.494. [preregistrations/plains.md](preregistrations/plains.md)
5. **The search for more analogs for thermal and ice added none that could be evaluated.** [validation/analog-search.md](validation/analog-search.md)

## 5. Candidates
Applying the population and vegetation flags and keeping away from known analogs, the result is **two basaltic volcanic fields in desert for Mars** (Harrat ash-Shamah and Haruj), with a real geological match and only moderate topography, and **two Antarctic cells for the Moon** that only appear because they are flat and that we rate as poor analogs. [results/candidate-profiles.md](results/candidate-profiles.md) details what is similar, what is not, and the limits (gravity, atmosphere, radiation).

Novelty check ([preregistrations/novelty.md](preregistrations/novelty.md)): **Harrat ash-Shamah has already been used as an analog for planetary pits** (2018 and 2019 abstracts) and **Haruj has no study of its own as an analog** in a preregistered search (with a positive control that worked); it is the least studied candidate, although "no evidence found" does not prove absence.

## 6. Use cases
Instead of one ranking, six use-case profiles ([results/use-cases.md](results/use-cases.md)): only the basaltic terrain of Mars gives a defensible recommendation (the profile candidates); mobility gives moderate matches, and the cold and ice cases show the limits of the Earth as an analog.

## 6a. Extended validation and stability
With a frozen set of 23 analogs ([validation/extended-validation.md](validation/extended-validation.md), preregistered protocol): **Moon u = 0.595 (CI 0.545 to 0.644), above chance by a small margin; Mars u = 0.564 (CI 0.448 to 0.678), cannot be claimed.** The model recovers arid, volcanic and impact analogs and **fails on cold and ice ones**. Geology is the only aspect with signal, and Mars ice fails consistently (−0.51). The two Mars candidates are **robust** to weights, PCA and sample ([validation/stability.md](validation/stability.md)): Harrat ash-Shamah stays in the best 5 % in 100 % of the replicates and Haruj in 79 %, although robustness is not validity.

**Thermal inertia (preregistered experiment, not adopted):** adding a thermal-inertia dimension (TES on Mars, MODIS proxy on Earth) **worsened** the Mars result (−0.081, CI −0.133 to −0.025): it improves cold analogs and worsens arid ones ([preregistrations/thermal-inertia.md](preregistrations/thermal-inertia.md)).

**Infrared emissivity for basalt (preregistered experiment, discarded in the first phase):** the MODIS index detects quartz sand seas, not basalt (AUC 0.69; coverage 64 %), just as ASTER did before. Geology remains GLiM ([preregistrations/emissivity.md](preregistrations/emissivity.md)).

**Multi-scale topography and calibration with target variability (two preregistered experiments, neither adopted):** the roughness exponent changes nothing measurable (differences of ±0.01 with intervals of ±0.05; [preregistrations/multiscale.md](preregistrations/multiscale.md)), and calibrating the distance with the site's heterogeneity slightly worsens the global result (−0.016 on the Moon and −0.005 on Mars; [preregistrations/variability.md](preregistrations/variability.md)). Neither beats chance in the crater test with a flatness control.

**Two analog groups, cold and warm (preregistered experiment, not adopted):** with weights of their own for the cold group the five cold analogs improve (+0.023, p = 0.031) but remain below chance (u = 0.310). **Correction:** the cause is not the snow variable: the polar Mars targets (Phoenix and Arcadia) **have no ice data** and the test could not succeed ([preregistrations/cold-warm-groups.md](preregistrations/cold-warm-groups.md), [preregistrations/models.md](preregistrations/models.md)).

**Earth-to-Earth analog model and consensus (preregistered, not adopted):** scoring by similarity to the known analogs does not beat chance overall (Mars 0.499; Moon 0.465), and the minimum-consensus worsens; but the Earth-to-Earth model **does recognise the cold analogs** (u = 0.743) that the main model does not (0.191), while the main model recognises the warm ones (0.671 versus 0.418): they are complementary ([preregistrations/models.md](preregistrations/models.md)).

**Shallow-ice targets with published evidence ([preregistrations/shallow-ice.md](preregistrations/shallow-ice.md)):** 8 Mars sites with exposed ice (coordinates from Dundas et al. 2021) + Phoenix. **Both preregistered criteria are met** (cold analogs u 0.753, CI 0.672 to 0.829; difference with the base +0.352, CI +0.309 to +0.394), so the permafrost variable is **adopted, for the cold use case only**: on the global score it worsens (−0.087, CI −0.147 to −0.023), the effect is partly by construction (binary class), the cold candidates are ice sheets, and the neutron index only recognises 4 of the 8 sites.

**A real permafrost map instead of the temperature rule ([preregistrations/permafrost-map.md](preregistrations/permafrost-map.md)):** with the Obu et al. (2018) map as the ground-ice class, the 14 cold analogs rise clearly (u 0.683, CI 0.512 to 0.840; difference with the base +0.244, CI +0.100 to +0.391) and the 6 candidates are ice-free land with probable permafrost (north-east and north Greenland, Baffin, Canadian Arctic). **It meets the three preregistered criteria and is integrated for the cold use case only** (a new case in the app); the global score does not change. The candidates are known permafrost regions, not discoveries; the map only covers the northern hemisphere.

**Third analog set, from the ESA expert catalogue ([preregistrations/validation-set-3.md](preregistrations/validation-set-3.md)):** 13 new sites chosen by a mechanical rule over the CAFE catalogue (2012). **Mars: u = 0.577 (CI 0.423 to 0.726; 12 analogs), does not pass the criterion.** Moon (7 new + Teide): u = 0.565 (CI 0.515 to 0.611), passes narrowly. The "A or B" union is not adopted (Mars +0.011; Moon −0.123). With the three sets together (descriptive): **Mars 0.595 (0.515 to 0.670; 40 analogs), Moon 0.583 (0.545 to 0.619; 20)**: the method discriminates somewhat better than chance, not by much. Cold, hydrothermal and lake sites fail.

**Permafrost without ice sheets ([preregistrations/cold-permafrost.md](preregistrations/cold-permafrost.md)):** a rule (mean annual snow ≥ 0.9 = ice sheet) improves the test with cold analogs (u 0.778, CI 0.558 to 0.908; +0.378, CI +0.229 to +0.500; the Dry Valleys are excluded because of MODIS snow) but **fails the candidate credibility check** (one falls in Antarctica and three in Greenland): **it is not integrated and the cold case is left without credible candidates**. Exploratory: without Antarctica and Greenland, Baffin Island, the Canadian Arctic, northern Tibet and the Pamir come out as hypotheses. A glacier mask and a permafrost map are needed.

**Second analog set, independent and preregistered ([preregistrations/validation-set-2.md](preregistrations/validation-set-2.md)):** 9 new sites fixed before measuring (8 for Mars, 1 for the Moon). **The base model is confirmed on Mars: u = 0.698 (CI 0.563 to 0.821)**; the Moon has no verdict (1 analog). Five of the eight are deserts, dunes or volcanoes (what the model recognises well) and the two ice sites (Fairbanks 0.38 and Tuktoyaktuk 0.45) are the lowest. The "A or B" union is **not adopted** (u 0.716, difference with A +0.006, CI −0.079 to +0.118) and neither is the **permafrost variable** (−0.058, CI −0.106 to −0.008: it worsens). The additional ice targets (SWIM) were not run for lack of a list of sites with verifiable coordinates (later completed in [preregistrations/shallow-ice.md](preregistrations/shallow-ice.md)).

**Polar ice on Mars with Odyssey neutrons and a permafrost variable (preregistered, not adopted):** a hydrogen index was obtained for all targets (validity gate ρ = 0.816; Phoenix clearly ice-rich) and a "ground ice" class comparable to terrestrial permafrost was tested. It improves the direction for cold analogs (+0.060) but is not conclusive (CI −0.017 to +0.127) ([preregistrations/polar-ice.md](preregistrations/polar-ice.md)).

## 6b. Aspect atlas and processes
[results/aspect-atlas.md](results/aspect-atlas.md) evaluates each dimension separately with a confidence label that comes from the measured results (none reaches "high"). [context/processes.md](context/processes.md) treats three processes (volcanism and lava tubes, aeolian transport, subsurface ice) as qualitative case studies: only the volcanic one connects with our results.

## 6c. What we learned
- **A context dimension was missing, not fine-tuning:** without vegetation, the first Mars candidates were rainforests.
- **Variables do not mean the same across bodies:** snow ≠ subsurface ice; monthly terrestrial temperature does not reproduce Mars' daily extremes.
- **With 4 to 8 analogs per body no result can be conclusive**; the bottleneck is validation, not computation.
- **Rigour was the contribution:** protocols fixed before measuring, controls against the flat-terrain bias, and negative results reported.

## 7. Limits
Few analogs; confusion with flat, stable terrain; different semantics between bodies; Mars without thermal data; dust/wind, caves and illumination not covered ([context/unmodeled-dimensions.md](context/unmodeled-dimensions.md)); population data from 1990-2010; coordinates of several analogs without a primary source ([validation/coordinate-verification.md](validation/coordinate-verification.md)). Earth also does not reproduce the reduced gravity, the lunar vacuum, Mars' thin atmosphere or its radiation.

## 8. How to reproduce
`pip install -e ".[app,dev]"`, `python -m astroatlas.pipeline` and `streamlit run app/streamlit_app.py`. The app runs without downloading anything thanks to `demo_data/`. Details in the [README](../README.md).

## 9. Next steps
Expand the analog list with primary sources and define before measuring which targets apply to each aspect; resolve Mars thermal; add a dryness variable with a Martian counterpart; check the pending coordinates and licences.
