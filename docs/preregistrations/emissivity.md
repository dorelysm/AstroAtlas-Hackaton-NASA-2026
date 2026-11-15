# Preregistration: infrared emissivity index for geology (15 Nov 2026, written BEFORE downloading or computing anything)

## Prior warning (a correction to what was proposed)
This index was proposed as something that "would distinguish basalt from quartz sand better than GLiM". **That ignored an earlier test of the project** ([../reference/data-sources.md](../reference/data-sources.md), "ASTER GED, tested and discarded"): with the ASTER mafic index, dark lava (Craters of the Moon, Harrat Khaybar) has a **flat, high-emissivity spectrum (~0.97)** that cannot be told from ice, water or vegetation; only 9 % of the cells had data; and the contrast mask biased towards the felsic.
The MODIS emissivity contrast (bands 29, 31 and 32) mostly detects **quartz and felsic minerals** (a low emissivity at 8.55 µm), not basalt. "No quartz" is not "basalt". **It is expected to fail for the same reason**, and this preregistration is designed to check it cheaply before spending more.
**Change of scope from the initial proposal:** no gridded products of Mars (TES) or of the Moon (Diviner, 32 pixels/degree, only ±60°) were found that measure the same band as MODIS, and calibrating between different bands would require a spectral model we do not have. That is why **emissivity is not compared between bodies**: the index is used only to **better measure Earth's basalt fraction** (today GLiM at 0.5°, which gives 0.14 at Pinacate and 0 at Etna), leaving the Moon and Mars side intact (FeO proxy).

## Phase 1: feasibility (costs ≈ 70 MB, a single month)
**Data:** NASA MODIS MOD11C3 v061, July 2019 (emissivity bands `Emis_29`, `Emis_31`, `Emis_32`; emissivity = DN × 0.002 + 0.49; fill 0). The file is deleted after reducing it. It is a single month: soil emissivity varies little with the season (not verified).
**Index:** `C = E29 − (E31 + E32)/2` (spectral contrast, which reduces the effect of overall emissivity from vegetation and moisture). **Higher C = more mafic** (quartz lowers E29, so it gives a more negative C). Median of the valid pixels in a ±25 km window.
**Places of known lithology** (general knowledge; coordinates to verify; **those within < 100 km of any of the 23 frozen analogs are excluded**, to avoid information leakage):
- *Basalt (10):* Harrat Rahat (23.5; 39.8), Harrat Khaybar (25.6; 39.9), Harrat Uwayrid (26.1; 37.8), Deccan (19.0; 74.5), Karoo/Lesotho (−29.5; 28.5), Paraná (−25.0; −52.0), Columbia River (46.0; −119.5), Ethiopian plateau (10.0; 38.0), Hekla (64.0; −19.7), Jebel Marra (12.9; 24.3).
- *Non-basalt (10):* Rub al Khali (21.0; 51.0), Great Sand Sea (27.0; 25.0), Namib sand sea (−24.8; 15.3), Taklamakan (38.9; 83.4), Simpson Desert (−25.5; 137.0), Nebraska Sand Hills (42.0; −101.5), Canadian Shield (52.0; −88.0), Alps (46.5; 9.0), Amazonia (−3.0; −60.0), Kalahari (−23.0; 22.0).
**Gates (all must be met; otherwise it stops and Phase 2 is not run):**
1. **Coverage:** valid index in ≥ 90 % of the 20 lithology places and in ≥ 80 % of the 951 grid cells (ASTER gave 9 %).
2. **Discrimination:** AUC of C to separate basalt from non-basalt ≥ 0.80 (in the sense "higher C = basalt").
3. **Small fields:** of the basaltic sites that GLiM underestimates (basalt fraction < 0.3 or no data: Pinacate, Etna, Lanzarote), at least 2 of 3 have C above the median of the 10 non-basalt places.

## Phase 2: only if Phase 1 passes
Download the 12 months of 2019 (≈ 840 MB), average C and calibrate `p_basalt = logistic(C)` with the 20 lithology places (**not with the analogs**). New Earth feature `geo__basalt_frac` = `p_basalt`, instead of the GLiM one; Moon and Mars unchanged.
**Evaluation (on the 23 frozen analogs, same measures as [../validation/extended-validation.md](../validation/extended-validation.md)):** paired difference per analog of the mean u of "all" between the model with `p_basalt` and the base, with a 95 % bootstrap CI, for the Moon and for Mars, plus "only geology".
**Success criterion:** the lower bound of the paired difference of "all" is **> 0 in at least one body** and the upper bound is **not < 0 in any**. If it is not met, it is not adopted.

## What is not done
The gates, the index, the windows, the month or the list of places are not changed after seeing the results; any variant is reported separately as exploratory.

## Limits known beforehand
The 20 coordinates come from general knowledge; MODIS has 5 km pixels that mix soil, vegetation and water; ice and water are masked; a single month; and the relation between emissivity at 8.55 µm and composition depends on moisture and vegetation.

## Phase 1 result (preregistration hash `82bb4a7f27a3e299`; no changes to the protocol)
One month of MOD11C3 (July 2019, downloaded and deleted), 20 places of known lithology, 951 grid cells and 3 small fields that GLiM underestimates.

| Gate | Threshold | Result | Passes? |
|---|---|---|---|
| 1. Coverage | ≥ 90 % of places and ≥ 80 % of cells | 100 % of places, **64.2 % of cells** | **No** |
| 2. Discrimination (AUC basalt versus non-basalt) | ≥ 0.80 | **0.69** | **No** |
| 3. Small fields above the "non-basalt" median | ≥ 2 of 3 | 3 of 3 (Pinacate −0.044, Etna −0.031, Lanzarote −0.053; median −0.074) | Yes |

**Verdict: Phase 1 fails (two gates out of three). By the protocol it stops here: the 12 months are not downloaded, Phase 2 is not calibrated or evaluated, and the model does not change.**

## What the index showed (matches what was expected)
- **It separates quartz sand seas very well:** Rub al Khali −0.21, Great Sand Sea −0.18, Namib −0.16, Simpson −0.14.
- **It does not separate basalt from the rest:** the 10 basaltic places lie between −0.006 and −0.061, the same range as the places **covered by vegetation or without quartz** (Alps −0.006, Sand Hills −0.013, Canadian Shield −0.013, Amazonia −0.015). That is, it detects "there is bare quartz", not "there is basalt". Gate 3 is met because the three small fields are not sand seas, not because the index recognises them as basalt.
- **Coverage:** 36 % of the cells have no valid index (ice, water, fill), far higher than ASTER's 9 % but below the threshold.

With this, **two infrared emissivity products** (ASTER and MODIS) are not useful to measure Earth's basalt. Geology stays GLiM, with its known limit (it underestimates basalt in small fields and gives the subglacial rock under ice).
