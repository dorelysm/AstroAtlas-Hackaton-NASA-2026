# Caves and lava tubes (15 Nov 2026)

**Summary:** there are open data on lunar pits and terrestrial lava tubes, but **they cannot be turned into a similarity dimension**: the terrestrial catalogue has no coordinates and the Mars one could not be downloaded automatically. They were integrated as **context**.

## What data exist
| Body | Source | Content | Licence | Status |
|---|---|---|---|---|
| Moon | Losarcos and Dombard (Zenodo 10.5281/zenodo.20516852, Jun 2026), `Pit-locations` layer (from LROC QuickMap; Wagner and Robinson) | 278 pits: 257 in impact-melt lakes, 16 in maria, 5 in highlands | CC BY 4.0 | **Integrated** (`pits_within_50km`, `nearest_pit_km`, `nearest_pit_name` in `moon.parquet`) |
| Earth | Pyroduct Digital Catalog v1 (Romio and Lobosco 2024, Zenodo 10.5281/zenodo.14535886) | 93 documented lava tubes (index in [docs/catalog/documented_lava_tubes.csv](../catalog/documented_lava_tubes.csv)); the full catalogue is cross-sections in a 498 MB DXF that was not downloaded | CC BY 4.0 | **Integrated as an index by region** (no coordinates) |
| Mars | Mars Global Cave Candidate Catalog (USGS, Cushing; PDS release 2019) | 1,062 candidates with coordinates, type (sky 354, srp 218, APC 132, crk 87, …) and priority | public domain (USGS) | **Integrated** (`caves_within_50km`, `nearest_cave_km`, `nearest_cave_name` in `mars.parquet`). The USGS server blocks automatic download and no attempt was made to get around it: a team member downloaded it to `data/raw/mgc3/`. The CSV header is scrambled; the XML order is used |

## Documented lava tubes by region (Pyroduct)
Hawaii (USA) 22 · Azores (Portugal) 20 · Etna (Italy) 17 · **Harrat Al-Shaam (Jordan) 8** · Oregon (USA) 6 · La Palma 5 · Queensland 3 · Victoria 3 · **Lanzarote 2** · New Mexico 2 · Vesuvius 1 · Harrat Buqum (Saudi Arabia) 1 · Harrat Ithnayn (Saudi Arabia) 1.
That a region does not appear does **not** mean it has no tubes: the catalogue itself warns that it does not cover all countries (for example Haruj, in Libya, and Craters of the Moon are not there).

## Results
1. **Mars:** none of the 14 targets has a cave candidate within 50 km; the nearest is 895 km away (Mawrth Vallis). The candidates are concentrated in Tharsis and surroundings and **our targets are rover landing sites, not cave regions**. The cave dimension does not discriminate on Mars either.
2. **Moon:** only 1 of the 21 lunar targets has a pit within 50 km, the *Mare Tranquillitatis pit* itself. The other 20 landing sites and targets are not near any. An expected result, but it means the cave dimension barely discriminates between our targets.
3. **The model does not see the tubes.** The best terrestrial analogs of the *Mare Tranquillitatis pit* (score 0.82-0.84) are flat Antarctic ice cells, which only match by topography (the other dimensions have no data). None is a volcanic region with tubes.
4. **Candidate A (Harrat ash-Shamah):** the catalogue documents **8 lava tubes in Harrat Al-Shaam (Jordan)**. It is the same volcanic region as the candidate, although it cannot be assured that they are inside the 50 km cell (there are no coordinates). It is a point in favour of the candidate as a cave analog, not a validation. **Candidate B (Haruj):** the catalogue does not cover it.
5. **Known analogs:** Mauna Kea (Hawaii, 22 tubes) and Lanzarote (2) are in regions with documented tubes; Craters of the Moon, which has known caves, is not in this catalogue.

## Why it is not a dimension
- Without coordinates of the terrestrial tubes cells cannot be compared one by one.
- No Mars target and only 1 Moon target has a cave or pit nearby: the dimension does not distinguish between the current targets. For it to matter, cave targets (Tharsis, Marius Hills) would have to be added.
- That a pit has not been detected in images does not mean it does not exist; there is a detection bias.
- To do it properly, a table of terrestrial tubes with coordinates would have to be built from the literature (Hawaii, Azores, Etna, Harrat, Canary Islands, Oregon, Queensland) and validated with analogs labelled for caves; that is work for another stage.

## What it is already useful for
For the profiles: it indicates whether a candidate's region has documented caves, and for the presentation: it shows what exists and why it is not used as a score.
