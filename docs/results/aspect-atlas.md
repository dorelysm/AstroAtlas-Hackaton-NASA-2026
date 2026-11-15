# Aspect atlas (15 Nov 2026)

The challenge says a place can be an excellent geological analog and a poor thermal one. A global ranking mixes everything, so here **each aspect is evaluated separately** and carries a **confidence label that comes from results already measured**, not from an opinion.
Code: `src/astroatlas/atlas.py` (`python -m astroatlas.atlas`). A cell's score = mean, over the body's targets with data in that aspect, of its similarity **in that dimension only**. Only viable, non-vegetated cells; regions separated by ≥ 500 km; nothing below 0.10 similarity is listed.

## Confidence per aspect and why
| Body | Aspect | Confidence | Measured result that justifies it |
|---|---|---|---|
| Moon | Topography | low | USGS layer with a flat-terrain control: AUC 0.48. By labelled analogs, +0.14 with an interval that includes zero ([../preregistrations/plains.md](../preregistrations/plains.md)) |
| Mars | Topography | low | The initial advantage (0.567) disappears when flatness is controlled (0.494). By analogs, +0.15, not conclusive |
| Moon | Geology | **medium** | Right direction (+0.64) with 1 to 3 analogs per group; minimum attainable p 0.25. The lunar proxy (FeO) and terrestrial basaltic rock do not measure the same thing |
| Mars | Geology | **medium** | Right direction (+0.97) with a single analog (Craters of the Moon); Mars geology saturates |
| Moon | Thermal | very low | Against (−0.48), a single polar reference; terrestrial thermal data are monthly means. **No cell exceeds 0.10 similarity: nothing is recommended** |
| Mars | Thermal | no data | Mars has no thermal data in the model |
| Moon | Ice | very low | Only 2 polar targets have data; no analog carries the label: not evaluable |
| Mars | Ice | very low | Fails at the Dry Valleys (−0.75): snow does not measure dryness; soil moisture does not improve ([../preregistrations/ice.md](../preregistrations/ice.md)) |

No aspect reaches "high": with 4 to 8 analogs per body none can be conclusively validated. The "medium" label for geology is the highest the data allow.

## Best regions per aspect (from `data/results/atlas_regions.csv`)
- **Geology, Mars (medium):** 27.5° N 17.5° E (Haruj), 32.5° N 37.5° E (Harrat ash-Shamah) and two Antarctic cells (−77.5°, 167.5° E and −77.5°, 127.5° W), all at 0.85. **Beware of the Antarctic ones:** GLiM gives the subglacial rock, not the visible surface; they are a source artefact. The first two are the candidates of [candidate-profiles.md](candidate-profiles.md).
- **Geology, Moon (medium):** the same cells, with a low score (0.23): terrestrial basalt does not resemble the lunar FeO profile much.
- **Topography, Mars (low):** 32.5° N 37.5° E, 37.5° N 92.5° E (Qaidam basin), 17.5° N 52.5° E, 22.5° N 22.5° E and 22.5° N 17.5° E, all ≈ 0.53: flat desert terrain.
- **Topography, Moon (low):** scores ≈ 0.43; among them is flat polar ice.
- **Ice, Mars (very low):** 42.5° N 102.5° E (Gobi), 37.5° N 117.5° W (near Death Valley), Atacama and Central Asian deserts, with 0.93 to 0.97. They are deserts without snow: what it measures is "no snow", not subsurface ice.
- **Ice, Moon (very low):** Arctic cells, one of them 327 km from Haughton, the only known polar analog.

## How to use it
As a guide to **which aspect resembles where**, not as a list of recommended analogs. The app shows it in the "Aspect atlas" section, with the confidence next to each table.
