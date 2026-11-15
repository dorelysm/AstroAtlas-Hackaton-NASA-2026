# Analogs by use case (15 Nov 2026)

Instead of a single ranking, six use profiles. Each one fixes which targets it is compared with, which dimensions weigh, and what can be claimed.
Code: `src/astroatlas/usecases.py` (`python -m astroatlas.usecases`). Only viable, non-vegetated cells are considered. **They are hypotheses**: the model's validation is close to chance.

## Results (3 regions per case, separated by ≥ 500 km)
| Use case | Best cells (lat, lon) | Score | Honest reading |
|---|---|---|---|
| **Mobility and landing, Mars** (12 sites, topography) | 37.5°, 92.5° · −72.5°, −72.5° · 22.5°, −2.5° | 0.51 · 0.51 · 0.50 | **Moderate** match. The first falls in the Qaidam basin (China), which as far as I know has been proposed as a Mars analog (**not verified here**); the second is Antarctic ice and the third the western Sahara |
| **Mobility and landing, Moon** (18 sites, topography) | 27.5°, 37.5° · 77.5°, −27.5° · 42.5°, 107.5° | 0.48 · 0.47 · 0.47 | **Low** match. The second is Greenland. Topography only |
| **Cold at the lunar poles** (2 targets) | 37.5°, 87.5° · 37.5°, 72.5° · 72.5°, −87.5° | 0.24 · 0.22 · 0.21 | **Very low**: Earth does not reproduce a shadowed zone (< 100 K). The third is 327 km from Haughton, the only known polar analog, which is consistent |
| **Ice in northern Mars** (2 targets) | 17.5°, 27.5° · 22.5°, 52.5° · 32.5°, 37.5° | 0.74 · 0.74 · 0.74 | **Artefact**: they are deserts without snow (Sahara, Arabia). The high score is "no snow", not subsurface ice |
| **Basaltic terrain, Mars** (9 sites, geology + topography) | 32.5°, 37.5° · 27.5°, 17.5° · −77.5°, −127.5° | 0.78 · 0.69 · 0.66 | **The only case with a clear meaning**: the first two are the candidates of [candidate-profiles.md](candidate-profiles.md) (Harrat ash-Shamah and Haruj); the third is the Marie Byrd volcanic zone (Antarctica) |
| **Volcanic and lava tubes, Moon** (8 sites) | −87.5°, 52.5° · −82.5°, −132.5° · 77.5°, −27.5° | 0.54 · 0.53 · 0.52 | All on polar ice; they come out by topography. **It does not see the tubes** (only 1 of 21 targets has a pit nearby, see [../context/caves-and-lava-tubes.md](../context/caves-and-lava-tubes.md)) |

A seventh case, added later, covers **cold ground ice on Mars with a real permafrost map** (Obu et al. 2018); see [../preregistrations/permafrost-map.md](../preregistrations/permafrost-map.md).

**Global reading:** only the basaltic Mars case gives a defensible recommendation. Mobility gives moderate matches, and the cold and ice cases show the limits of Earth as an analog. That the method says so explicitly is part of the result.

## Why engineering thresholds are not used
The model variables come from a common **500 m** grid and 50 km windows. The published thresholds are defined at scales of metres and 2 to 5 km, so they **cannot be applied as absolute thresholds** to this data. That is why the mobility cases compare with the terrain of sites where a landing or a drive has already happened (a relative measure). The thresholds, as context only (**to be verified in the primary source**):

| Quantity | Value | Source (search result, not verified in the original document) |
|---|---|---|
| MSL (Curiosity) landing slope | ≤ 3° at 2 to 5 km scale within the ellipse | [MSL Engineering User Guide](https://marsoweb.nas.nasa.gov/landingsites/msl/memoranda/MSL_Eng_User_Guide_v2.pdf) |
| InSight slope and rocks | < 15° at 84 m and 2 m scales; rock abundance < 10 % | search results on the InSight site selection |
| Starship HLS landing on the Moon | ≤ 8° from vertical (assessment references mention ≤ 10°) | [Artemis III site assessment](https://arxiv.org/pdf/2406.19863) and NASA statements |
| Rover tilt avoided when planning | ≈ 30° (Perseverance); mechanical tolerance 45° (Curiosity); records of 31° and 32° | [NASA/JPL, Perseverance](https://www.jpl.nasa.gov/news/nasas-perseverance-rover-looks-back-while-climbing-slippery-slope/) |

## What is missing to make them more useful
- Engineering thresholds at the right scale: this would require metre-scale digital terrain models (HiRISE on Mars, LROC NAC on the Moon) and their terrestrial equivalents, not the 90 m ones.
- Use cases with new dimensions (dust and wind, caves) once there is a Martian counterpart and analogs to validate them.
