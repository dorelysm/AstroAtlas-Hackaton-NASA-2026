# Preregistration: second, independent set of analogs (15 Nov 2026, written BEFORE searching and computing anything)

**Why:** with 23 analogs almost all tests were inconclusive, and several ideas were tested on the same 23 (risk of fitting the test). A second set, searched and frozen before measuring, is the only way to check independently (a) whether the base model works, (b) the "A or B" union and (c) the permafrost variable.
**Model A:** the frozen one (commit `0b8a0a2`). **First set (reference):** the 23 of [analog-validation.md](analog-validation.md). Nothing about them is changed.

## Inclusion criteria (the same as in the first set, plus an independence rule)
1. An open source **names the site as a terrestrial analog of the Moon and/or Mars** (agency, article or peer-reviewed abstract, or an institute/university dedicated to analogs).
2. **Locatable site** with a coordinate of reasonable uncertainty (≈ ≤ 10 km), with its origin noted (**TO VERIFY** if it comes from general knowledge or Wikipedia).
3. **No model result is consulted** to decide what enters.
4. **Independence:** a candidate **within 100 km** of any of the 23 analogs of the first set, or of another already accepted candidate (the one with the stronger source enters), **is excluded**.
5. Aspect labels only if the source text names the aspect (same rules as before).

## Searches (8, fixed now; no queries are added to look for more sites after seeing results)
(1) `Wudalianchi volcanic field Mars analog` · (2) `Iceland basaltic terrestrial analog Mars field site Holuhraun Kverkfjoll` · (3) `Mars analog dunes Namib Sahara Gobi field site aeolian` · (4) `Mars Desert Research Station Utah analog field site Hanksville` · (5) `Mars analog Oman Dhofar sabkha desert field site` · (6) `Mars analog Pilbara Western Australia field site` · (7) `Mars analog ice-rich permafrost field site Alaska Siberia Yukon Banks Island` · (8) `lunar analog Kamchatka Tolbachik Tenerife Teide volcanic field site Moon`.
Only follow-up queries are made to obtain coordinates or the cited reason of sites already found. The list is frozen (with a hash) **before** computing features or scores.

## Evaluation (fixed; the new set is the only one that decides)
Same 50 km windows and same dimensions as the first set. Computed in each body with ≥ 8 applicable new analogs.
- **V1, base model A:** mean u over the 14 Mars targets (or the Moon's), 95 % bootstrap CI over the new analogs. **It replicates whether the model works:** lower bound > 0.5.
- **V2, "A or B" union:** `s(c) = max(P_A(c), P_B(c))`. `P_A`: percentile of model A's mean score over the targets (as in [models.md](models.md)). `P_B`: Earth-to-Earth analog model with **the 23 analogs of the first set as the only references** (the new ones are not used as references when evaluated; references within 500 km of the evaluated analog are excluded). **It is adopted only if:** lower bound of the mean u > 0.5 **and** paired difference with `P_A` with a lower bound > 0 in at least one body and no upper bound < 0.
- **V3, permafrost variable** (classes and thresholds of [polar-ice.md](polar-ice.md), unchanged): paired difference of the mean u of "all" on Mars against the base, lower bound > 0 (primary); and new cold analogs (rule of [cold-warm-groups.md](cold-warm-groups.md)) against cold targets with cold-model weights, u with a lower bound > 0.5 (secondary, only if there are ≥ 5 new cold analogs; if fewer, reported without a verdict). It is adopted only if both are met.
- **Combined set (exploratory):** the 23 + the new ones, only as a description; it decides nothing.

## What is not done
Models, thresholds, weights, radii or criteria are not changed after seeing results; any variant is reported separately as exploratory.

## Limits known beforehand
Coordinates to verify; the final set may be smaller than 8 on the Moon (then the Moon is reported without a verdict); selection bias of the 8 queries; the 0.5° GLiM geology underestimates small basalt fields; monthly MODIS 2019 for thermal.

## Frozen list (annex, written after the 8 searches and BEFORE computing any feature or score)
Hash of the protocol before this annex: `7645d89cbe9a9476`. `docs/catalog/analogs_set2.csv` sha256 `ec1a07d1da462b70` (9 sites); `docs/catalog/aspects_set2.csv` sha256 `9612fd97ab33f8d6` (3 labels).
**Included (9):** Wudalianchi, Namib/Sossusvlei, Bruneau Dunes, Maspalomas, Mars Desert Research Station, Strelley Pool (Pilbara), CRREL Permafrost Tunnel (Fairbanks), Tuktoyaktuk and Teide (Tenerife; the only one for the Moon). Minimum distance to any of the earlier 23: 185 km; among new ones, the nearest pair (Maspalomas-Teide) is 117 km apart.
**Excluded and why:** Holuhraun (~20 km from Askja, which is already in) and Kverkfjöll (it does not appear as a Mars analog); Dhofar/AMADEE-18 (the source says the exact location was kept in reserve; it does not meet criterion 2); Tengger and Sahara (the source does not present them as analogs); north-eastern Siberia (a region, not a site) and Banks Island/Yukon (no source); Kamchatka/Tolbachik (the source treats it as a Venus analog, not a lunar one); Dresser/North Pole (Pilbara) for being < 100 km from Strelley Pool; Pingo Canadian Landmark for being < 100 km from Tuktoyaktuk.
**Consequences known beforehand:** there is only **1 new Moon analog**, so the Moon **has no verdict** in this set; Mars has 8 (exactly the minimum). There are only **2 new cold analogs**, so the secondary test of V3 is reported **without a verdict**. Coordinates to verify (Strelley Pool with an uncertainty perhaps of 10-20 km).

## Results (protocol hash `7645d89cbe9a9476`; list frozen with the annex hashes; no changes to the protocol after seeing the numbers)
Code: `src/astroatlas/validation2.py` (`python -m astroatlas.validation2 --build`, then without `--build`). Thermal and snow from MODIS 2019 (a download of about 900 MB reduced and deleted), GLiM geology (missing at 1 of the 9 sites).

| Test | Body | Analogs | Result | Met? |
|---|---|---|---|---|
| **V1 base model A** | **Mars** | 8 | **u = 0.698 (CI 0.563 to 0.821)** | **Yes** (lower bound > 0.5) |
| V1 base model A | Moon | 1 (Teide) | u = 0.525 | No verdict (1 analog) |
| **V2 "A or B" union** | Mars | 8 | u = 0.716 (0.616 to 0.833); difference with `P_A` **+0.006 (−0.079 to +0.118)** | **No** (the u is met, but the difference with A has no lower bound > 0) |
| V2 union | Moon | 1 | 0.304 | No verdict |
| **V3 permafrost, primary** | Mars "all" | 8 | base 0.698 → 0.640; **difference −0.058 (−0.106 to −0.008)** | **No** (and the effect is significantly **negative**) |
| V3 secondary | Mars, cold | 2 | Fairbanks 0.39 → 0.43; Tuktoyaktuk 0.71 → 0.61 | No verdict (< 5 cold) |

**Preregistered verdicts:** the base model **is confirmed on Mars with an independent set**; the **A-or-B union is not adopted** (it does not demonstrably improve on A: +0.006); the **permafrost variable is not adopted** (it worsens). The Moon has no verdict (1 new analog).

### Per analog (Mars; u of model A, u of model B with the earlier 23 as reference, u of the union)
Bruneau 0.92 / 0.41 / 0.98 · Maspalomas 0.99 / 0.38 / 0.98 · MDRS 0.79 / 0.77 / 0.70 · Namib 0.77 / 0.56 / 0.68 · Strelley Pool 0.72 / 0.63 / 0.63 · Wudalianchi 0.65 / 0.60 / 0.54 · Tuktoyaktuk 0.46 / 0.67 / 0.57 · **Fairbanks (permafrost) 0.30 / 0.76 / 0.66**. Mean annual temperatures: Fairbanks 270.7 K and Tuktoyaktuk 263.7 K (both in the permafrost class); all the others ≥ 275 K.

### Honest reading
- **The good:** with 8 analogs the model had never seen and that were not used to tune anything, the mean u on Mars is 0.70 with a lower bound of 0.56. It is the first independent confirmation that the base model beats chance on Mars. The first set gave 0.564 (not conclusive); the difference between 0.56 and 0.70 is within the noise to be expected with 20 and 8 analogs, so it must not be read as the model having improved.
- **What must not be oversold:** 5 of the 8 are deserts, dunes or volcanic fields (exactly what the model recognises well: Bruneau and Maspalomas give 0.92 and 0.99 for being flat dunes, again the flat-terrain effect of [plains.md](plains.md)); the **two ice analogs (Fairbanks, Tuktoyaktuk) are the lowest of model A (0.30 and 0.46)**, so the weakness with cold places repeats on new data. The coordinates are to be verified.
- **The A-or-B union:** the result is what its construction predicts (B recovers the cold ones: Fairbanks rises from 0.30 to 0.66) but at the cost of dropping others (Namib from 0.77 with A to 0.68 with the union, Wudalianchi from 0.65 to 0.54), and the net effect over A is zero. **There is no evidence that combining improves.**
- **Permafrost:** with two cold analogs that do have a permafrost class, the variable **does not improve** and the global effect is negative (−0.058): replacing "snow" with a binary class loses information on the 6 warm analogs (which move to a "no permafrost" class identical to that of most targets). With this result there is no reason to test it again with this design.

## Additional shallow-ice targets on Mars (SWIM): first attempt without a list; later solved with another source (see [shallow-ice.md](shallow-ice.md))
An attempt was made to obtain a list of shallow-ice sites with verifiable coordinates (SWIM project, USGS/PSI; scarps of Dundas et al. 2018). The open sources found give the summary (shallow ice poleward of ~40°, scarps at 55-58° latitude) but **not a list of sites with coordinates**; those are in supplementary tables or in the PDS that could not be obtained and checked. **No coordinates were invented.** Discarded alternative: defining the ice targets with the neutron index itself (`H`), because it would be circular (the "ice-rich" class already comes from that data). In addition, with the V3 result (the permafrost variable worsens on independent data) adding targets loses priority. Pending at that time: obtain the table of Dundas et al. (2018) or Morgan et al. (2021) and, only if a verifiable list comes out, preregister a version with those targets (done afterwards with the 8 coordinates of Dundas et al. 2021).
