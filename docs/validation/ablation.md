# Ablation by dimension (14 Nov 2026)

Question: which of the four dimensions (topography, thermal, ice, geology) help the model recover the known terrestrial analogs? Code: `src/astroatlas/ablation.py` (`python -m astroatlas.ablation`); full results in `data/results/ablation_*.csv` (not versioned; the summary is in `demo_data/results/ablation_summary.csv`).

> **Note (14 Nov 2026):** the tables in this document are from the first version (**15 lunar sites**). The Moon later moved to **21 sites** (LROC tables) and everything was repeated: see the section "Repetition with 21 lunar sites" below. The Mars figures do not change.

## Method
- For each of the 29 targets (15 lunar, 14 Martian) the Earth is scored with: **all** dimensions, **one only** and **all but one**.
- Metric `u` = probability that a known analog scores higher than a typical grid cell (0.5 = chance). Analogs are scored with the same 50 km windows as the targets.
- **Statistical care:** all targets of a body are evaluated against **the same analogs** (4 on the Moon, 8 on Mars). The independent unit is the analog, not the target, so the 95 % confidence intervals come from resampling the **analogs**. With so few, the intervals are wide.

## Results
**Mars** (14 targets, 8 analogs):

| Configuration | Mean u | 95 % CI | Change vs "all" |
|---|---|---|---|
| all | 0.50 | 0.32 – 0.69 | — |
| only ice | **0.62** | 0.38 – 0.86 | **+0.10** (0.02 to 0.18) |
| only topography | 0.45 | 0.34 – 0.56 | −0.06 (−0.22 to 0.10) |
| only geology | **0.14** | 0.00 – 0.42 | −0.32 (−0.60 to 0.01) |
| without topography | 0.60 | 0.32 – 0.83 | +0.07 (−0.02 to 0.16) |
| without ice | 0.44 | 0.30 – 0.60 | −0.06 (−0.21 to 0.08) |
| without geology | 0.51 | 0.36 – 0.65 | +0.01 (−0.04 to 0.04) |
| without thermal | 0.50 | 0.32 – 0.69 | 0.00 (Mars has no thermal) |

**Moon** (15 targets, 4 analogs):

| Configuration | Mean u | 95 % CI | Change vs "all" |
|---|---|---|---|
| all | 0.60 | 0.52 – 0.68 | — |
| only thermal | 0.64 | 0.42 – 0.86 | +0.04 (−0.26 to 0.31) |
| only topography | 0.58 | 0.42 – 0.71 | −0.02 (−0.10 to 0.07) |
| only geology | 0.44 | 0.18 – 0.60 | −0.17 (−0.50 to 0.06) |
| only ice | 0.68 | — | only 2 targets have ice (Shackleton, Malapert); not conclusive |
| without thermal | 0.57 | 0.48 – 0.62 | **−0.04** (−0.04 to −0.03) |
| without topography, without ice, without geology | 0.60 – 0.62 | wide | ≈ 0 |

## What they say (and what they do not)
1. **With 4 and 8 analogs it cannot be claimed that any combination robustly beats chance.** The full model gives 0.50 on Mars and 0.60 on the Moon (the latter with an interval barely above 0.5, and only 4 analogs).
2. **Mars geology is counter-productive (u = 0.14).** The basalt proxy saturated at 1.0 at almost all Martian sites (median 1.00, minimum 0.89), so it looks for basaltic cells on Earth. Six of the seven analogs with data have basalt 0 and score 0.00. Only Craters of the Moon, basaltic, comes out high (0.97). This does **not** say Mars is not basaltic (it is) but that this variable does not discriminate between Martian sites and that the listed analogs are not analogs for their geology.
3. **Mars ice works as a "desert without snow" detector.** Martian sites have 3 to 7 % water, and the Earth's mean annual snow is ~0 in deserts. That is why deserts score high (Death Valley 0.97, Atacama 0.93, Lanzarote 0.92, Río Tinto 0.91) and polar sites low (Dry Valleys 0.00, Svalbard 0.31, Haughton 0.39). It is a real but **accidental** signal: it does not compare water with water. And it penalises the Dry Valleys, the most classic Mars analog, because MODIS gives them mean snow 1.00.
4. **Thermal helps a little on the Moon** (removing it lowers `u` by 0.04, consistently), but the Earth does not reach lunar temperatures: the effect comes from ordering cells, not from matching them.
5. **Topography adds no clear signal** on either body.

## Limits of this test (important)
- **The analog list does not say in which aspect each site is an analog.** Atacama and the Dry Valleys are for their dry, cold climate; Mauna Kea, Askja and Craters of the Moon for their basalt; Haughton for being a polar impact crater; Río Tinto for its water chemistry. Requiring *every* dimension to recover *all* analogs mixes different criteria and pushes results towards chance.
- There are only 4 lunar analogs, and the lunar targets share the same thermal profile (~390 K except the polar ones), which adds little variation.
- These are several comparisons with little data: small differences (±0.05) are not reliable.

## Repetition with 21 lunar sites (14 Nov 2026)
After updating the Moon with the LROC tables (6 new sites and corrected Surveyors) the ablation was repeated. **Mars does not change** (the same 14 targets and the same numbers). The Moon's analogs are still 4: the only thing that changed is the set of lunar **targets** (from 15 to 21), not the list of analogs they are measured against.

| Moon, mean u (95 % CI) | 1st version (15 sites) | After flat-terrain fix (15) | **Now (21 sites)** |
|---|---|---|---|
| all | 0.60 (0.52 to 0.68) | 0.58 (0.49 to 0.67) | **0.64 (0.56 to 0.68)** |
| only thermal | 0.64 (0.42 to 0.86) | 0.64 (0.42 to 0.86) | 0.64 (0.42 to 0.86) |
| only topography | 0.58 (0.42 to 0.71) | 0.60 (0.43 to 0.73) | 0.60 (0.42 to 0.75) |
| only geology | 0.44 (0.18 to 0.60) | 0.43 (0.17 to 0.60) | 0.51 (0.20 to 0.71) |
| without thermal (change vs "all") | −0.04 (−0.04 to −0.03) | −0.02 (−0.03 to −0.01) | −0.02 (−0.03 to −0.02) |
| only ice (only 2 targets with data) | 0.68 | 0.68 | 0.68 |

**How to read it:**
- The full model for the Moon rises to 0.64 and its lower bound (0.56) exceeds 0.5 for the first time. **It must not be read as an improvement of the model**: the analogs are the same 4, and the average is over more targets, most of them equatorial maria similar to each other. With 4 analogs the interval is still fragile.
- Thermal remains the only dimension with a consistent effect (removing it lowers 0.02).
- Lunar geology rises from 0.43 to 0.51 when basaltic maria are added (Luna 16, Chang'e 3): it now neither improves nor worsens chance.

## Recommended next step: per-aspect validation
Label each analog with the dimension(s) for which it is considered an analog, **taking the labels from the sources already cited in `docs/catalog/known_analogs.csv` and fixing them before measuring again** (otherwise the label is being fitted to the result, and this ablation has already been seen). Then each dimension would be required to do only what applies to it: geology must recover the basaltic analogs; ice and thermal, the cold and dry deserts; topography, the craters. The list should also be expanded beyond 4 and 8 analogs. This was done in [per-aspect-validation.md](per-aspect-validation.md).
