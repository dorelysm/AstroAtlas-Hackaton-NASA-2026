# Preregistration: extended set of validation analogs (15 Nov 2026, written BEFORE searching)

**Why:** with 10 analogs (4 to 8 per body) no measure can be conclusive, and any improvement tested on them would be fitting the test. A larger set is built, **frozen**, and only then measured.
**Frozen model:** that of commit `0b8a0a2` (per-dimension score `exp(−RMS z)`, whitened topography PCA, equal weights). **Nothing in the model is changed after seeing these results**; any later improvement is tested against this already fixed set and reported separately.

## Inclusion criteria (all mandatory)
1. An open source **names the site as a terrestrial analog of the Moon and/or Mars**: an agency page (NASA, ESA, USGS, JAXA...), a peer-reviewed article or conference abstract (LPSC, AGU...), or a page of an institute or university dedicated to analogs.
2. It is a **locatable site** (a lava field, crater, valley, salt flat...), not a whole desert. A coordinate with reasonable uncertainty (≈ ≤ 10 km) is needed, from the source itself or from Wikipedia/a gazetteer, with its origin noted.
3. **No model result is consulted** to decide which sites are included.
4. **Independence:** if two candidate sites are less than 100 km apart, only the one with the stronger source is included (agency > article > university > other).
5. The 10 current analogs **are kept** and reported separately (original / new / all).

## Searches (fixed; no queries are added to look for more sites after seeing the results)
(1) `basaltic lava field terrestrial analog Mars field site NASA` · (2) `Mars analog cold desert permafrost field site Axel Heiberg Devon Island Dry Valleys` · (3) `hyperarid desert Mars analog field site Atacama Yungay Salar` · (4) `impact crater terrestrial analog Moon Mars field site Meteor Crater Ries` · (5) `lunar analog terrestrial field site volcanic ash regolith simulant` · (6) `Mars analog acidic evaporite salt flat field site Danakil Uyuni Rio Tinto` · (7) `Mars analog dunes aeolian field site Namib Qaidam` · (8) `lava tube cave planetary analog field site Lava Beds Undara`.
Only follow-up queries are made to **obtain coordinates or the cited reason** of sites already found.

## Aspect labels
An aspect label (topo, thermal, ice, geo, caves, aeolian) is only assigned if the source text names that aspect. Levels: *source* (the text says it) or *note* (our note says it). If no aspect is named, the site enters the global validation but no per-aspect one.

## Evaluation plan (fixed)
- Same metrics as before: u = P(analog > typical cell) with 50 km windows (`validate.evaluate_sites`), **bootstrap over the analogs**, one measure per body and per set (original / new / all).
- **Success criterion:** the lower bound of the confidence interval of the mean u ("all dimensions") is **> 0.5** in every body with at least 8 analogs. Per-aspect intervals are also reported when there are ≥ 3 analogs per group.
- Dimensions the site lacks (e.g. Mars thermal) are ignored, as in the model.
- **Limit:** the features of the new sites will be computed only with topography (Copernicus), thermal and snow (MODIS) and geology (GLiM), so as not to repeat the whole context download; the population and vegetation flags are not applied to the validation.

## Frozen list (annex, written after the 8 searches and BEFORE computing any feature or any score)
- `docs/catalog/extended_analogs.csv` (13 new sites), sha256 `0f234908cd16ce94`; `docs/catalog/extended_analog_aspects.csv` (10 labels), sha256 `3cc33c3ddf4c8a6f`. With the original 10 they add up to **23 analogs**. No pair of sites is less than 100 km apart.
- **The ~30 planned were not reached:** the 8 fixed queries produced 13 sites that meet the criteria, and the protocol does not allow adding queries to look for more.
- **Excluded and why:** Mauna Ulu/Kilauea, Mauna Loa and Snake River Plain (< 100 km from Mauna Kea and Craters of the Moon, which are kept); Yungay and Salar de Pajonales (< 100 km from the Atacama point); Steinheim (< 100 km from Ries); Beacon Valley (in the same cell as the Dry Valleys); Undara (the search does not present it as an analog); Qaidam (the source proposes the entire basin, not a locatable site, and excluding it avoids reinforcing the mobility result that already came out); Eifel (a region, not a site); Merriam Crater/Cinder Lake (< 100 km from Meteor Crater). Wudalianchi appeared in another search (the novelty check), not in the 8 of this protocol, and is left for a second version (it was used in [validation-set-2.md](validation-set-2.md)).
- **Coordinates:** all those of the new sites come from general knowledge or Wikipedia and are marked **TO VERIFY** in the CSV. An error of tens of kilometres would change the result little (50 km window), but it is not checked.
- **Known selection bias:** impact craters abound (5 of 13) because one article scores 11 structures; this gives weight to the topographic aspect.
