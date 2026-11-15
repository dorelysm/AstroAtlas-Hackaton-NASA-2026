# Per-aspect validation (14 Nov 2026)

Question: does each dimension recover the known analogs **that are analogs for that aspect**? It is the correction proposed by the global ablation ([ablation.md](ablation.md)), which required every dimension to recover all analogs even though some are analogs for their climate and others for their basalt.

Code: `src/astroatlas/aspect.py` (`python -m astroatlas.aspect`). Labels: `docs/catalog/analog_aspects.csv`. Full results: `data/results/aspect_summary.*` (not versioned).

> **Note (14 Nov 2026):** the tables in this document are from the first version (**15 lunar sites**). The Moon later moved to **21 sites** (LROC tables) and everything was repeated: see the section "Repetition with 21 lunar sites" below. The Mars figures do not change.

## How it was done (and what was fixed before measuring)
- **Labels fixed before measuring.** They come only from what the sources already cited in `docs/catalog/known_analogs.csv` say. File fingerprint: **sha256 `ca45726975642cb2…`** (14 Nov 2026, 22:38), recorded in the results. The main analysis was also declared beforehand: the "source + note" level.
- **Three evidence levels per label:** *source* (the cited page names the aspect: e.g. NASA says the Dry Valleys are cold and dry), *note* (only our descriptive note says it) and *general* (knowledge without an open source). Each cumulative level is evaluated to see whether the result depends on how much the labels are trusted.
- **Test:** with dimension D **alone**, we compare how analogs labelled with D score (u = probability of beating a typical cell; 0.5 = chance) against those that have labels but not D. Analogs without labels belong to no group.
- **Statistics:** with 1 to 6 analogs per group an **exact permutation test** (one-sided) and a bootstrap over the analogs are used, with no normality assumptions.

## Results (main analysis: source + note)
`gap` = u of the aspect's analogs − u of the others; positive is expected.

| Body | Dimension | With the aspect | Without it | u with | u without | gap (95 % CI) | permutation p |
|---|---|---|---|---|---|---|---|
| Mars | geology | Craters of the Moon | 4 analogs | 0.97 | 0.00 | **+0.97** | 0.20 |
| Mars | topography | Lanzarote, Death Valley, Haughton | 3 | 0.52 | 0.38 | +0.14 (−0.12 to 0.39) | 0.25 |
| Mars | ice | Dry Valleys | 5 | 0.00 | 0.75 | **−0.75** (−0.94 to −0.53) | 1.00 |
| Mars | thermal | — | — | not evaluable: Mars has no thermal data | | | |
| Moon | geology | Mauna Kea, Askja, Craters of the Moon | Haughton | 0.57 | 0.03 | **+0.53** (0.47 to 0.57) | 0.25 |
| Moon | topography | Haughton | 3 | 0.65 | 0.56 | +0.08 (−0.10 to 0.30) | 0.50 |
| Moon | thermal | Haughton | 3 | 0.28 | 0.76 | **−0.48** (−0.59 to −0.30) | 1.00 |
| Moon | ice | — | — | not evaluable: no lunar analog carries the ice label | | | |

**Sensitivity to the evidence level.** With source labels only: Mars geology +0.97, topography +0.06, Mars ice −0.84; the Moon is not evaluable (a single labelled analog per group). Adding general-knowledge ones: geology +0.97 (Mars) and +0.53 (Moon), topography +0.11 and +0.08, Mars ice goes to −0.21 (Atacama 0.93 raises the group, the Dry Valleys 0.00 lower it). **The direction of every result does not change with the level.**

## What they say

1. **No dimension is validated in a statistically conclusive way, and it could not be.** With 1 positive or 1 negative per group, the minimum attainable p is 0.20 to 0.50. It is a limit of the number of analogs, not of the model.
2. **Geology goes in the right direction on both bodies** (Moon +0.53, Mars +0.97): analogs that are analogs for their basalt score high and those that are not score low. It is the most consistent signal, but it rests on 1 to 3 analogs per group. On Mars only Craters of the Moon counts, because Lanzarote has no geology data (no 0.5° grid cell for a small island).
3. **Mars ice fails exactly where it should succeed (−0.75).** The Dry Valleys are the classic example of a cold, dry place, but MODIS gives them mean snow 1.00 (ice and glaciers), while Martian sites have 3 to 7 % water. Earth "snow" does not measure dryness. It is the clearest failure and confirms the semantics warning in [../reference/data-sources.md](../reference/data-sources.md): that variable does not represent what the aspect asks for.
4. **Lunar thermal comes out against (−0.48), but with a single reference.** Only Haughton carries the label (cold polar crater, by note), and it is compared with 15 lunar targets almost all equatorial (~390 K). A cold polar analog cannot resemble an equatorial site thermally: **the analogy would only make sense for the two polar targets** (Shackleton and Malapert). This test averages over all targets, which mixes cases where the aspect does not apply.
5. **Topography shows a small difference in favour** (+0.14 and +0.08) with intervals that include zero: no information.

## Limits of this test
- **Very few analogs per group** (1 to 3 positives). Bootstrap intervals with 1 element are degenerate (e.g. the Mars geology one collapses to 0.97) and must not be read as certainty.
- **Targets are not filtered by relevance.** For each aspect all the body's targets are averaged, even if the aspect only applies to some (thermal: only the polar ones). Filtering them after seeing the results would be fitting the test to the data; doing it properly requires deciding the relevance criterion beforehand.
- **The "note" and "general" labels are weak.** Mauna Kea, Askja and Svalbard have an unverified reason for the analogy; Río Tinto has no measurable aspect (chemistry and habitability) and only serves as a negative.
- **More than one main analysis was not tried**, but each dimension is looked at separately (4 dimensions × 2 bodies): an isolated p = 0.2 must not be taken as a finding.

## Existing databases of analog sites (search of 14 Nov 2026)
**There is no NASA database with a catalogue of analog sites.** The closest:

| Resource | Who | Content | Access | Status |
|---|---|---|---|---|
| **Known Terrestrial Analog Sites for Planetary Science** (Hunter 2020, DOI 10.5066/P9J72921) | USGS Astrogeology | **192 points** (shapefile `TerrestrialAnalogs.shp`). Fields: `Name`, `AnalogType` (only 3 values: *Impact Crater*, *Dunes*, *Volcanic Eruption*), `Lat`, `Lon` (latitude from -34.7 to 75.7: **it does not include Antarctica**) and `AnalogBody` (the extraterrestrial body for which the site was used). Limited to sites **verified with NASA-funded research** (funded by the USGS-NASA agreement of the Terrestrial Analogs Data Portal). Public domain. | the **metadata** were read (`AnalogSites_metadata.xml`, provided by the team); the DOI page on ScienceBase | **Metadata verified. Warnings from the producer itself:** "to identify areas of research, not for analysis"; the points approximate large areas and may be **up to 10 km** from the centroid; "in progress" status; it does not include all possible analogs. **The point layer had not yet been downloaded** at that time (it was later, by a team member; see below) |
| **Planetary Aeolian Analog Database (PAAD)** (Gullikson, Titus and Hunter 2023, DOI 10.5066/P9IFVZEX) | USGS | 45 dune fields; attributes: landform type, climate class, sand origin and composition, latitude, longitude, elevation, extent; CC0 | DOI page; it will be integrated into the Terrestrial Analogs Data Portal (tadp.astrogeology.usgs.gov) | Verified on the USGS page; data not downloaded |
| **Catalogue of Planetary Analogues (CAFE / CPA)** | ESA (CAFE project, Open University) | sites on the seven continents organised by lunar and Martian feature | PDF; **403 to my automatic access** | Exists according to search results at that time; content unverified (used later as the third validation set) |
| **Astrobiology Habitable Environments Database (AHED)** | NASA Ames | repository of astrobiological data and samples | web portal | It is a sample database, not a site catalogue |
| **Astrobiology research locations** | NASA | descriptions of field sites (e.g. Atacama) | page being migrated | Unverified |
| IMEWG Mars Analog Database | international group | interactive database of Mars analog sites | in development | status not confirmed |
| PTAL (ptal.eu) | European consortium | 102 analog rock samples, centred on Mawrth Vallis and Oxia Planum | web database | It is a sample database, not a site one |

**For our problem:** the USGS layer provides sites with a process category given by an authority, not by us. Its three categories only cover the **topography** (craters, dunes) and **geology** (volcanoes) aspects. **There is no cold or dryness category: thermal and ice stay without analogs with this source.**

**Category-to-aspect rule, fixed before seeing any point** (`docs/catalog/usgs_aspects.csv`, sha256 `af372c56698d6704…`, 14 Nov 2026, 22:50, before downloading the points): *Impact Crater* and *Dunes* count as the **topography** aspect and *Volcanic Eruption* as **geology**, all with evidence level "source". Each site is only evaluated against the body's targets indicated by `AnalogBody`. A known warning: "volcanic eruption" does not imply basalt, and the geology variable measures basalt fraction; a felsic volcanic site can come out badly for that reason and not because of a failure of the dimension.

## Protocol with the USGS layer (fixed on 14 Nov 2026, before computing any score)
What was seen before fixing it: only the **structure** of the data, no result. Of the 192 points, 190 are impact craters, 1 is a dune field (Grand Falls, Mars) and 1 a volcanic eruption; `AnalogBody` is empty in 191 of 192; there are 5 duplicated craters (same name, 15 to 30 km apart). The volcanic record is called "Ritland" (like a Norwegian crater) but its coordinates (64.93° N, 16.52° W) fall in Iceland, near Askja: a **labelling error by the producer**. The craters come from the Earth Impact Database, that is, they are *the confirmed craters of the Earth*, not a selection made by similarity to the Moon or Mars.

**Data:** unique craters (duplicates with the same name within 50 km are merged), plus Grand Falls, as analogs of the **topography** aspect (rule of `docs/catalog/usgs_aspects.csv`, sha256 `af372c56698d6704…`). The single volcanic record does not allow evaluating geology (n = 1): it is only reported.
**Body:** since `AnalogBody` is empty, the craters are evaluated against the Moon and Mars targets, each separately.
**Variable:** u = probability that the site scores higher than an Earth grid cell, using only the topography dimension (with the PCA), averaged over the body's targets.

**The control (to separate "crater" from "flat, stable terrain").** 200 random points on dry land, with latitude between -35° and 76° (the craters' range) uniform in the sine of latitude, longitude uniform, seed 20261114. Points within 50 km of a crater, those without a valid DEM or on flat sea, and those of ice, water or no data in GLiM are discarded. They are evaluated with the same computation.
**Main test:** `AUC_rank` = P(u of a crater > u of a control point), one-sided (Mann-Whitney), with a 95 % bootstrap confidence interval over both groups, per body. **Signal is considered to exist only if the lower bound of the interval exceeds 0.5.**
**Known limits:** craters are preserved on cratons and deserts, which are stable terrain, so the control does not fully remove that bias; most are smaller than the 50 km window; points may be displaced up to 10 km; the only contrast possible is with topography.

## Result with the USGS layer (14 Nov 2026)
The protocol above was run without changing it. Code: `src/astroatlas/aspect_usgs.py`; data: `data/features/earth_usgs.parquet` (not versioned).

**Sample.** 185 unique craters + Grand Falls (dunes) and 200 control points (one crater without DEM). With a score there were **180 positives and 186 controls**: 6 craters and 14 controls were lost because of the defect described below.

| Body | u craters and dunes | u control | Craters with u > 0.5 | Controls with u > 0.5 | Rank AUC (95 % CI) | p (Mann-Whitney, 1-sided) | Signal? |
|---|---|---|---|---|---|---|---|
| Moon | 0.530 | 0.530 | 58 % | 63 % | 0.491 (0.432 to 0.552) | 0.62 | **No** |
| Mars | 0.597 | 0.548 | 78 % | 68 % | 0.557 (0.499 to 0.618) | 0.029 | **No** (the lower bound, 0.499, does not exceed 0.5) |

Craters only, without the dunes: Moon 0.488 (0.430 to 0.548), Mars 0.555 (0.497 to 0.614). The two remaining records, informative (n = 1): Grand Falls scores u = 0.71 against the Moon and 0.79 against Mars; the volcano (mislabelled "Ritland", in Iceland) 0.72 and 0.77.

**Verdict according to the criterion fixed beforehand: topography is not validated as an aspect with this layer.**
- On the **Moon** there is no difference between craters and random points (AUC 0.49).
- On **Mars** there is a small difference (AUC 0.56) that touches the threshold: the p-value (0.029) is nominally low, but two comparisons were made (Moon and Mars), so the corrected threshold would be 0.025, and the interval does not exclude 0.5 by a thousandth. **It must not be presented as evidence in favour.**
- **The flat-terrain bias is real in the data itself:** craters are flatter than the control (mean slope 1.33° versus 2.53°; median local relief 152 m versus 250 m). Since the Mars sites are also flat (median slope 0.7°), a crater can score somewhat better **just by being on a stable craton**. The slight advantage on Mars is compatible with that and not with a crater-shape similarity.

**Defect found: the flattest cells do not receive a topography score.** The variables `topo__aspect_concentration` and `topo__aspect_equatorward` are NaN when the mean slope is below 0.1° (with no slopes there is no aspect), and the PCA does not accept NaN. Measured consequences:
- **91 of the 955 Earth grid cells do not score** in topography: 54 in Antarctica (53 with mean annual snow above 0.5), and the rest are **lakes** (Michigan, Caspian, which Copernicus flattens to zero relief at any altitude, so the ocean filter does not catch them) and real plains (the Sudd).
- **Exactly the sites most topographically similar to Mars drop out of the rankings** (slopes of 0.3° to 0.7°).
- In this test 3 % of the craters and 7 % of the controls (the flattest of each group) were lost.
- **It had not been corrected.** Giving those variables the value 0 on flat terrain is the neutral choice, but lakes also have to be filtered (relief below 1 m at any altitude) or they would appear as candidates. It is a model change that affects all earlier results and requires a decision.

**Limits:** the craters are the list of confirmed Earth ones (Earth Impact Database), not a selection by similarity to the Moon or Mars; most are smaller than the 50 km window; points may be displaced up to 10 km; sensitivity to the defect above was not tested because lakes would have to be filtered first and that is part of the fix.

## Second run, after fixing flat terrain (14 Nov 2026)
**What changed in the model** (decided after seeing the first run): the aspect variables are 0, not NaN, on flat terrain (mean slope < 0.1°); and the water filter discards relief < 1 m at any altitude (lakes included). Result: the 91 flattest Earth cells now score, 4 water cells drop out (951 cells) and no crater or control is lost any more (**185 positives and 200 controls, previously 180 and 186**). The controls were reselected with the same seed and rules. The Moon and Mars do not change (minimum slopes 0.59° and 0.28°).

**Topography with the USGS layer (same test and same criterion fixed beforehand):**

| Body | Run | u craters and dunes | u control | Rank AUC (95 % CI) | p (1-sided) | Signal? |
|---|---|---|---|---|---|---|
| Moon | first (before fixing) | 0.530 | 0.530 | 0.491 (0.432 to 0.552) | 0.62 | No |
| Moon | **second (fixed)** | 0.548 | 0.538 | **0.522 (0.465 to 0.578)** | 0.23 | **No** |
| Mars | first (before fixing) | 0.597 | 0.548 | 0.557 (0.499 to 0.618) | 0.029 | No (bound 0.499) |
| Mars | **second (fixed)** | 0.598 | 0.547 | **0.567 (0.507 to 0.620)** | **0.012** | **Yes** (bound 0.507) |

**How to read it, with caution:**
- **On Mars the criterion fixed beforehand is now met** (lower bound > 0.5, and p = 0.012 is below the 0.025 threshold that corrects for the two comparisons). The signal is small: a crater scores higher than a random point 57 % of the time (chance is 50 %), and the lower bound exceeds 0.5 by only 0.007. On the **Moon there is still no signal**.
- **The Mars verdict changed because of a correction made after seeing a borderline result** (0.499). The correction is one of principle (it was a design defect that dropped exactly the flattest sites, and it was not chosen for its effect: before measuring it was not known which direction it went), and it restores the full sample. But for that reason the **first run is the one that meets the protocol in the strict sense, and the second must be presented as a repetition after fixing a defect, not as an independent confirmation.**
- **The flat-terrain bias is still not eliminated:** craters are flatter than the control, and so are the Mars sites. The 0.567 advantage may be due to that terrain similarity and not to crater shape. This test cannot separate them.
- The confidence interval already incorporates the variation of the control group (both groups are resampled), so it is not necessary to try other seeds, but it is a single set of 200 controls.

**Effect of the fix on the other results** (small changes, within noise; the conclusions do not change):
- Pipeline (29 targets): cell AUC 0.479 → 0.505; exact-site AUC 0.556 → 0.539; site recall 0.147 → 0.147.
- Ablation: Mars "all" 0.50 → 0.49 and Moon 0.60 → 0.58; Mars "only ice" 0.62 (+0.11), Mars "only geology" 0.14, Moon "only thermal" 0.64: the same as before.
- Per-aspect validation (main level): Mars topography +0.14 → +0.15 and Moon +0.08 → +0.12 (still not conclusive); geology (+0.97 Mars, +0.53 Moon), Mars ice (−0.75) and Moon thermal (−0.48): identical.

## Repetition with 21 lunar sites (14 Nov 2026)
Everything was repeated after updating the Moon with LROC (21 sites, previously 15). **Mars does not change.** The aspect labels and the USGS protocol were not touched.

**Per-aspect validation (source + note level), Moon:**

| Dimension | With the aspect | Before (15 sites) | **Now (21 sites)** | permutation p |
|---|---|---|---|---|
| Geology | Mauna Kea, Askja, Craters of the Moon (versus Haughton) | +0.53 (0.47 to 0.57) | **+0.64 (0.56 to 0.69)** | 0.25 (the minimum possible with 1 negative) |
| Topography | Haughton | +0.12 | +0.14 (−0.08 to 0.39) | 0.50 |
| Thermal | Haughton | −0.48 | −0.48 (−0.58 to −0.29) | 1.00 |
| Ice | — | not evaluable | not evaluable | |

The direction of each result is kept. Geology remains in the right direction and is now somewhat larger, but **it still cannot be conclusive** (the minimum attainable p is 0.25). Thermal remains against for the reason already explained (a cold polar analog against almost entirely equatorial targets).

**Topography with the USGS layer (same test and criterion):**

| Body | Before (15 sites) | **Now (21 sites)** | Signal? |
|---|---|---|---|
| Moon | 0.522 (0.465 to 0.578), p 0.23 | **0.531 (0.473 to 0.586), p 0.144** | **No** |
| Mars | 0.567 (0.507 to 0.620), p 0.012 | 0.567 (0.507 to 0.620), p 0.012 | Yes (unchanged; it is the repetition after fixing a defect, not an independent confirmation) |

**Pipeline (35 targets: 21 lunar and 14 Martian):** exact-site AUC 0.539 → **0.579** (range 0.27 to 0.89); site recall 0.147 → **0.171**; cell AUC 0.505 → 0.498. Still close to chance, with a small improvement that comes from the new targets and not from a change of method.

## What would be needed to conclude
1. **More analogs per aspect, with the reason cited** (at least 5 per aspect): basaltic fields, cold and dry deserts, impact craters, polar zones. Each with its open NASA or ESA source and its label fixed before measuring.
2. **Change Earth's ice variable** to one that measures dryness or soil water (precipitation or soil moisture, like GLDAS, which requires accepting its licence) instead of snow cover.
3. **Define beforehand which targets are relevant** for each aspect (thermal: polar sites; geology: sites with basalt).

## Flat-terrain control (15 Nov 2026)
Preregistered in [../preregistrations/plains.md](../preregistrations/plains.md) before measuring. Comparing craters and controls within strata of mean slope, the Mars AUC drops from 0.567 to **0.494** (CI 0.436-0.552) and the Moon's from 0.531 to 0.476. **The Mars advantage in the USGS test is explained by terrain flatness, not by crater shape**; topography is not validated as an aspect with this layer.
