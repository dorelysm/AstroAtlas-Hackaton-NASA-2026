# Verification of coordinates and analogies (15 Nov 2026)

Goal: replace Wikipedia coordinates with primary sources before citing them. **Result: partial verification.**
Sources were opened with a page-download tool; several servers (USGS Gazetteer, NASA, Earth Impact Database, SEDAC, Copernicus) refused the connection or returned 404 in this session, so **most of the list is still unverified**.

## What was checked
| Site | Value in the repo | What was found | Conclusion |
|---|---|---|---|
| Oxia Planum | 18.2° N, 335.7° E (ESA 2018) | Wikipedia cites the 2019 IAU approval: **18.275° N, 335.368° E** (and Quantin-Nataf et al. 2021, *Astrobiology*) | **A discrepancy of ~19 km in longitude**, inside the 50 km window. The CSV was not changed so as not to alter results already measured; if it is corrected, `mars.parquet` must be recomputed and the evaluations repeated |
| Jezero | 18.38° N, 77.58° E | Matches Wikipedia (18°23′N 77°35′E); the primary source (USGS Gazetteer) could not be opened | A plausible crater-centre coordinate; still "not verified in a primary source" |
| Río Tinto | 37.7° N, 6.55° W (value from memory) | Wikipedia gives the river mouth at 37.21° N, 6.94° W; it does not give the mining area | The coordinate is that of the mining area, not the mouth. Still unsourced. The analogy with Mars is in a 2005 NASA JPL note cited by Wikipedia (water of the Meridiani deposit) |

## What remains unverified (to be opened by hand)
- **Terrestrial analogs** (`docs/catalog/known_analogs.csv`): coordinates of Atacama, Haughton, Mauna Kea, Askja, Lanzarote, Svalbard, Craters of the Moon and Death Valley come from Wikipedia. Suggested primary sources: Earth Impact Database (Haughton), Global Volcanism Program (Askja), USGS GNIS (Death Valley, Craters of the Moon). The Dry Valleys and Atacama are regions: the coordinate is a representative point.
- **Analogies without a source:** Mauna Kea, Askja and Svalbard (the reason for the analogy is not checked).
- **Target sites:** Shackleton (approximate), Mare Tranquillitatis pit, Jezero, Oxia Planum and Arcadia Planitia (the SWIM table could not be read at the time; later completed from Dundas et al. 2021).
- **Without an LROC table:** Chang'e 4 and Chang'e 6 (after 2016).

## What to do before citing
Open each `source_url` / `coord_source` of the CSVs and, for the rows above, look for the primary source. A team member with access to those sites can do it in about 30 minutes; if any target coordinate is corrected, rerun `python -m astroatlas.data.mars` (or `moon`) and the evaluations.
