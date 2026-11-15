# Candidate profiles (15 Nov 2026)

**What they are:** Earth cells that the model proposes as new analogs (far from any known analog of that body), with what is similar, what is not, and what they might be useful for.
**What they are NOT:** validated discoveries. The model's validation is close to chance ([../validation/validation.md](../validation/validation.md)), so they are **hypotheses to review with an expert**, not results.

## How they were chosen (and an honesty note)
Rule (code in `src/astroatlas/profiles.py`): start from `candidates_shortlist.csv` (viable, non-vegetated cells more than 500 km from any known analog of that body); count in how many of the body's targets each cell appears in the top 10; keep the first 2 separated by at least 500 km.
**Note:** the rule was written **after** seeing a preliminary list of repeated cells, not before. It is a mechanical, simple rule (no cell was picked by hand), but it is not a strict preregistration.
The two flags used for filtering (`viable`, `vegetated`) do not enter the score and are not applied to the validation. The vegetation filter was added **because** the first Mars candidates were rainforests in New Guinea and Indonesia (the model has no biology dimension and the "ice" variable is ~0, the same as on Mars); that was discovered by looking at the results, and it is documented here.

Each cell is a point of a 5° grid and the variables are computed in a **50 × 50 km window** around its centre, not over the whole region. Region names are an interpretation from the coordinates (to be checked).

## Mars

### A. Harrat ash-Shamah basaltic plateau (southern Syria / northern Jordan) · `earth_24_43` · 32.5° N, 37.5° E
Appears in the top 10 of **13 of the 14 Mars targets** (mean score 0.76).

| Dimension | Score | Value on Earth | Reading |
|---|---|---|---|
| Geology | 0.85 | 100 % of the window is basalt (GLiM) | **Real match**: Mars is a basaltic planet |
| Topography | 0.53 | mean slope 0.74°, local relief 242 m | Moderate match; flat but with relief |
| Ice/water | 0.90 | mean snow 0 | **Artefact**: it matches only through the absence of snow; it measures neither dryness nor subsurface ice |
| Thermal | no data | monthly max. T 325 K, diurnal range 20 K | Mars has no thermal data in the model |

- **Novelty ([../preregistrations/novelty.md](../preregistrations/novelty.md)):** the "jubot" depressions in the north-west of the field have been presented as a **planetary-pit analog** (2018 and 2019 abstracts); it is not an unstudied region, although no study as a geological analog of Mars turned up.
- **Caves (context):** the Pyroduct catalogue documents **8 lava tubes in Harrat Al-Shaam (Jordan)**, the same volcanic region; there are no coordinates to confirm that they are inside the cell ([../context/caves-and-lava-tubes.md](../context/caves-and-lava-tubes.md)).
- **Dust and wind (context only, MERRA-2 2019):** surface dust 88 µg/m³ (high), mean 10 m wind 2.5 m/s. On Mars dust and storms are a key operational factor, but the model does not compare them.
- **Vegetation:** max. NDVI 0.12 (almost bare soil). **Population:** the nearest settlement of ≥ 1,000 inhabitants (As-Suwayda') is 90 km away. Nearest known analog: Río Tinto, 4,012 km.
- **What it could contribute:** testing rovers and navigation over a lava field with loose rocks and desert soil; practising geological sampling on basaltic terrain.
- **Where the analogy fails:** gravity (0.38 g on Mars), atmosphere (0.6 % of Earth's), radiation, and above all **we do not know whether it is dry like Mars**: the model does not measure it. It has an arid climate, but it is not an ice analog.
- **Practical risk:** the area is in a region with insecurity and access restrictions; that would have to be assessed before proposing it as a field site. The model does not see it.

### B. Haruj volcanic field (Libya) · `earth_23_39` · 27.5° N, 17.5° E
Appears in **9 of 14** Mars targets (mean score 0.69).

| Dimension | Score | Value on Earth | Reading |
|---|---|---|---|
| Geology | 0.86 | 100 % basalt | **Real match** |
| Topography | 0.32 | mean slope 0.59°, relief 368 m | **Low match**: it is the weakest dimension |
| Ice/water | 0.90 | mean snow 0 | **Artefact** (same as above) |
| Thermal | no data | max. T 328 K, diurnal range 24 K | Not compared |

- **Novelty ([../preregistrations/novelty.md](../preregistrations/novelty.md)):** the preregistered search found **no study of Haruj as an analog** of Mars or the Moon (there is one of another Libyan caldera, Wau-an-Namus): it is the least studied candidate. "No evidence" does not prove there is no literature.
- **Caves (context):** Haruj is not covered by the lava-tube catalogue (that does not imply it has none).
- **Dust and wind (context only, MERRA-2 2019):** surface dust 187 µg/m³ (very high; it is the Sahara), mean wind 2.4 m/s.
- **Vegetation:** max. NDVI 0.09. **Population:** the nearest settlement of ≥ 1,000 inhabitants (Waddan) is 229 km away, the more isolated of the two. Nearest known analog: Río Tinto, 2,512 km.
- **What it could contribute:** a hyper-arid desert with an extensive, isolated volcanic field; a place for autonomy trials where communications and logistic support are part of the test.
- **Where it fails:** same as A, and its topography only matches moderately.
- **Practical risk:** access and security in Libya; this would also have to be verified.

## Moon

### C and D. Frozen surface of Antarctica (Ross Ice Shelf and surroundings) · `earth_2_70` (−77.5°, 172.5° E) and `earth_1_0` (−82.5°, 177.5° W)
They appear in **7 of 21** lunar targets (mean score 0.51 and 0.51).

- **Only topography data exist** (score 0.51 in both): they are extremely flat ice surfaces (mean slope 0.06° and 0.04°). Thermal, ice and geology have no valid data in these cells (the exact cause was not checked; it is probably polar night and ice), so the score **only says they are as flat as a lunar mare**.
- **Honest assessment:** **they are not good lunar analogs.** A flat ice shelf does not resemble a lunar basalt mare in materials, temperature (the Moon reaches 390 K by day) or processes. They appear because the model, without other dimensions, rewards flatness. They are shown for transparency and as an example of the method's limit.
- **Dust and wind (context):** almost no dust (0.3 µg/m³) and a mean wind of 5 to 7 m/s, among the highest in the sample: the opposite of the Mars candidates.
- **It does have a useful reading:** polar logistics (cold-operation trials, rovers on a flat surface, communications at high latitudes) resemble a polar lunar base more than an equatorial landing site; but that is our idea, not something the model shows.
- One of the cells (C) is about 250 km from the Dry Valleys, a known analog of Mars (not of the Moon), which is why the 500 km rule does not exclude it.

## What these profiles say about the method
1. The **two Mars candidates are basaltic volcanic fields in desert**: this matches what would be expected from a good geological analog and is the most defensible result. But they resemble **sites already studied** (there are known basaltic analogs such as Craters of the Moon or Lanzarote) and by topography they only match moderately.
2. The lunar candidates are an **artefact of having a single dimension with data**. The missing dimension weighs far more than any model adjustment.
3. Without the vegetation flag, the first Mars candidates were rainforests. This confirms that **context dimensions are missing** (biology, caves, dust and wind, illumination) before the ranking can be trusted.
4. Everything said about use for exploration is **plausible, not demonstrated by the data**.

## Supporting data
`data/results/candidate_profiles.{csv,json}` (not versioned; regenerated with `python -m astroatlas.profiles`; a copy of the CSV is in `demo_data/results/`).

## Zoom to volcanic-field scale (15 Nov 2026)
The challenge asks to look at the scale of a volcanic field and not of a desert. For the two Mars candidates the **topography** was recomputed on a **0.25° (~28 km)** grid (the global one is 5°), with the same variables, 50 km window and 500 m baseline, and scored against the 14 Mars targets. Code: `src/astroatlas/zoom.py` (`python -m astroatlas.zoom --name harrat --lat 29 36 --lon 34 42`).

| Region | Box | Cells | Mean topographic score (range) | Best fine cell |
|---|---|---|---|---|
| Harrat ash-Shamah | 29-36° N, 34-42° E | 895 | 0.43 (0.15 to 0.55) | 0.55 at 29.9° N, 36.6° E |
| Haruj | 25-30° N, 14-21° E | 560 | 0.47 (0.15 to 0.55) | 0.55 at 28.6° N, 16.4° E |

**What it says:**
- **Within each region the topographic similarity varies a lot** (0.15 to 0.55): treating the region as a single analog loses information, and the zoom helps choose *where* within it. That is the point the challenge makes about scale.
- **At Harrat, the original 5° cell (topography 0.53) was already among the best** of its region: the zoom finds nothing clearly better.
- **At Haruj, the original cell (0.32) was weak** and the zoom finds cells of 0.55 about 1.5° north of the cell centre, that is, **the 5° candidate was badly centred**. This reinforces that the coarse grid should only be used to choose regions.
- No sub-point exceeds 0.55 on average: not even the best fine site is a good global topographic match with the Mars targets.

**Limits:** the zoom is **topography only** (GLiM geology is 0.5° and adds nothing at this scale; thermal and ice would need re-downloading the MODIS products for the new cells). That the best fine cells are the most similar **by topography** does not guarantee that they lie over the lava field: it was not checked against a detailed geological map. The coordinates of the best cell have not been verified on the ground.
