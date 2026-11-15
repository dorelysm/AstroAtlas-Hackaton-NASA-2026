# Data provenance

Record of where each piece of data in the repository comes from and how reliable it is. Update it every time data is added or changed.

**Date of the searches:** 14 November 2026.
**How they were obtained:** three web searches made by AI agents (Haiku model) that opened pages with a page-download tool. An AI agent can make transcription mistakes, so **before citing a value in the final submission, open the URL in the `source_url` column and check it**.

## Confidence levels

| Level | Meaning |
|---|---|
| **Verified** | The agent opened the page and copied the value from there. A second human check is still missing. |
| **Verified (secondary source)** | The page opened is not the agency's, but it cites a paper. |
| **NOT VERIFIED** | Value seen only in a search summary or in a source that could not be opened. Do not use without confirming. |
| **Unchecked** | Written by us from memory, without a source. |
| **Wikipedia** | Coordinate taken from Wikipedia, which cites no primary source. Indicative, not official. |

## Files and their origin

### `docs/catalog/known_landings.csv` (41 rows)
Coordinates of landing sites on the Moon and Mars. Origin by block:

| Block | Source | Level |
|---|---|---|
| Apollo 11, 12, 14, 15, 16, 17 | NASA NSSDCA: https://nssdc.gsfc.nasa.gov/planetary/lunar/lunar_sites.html; **confirmed by LROC** (table below): all six agree within 1e-4° (~3 m) | Verified with two sources |
| **LROC tables** (Coordinates of Lunar Anthropogenic Targets, LROC team at Arizona State University for NASA's LRO mission, 28 Jul 2016; Wagner et al., *Icarus* 283, 92-103, doi:10.1016/j.icarus.2016.05.011): https://lroc.im-ldi.com/data/support/downloads/2016_LROC_Coordinates_of_Robotic_Spacecraft.pdf and https://lroc.im-ldi.com/data/support/downloads/2016_LROC_Coordinates_of_Human_Features.pdf | mean of several NAC camera images, Mean Earth / polar axis system, **uncertainty of 0.3 to 13 m**, east longitude 0-360 | Verified (the tables were read; the PDF was kept outside the repository) |
| Surveyor 1, 3, 5, 6, 7 | **LROC 2016** (before, NSSDCA, which was shifted by 1 to 4 km: Surveyor 1 by ~4 km and Surveyor 7 by 3.7 km) | Verified (LROC) |
| **Luna 16, 17, 20, 21, 23, 24 and Chang'e 3** (new sites, 14 Nov 2026) | LROC 2016 (robotic). The **years** of these missions are not in the table: they are general knowledge | Verified (coordinates); years unsourced |
| Chang'e 6 | NASA Goddard: https://www.nasa.gov/centers-and-facilities/goddard/nasas-lro-spots-chinas-change-6-spacecraft-on-lunar-far-side | Verified (approximate: ~42° S, ~206° E) |
| Chang'e 4 | LROC (Arizona State University): https://lroc.im-ldi.com/posts/1087 | Verified (not a Chinese-agency source) |
| Viking 1 and 2, Pathfinder, Spirit, Opportunity, Phoenix, Curiosity | Mars Orbital Data Explorer (Washington University in St. Louis): https://ode.rsl.wustl.edu/mars/pagehelp/Content/Missions_Instruments/Landing_Sites.htm | Verified |
| MSL candidates (Gale, Eberswalde, Holden, Mawrth) | same Mars Orbital Data Explorer page (Golombek 2011) | Verified (candidates, not landings) |
| InSight (4.502° N, 135.623° E) | planetary.org, citing Golombek 2019 | Verified (secondary source) |
| InSight, ellipse centre (4.5° N, 135.9° E) | NASA: https://science.nasa.gov/resource/insights-landing-site-elysium-planitia/ | Verified, but it is the target, not the real point |
| Artemis III (region names) | NASA press releases of August 2022 and October 2024 (URLs in the CSV) | Verified; **NASA does not publish coordinates** |
| Chandrayaan-3, SLIM, Oxia Planum | secondary sources (Wikipedia, LROC, ISRO/JAXA unopened) | NOT VERIFIED |
| Perseverance (decimals), Zhurong | search summaries (Nature Astronomy asks for a login) | NOT VERIFIED |
| Mars Polar Lander, Beagle 2 | planetary.org (secondary source) | NOT VERIFIED |

Without coordinates for lack of a reliable source: Artemis III regions, Mars 2, 3 and 6, Schiaparelli, Deep Space 2, NE Syrtis and Columbia Hills.

**Duplicates that are not counted twice** (the `sites.py` filter merges those within 15 km): Surveyor 3 with Apollo 12 (0.2 km; Apollo 12 landed next to the probe), Luna 24 with Luna 23 (2.3 km), and the Lunokhod 1 and 2 and Yutu rovers with their landers (Luna 17, Luna 21 and Chang'e 3). That is why the model uses 6 new lunar sites and not 9. The probe-impact sites in the LROC table (Ranger, GRAIL, LADEE, S-IVB stages) **are not landings** and are not used.
**Still without an LROC table:** Chang'e 4 (LROC, separate publication) and Chang'e 6 (NASA Goddard, approximate) are after 2016.

### `docs/catalog/known_analogs.csv` (10 rows) and `docs/catalog/target_sites.csv` (6 rows)
Written from memory when the skeleton was set up and **checked afterwards with a fourth web search** (Haiku agent, 14 Nov 2026). The columns `coord_source`, `reason_source_url` and `status` say where each value comes from. Result:

**Coordinates:** almost all come from **Wikipedia**, which cites no primary source for them (it only links GeoHack). They locate the place but **are not an official source**. Those of Craters of the Moon, Death Valley, Haughton, Lanzarote and Askja changed somewhat from my remembered value (by up to ~38 km); we use Wikipedia's. For sites that are regions (Atacama, Dry Valleys, Svalbard) the coordinate is a representative point, not a centre.

**Why it is an analog:**
- Verified at NASA: Dry Valleys (Earth Observatory) and Rio Tinto (NASA Astrobiology).
- Verified at ESA: Lanzarote (Mars only).
- Verified in non-NASA/ESA sources: Atacama (article in Frontiers), Haughton (Mars Institute), Craters of the Moon and Death Valley (US National Park Service).
- **Not verified:** Mauna Kea, Askja and Svalbard.

**Target sites:**
- Verified at USGS: Mons Malapert (-85.98°, -1.67°, i.e. 358.33° E).
- The others use Wikipedia, and the USGS Gazetteer returned error 500 on searches.
- **Changes from the first version:**
  - Longitudes moved to 0–360 east-positive, like the rest of the repo.
  - Arcadia Planitia moved from 47°, -170° to 47.25°, 196° E, the centre of the SWIM pilot study (NASA/USGS). This value is still unverified on an opened page.
  - Oxia Planum stays at 18.2°, 335.7° E (ESA 2018 according to planetary.org); Wikipedia gives 18.275°, 335.368°. ESA gave 404.
  - Shackleton (-89.9°) is practically the south pole, so it is described as "rim / south pole" and not as a central point.

### `docs/reference/feature-contract.md`
- The **table of features and their sources** is our proposal; it was not checked that each dataset exists at the needed resolution.
- The **coordinate convention** comes from the USGS documentation: https://planetarynames.wr.usgs.gov/Page/MARS/system (Mars: planetocentric latitude and east-positive longitude) and from the NSSDC Viking page: https://nssdc.gsfc.nasa.gov/planetary/viking.html.

### `data/features/*.parquet` (if they exist)
If they were generated with `python -m astroatlas.synthetic`, they are **synthetic data**: random and without scientific value, and any metric computed with them (AUC, recall) means nothing. `moon.parquet` and `mars.parquet` generated with `python -m astroatlas.data.moon` / `mars` are real data (next section).

### `data/features/moon.parquet` and `mars.parquet`: all variables from the NASA PDS
**Team rule:** all data entering the model comes from NASA. For the Moon and Mars, everything comes from the **NASA Planetary Data System, Geosciences Node** (`pds-geosciences.wustl.edu`). URLs checked with HTTP 200 on 14 November 2026. Code: `src/astroatlas/data/pds_dem.py` (topography) and `src/astroatlas/data/planetary.py` (the rest). Window: cells with their centre within ≤ 25 km of the site; if the product is coarser, the nearest cell.

| Variable | Body | Product (NASA mission) | URL | Reference | Level |
|---|---|---|---|---|---|
| `topo__*` | Moon | LRO LOLA LDEM_256 (256 px/°, ~118 m) | https://pds-geosciences.wustl.edu/lro/lro-l-lola-3-rdr-v1/lrolol_1xxx/data/lola_gdr/cylindrical/img/ | LOLA GDR | Verified. Replaces the USGS mosaic (same data); elevations checked: Apollo 11 −1,935 m |
| `topo__*` | Mars | MGS MOLA MEGDR 128 px/° (~463 m) | https://pds-geosciences.wustl.edu/mgs/mgs-m-mola-5-megdr-l3-v1/mgsl_300x/meg128/ | MOLA MEGDR | Verified. Replaces the USGS mosaic; Olympus Mons 20,018 m, Jezero −2,647 m, Gale −4,502 m |
| `thermal__t_max_k`, `thermal__t_range_k` | Moon | LRO Diviner, Global Cumulative Products, bolometric temperature, 0.5° × 0.25 h of local time | https://pds-geosciences.wustl.edu/lro/urn-nasa-pds-lro_diviner_derived1/data_derived_gcp/ | Williams et al. (2017), Icarus 283, 300-325 | Verified. Maximum and (max − min) of the diurnal curve, area-weighted mean |
| `ice__water_frac` | Moon | LRO Diviner, southern Polar Resource Product | https://pds-geosciences.wustl.edu/lro/urn-nasa-pds-lro_diviner_derived1/data_derived_prp/ | Paige et al. (2010), Science 330, 479 | Verified. Fraction of the area with stable ice at ≤ 1 m; it is a thermal model fitted to data. Only > 80° S; **outside that zone it is NaN** (it used to be set to 0 as an assumption; fixed on 14 Nov) |
| `geo__basalt_frac` | Moon | Lunar Prospector GRS, elemental abundances (FeO), 5° pixel | https://pds-geosciences.wustl.edu/lunar/lp-l-grs-5-elem-abundance-v1/lp_9001/data/ | Prettyman et al. (2006), JGR 111, E12007 | Verified. **Our proxy**: (FeO − 5) / 15, clipped to 0-1 |
| `ice__water_frac` | Mars | Mars Odyssey GRS, H2O_SR_5X5 (H2O in % by mass) | https://pds-geosciences.wustl.edu/ody/ody-m-grs-5-elements-v1/odgm_xxxx/data/smoothed/ | ODY-M-GRS-5-ELEMENTS-V1.0 | Verified. % / 100. No data beyond ±57.5° and gaps between 45° and 60° (checked in the table: 94 of 216 cells with data between 45° and 60° N/S). Arcadia (47.25° N) and Phoenix (68.2° N) stay NaN |
| `geo__basalt_frac` | Mars | Mars Odyssey GRS, FE_SR_5X5 (Fe in % by mass) | same URL | ODY-M-GRS-5-ELEMENTS-V1.0 | Verified. Same proxy as the Moon with FeO = Fe × 1.2865; saturates at 1 over almost all of Mars |
| `thermal__*` | Mars | — | — | — | **NO DATA**: there is no maximum/minimum temperature map in the PDS. Stays NaN |

**Comparability:** `ice__water_frac` does not measure the same on each body (Moon: area with stable ice according to a model; Mars: measured % of water; Earth: snow cover). This must be said in the profiles.

### `data/features/earth.parquet` and `earth_sites.parquet`: real Earth data (14 Nov 2026)
5° grid (955 land cells; `earth_sites` = the known analogs, only to compare and validate). 50 × 50 km window per cell. Code: `src/astroatlas/data/{copernicus,earth,earth_water,edl}.py`.

| Variable | Product (agency) | Detail | Level |
|---|---|---|---|
| `topo__*` | Copernicus GLO-90 (ESA, AWS Open Data) | 1° tiles read decimated to ~360 m; common 500 m baseline with the Moon and Mars | Verified (Death Valley -85.5 m, Dead Sea -427 m, South Pole 2,801 m; Everest comes out at 8,605 m because of the decimation) |
| `thermal__t_max_k`, `thermal__t_range_k` | MODIS/Terra LST Monthly `MOD11C3` v061 (NASA LP DAAC), year 2019 | **surface temperature**. `t_max` = maximum over the 12 months of the monthly mean daytime LST; `t_range` = mean of (day − night). 886.7 MB downloaded in 168 s, each file deleted after reducing it | Verified (Death Valley 323 K, Sahara 324 K, Dry Valleys 263 K, interior Antarctica 251 K). **Monthly means, not the instantaneous peak** |
| `thermal_air_*` (diagnostic) | POWER (NASA Langley) | 2 m air temperature, the earlier value. Its "range" was the **seasonal** difference (median 56 K), not the diurnal one: it was mislabelled | discarded |
| `ice__water_frac` | MODIS/Terra Snow Cover Monthly `MOD10CM` v061 (NASA NSIDC), year 2019 | annual mean of the snow cover (0-1) of the valid pixels of the window. 15.8 MB downloaded in total (12 files, each deleted after reducing it) | Verified (Greenland 1.00, Antarctica 1.00, Sahara 0.00, Amazon 0.00, Dry Valleys 1.00) |
| `ice_precip_proxy` (diagnostic) | POWER | the earlier precipitation proxy; kept but **no longer enters the model** (it gave 1.0 in the Amazon) | discarded |
| `ice_snow_cover_max`, `ice_snow_months_valid` (diagnostic) | MOD10CM | monthly maximum and number of months with data | verified |
| `geo__basalt_frac` | **GLiM** v1.0 on a 0.5° grid (Hartmann and Moosdorf 2012; **not from NASA**, exception approved by the team on 14 Nov 2026) | fraction of the rock cells of a **75 km** window whose dominant lithological class is "basic volcanic" (`vb`). 38 kB download, CC-BY 3.0 | Verified: gets 11 of 13 known basaltic sites right and 0 of 9 false positives (see below) |
| `geo_glim_mafic_frac`, `geo_glim_class`, `geo_glim_rock_cells` (diagnostic) | GLiM | mafic fraction (basic volcanic + basic plutonic), dominant class and number of rock cells | verified |
| (tested and discarded) | ASTER GED (NASA LP DAAC) | mafic index (band 12 / band 13, Ninomiya 2005) of the infrared emissivity | Not usable: see below |

**Earth geology: tested with ASTER GED and discarded (14 Nov 2026).** A monthly `AG5KMMOH` file was downloaded (337 MB; emissivity = DN × 0.002 + 0.49 in 5 thermal bands, plus NDVI), the mafic index `MI = b12/b13` was computed and validated with places of known lithology (none from our analog list):
- **Where there is data, it separates:** basalt (Mauna Loa 0.925, Pinacate 0.939, Harrat Rahat 0.957, Erta Ale 0.958) versus sand and quartz (Rub al Khali 0.755, Great Sand Sea 0.791, Namib 0.809), with paired AUC 1.00. **It is a sample of 4 against 6.**
- **But it covers very little:** of the 10 basaltic places, 6 have no usable pixels. Craters of the Moon and Harrat Khaybar have a **flat, high-emissivity spectrum (~0.97)**, typical of dark lava, which the contrast mask discards. Askja and others come out flat because of snow or vegetation.
- **Coverage in our grid:** only **84 of 955 cells (9 %)** have ≥ 50 % usable pixels (0 of 273 south of 60° S, 0 of 180 north of 60° N; almost all between 0° and 30° N). In **57 %** of the cells the spectrum is flat and of high emissivity, and there dark lava, ice, water and sparse vegetation **are indistinguishable**.
- **Bias:** in cells that mix both pixel types, the mask keeps the high-contrast ones (sand, ash, felsic rocks) and discards the flat lava, that is, it would bias towards the felsic.
- **Conclusion:** as an index for `geo__basalt_frac` it is not reliable and was replaced by GLiM (next paragraph).

**Earth geology with GLiM (14 Nov 2026).** Source: Hartmann, J. and Moosdorf, N. (2012), *Global Lithological Map Database v1.0 (gridded to 0.5° spatial resolution)*, PANGAEA, https://doi.org/10.1594/PANGAEA.788537; paper: *Geochemistry, Geophysics, Geosystems* 13, Q12004, https://doi.org/10.1029/2012GC004370. CC-BY 3.0 licence (it must be cited). File: `hartmann-moosdorf_2012.zip` (38.7 kB), from https://epic.awi.de/id/eprint/31092/ ; ESRI ASCII of 720 × 360 cells with **one dominant class per cell**; the zip is extracted with path checking. The meanings of the codes (`vb` = basic volcanic, etc.) come from the paper, not from the file.
- **Validation with places of known lithology (none from our analog list):** 11 of 13 basaltic sites classified as `vb` (Mauna Loa, Craters of the Moon, Harrat Rahat and Khaybar, Pinacate, San Francisco, Erta Ale, Askja, Deccan, Karoo, Paraná); 0 of 9 non-basaltic sites (sand seas, Amazon, Canadian Shield, Alps) as `vb`. Failures: **Etna** (no data in a coastal cell) and the **Columbia River basalt** (comes out as sediments because of the loess covering it).
- **In our grid:** 715 of 955 cells with data (240 are ice, water or no data: NaN), 81 with some basalt, 13 with 1.0. Those with the most basalt are real provinces: Ethiopia, Paraná, Faroe Islands, Haruj (Libya), the Ross and Marie Byrd volcanic zones (Antarctica). Analogs: Mauna Kea 0.75, Askja 1.00, Craters of the Moon 0.50, Atacama 0.00, Death Valley 0.00; Lanzarote no data (small islands do not enter the 0.5° grid).
- **Limitations:** (1) a single dominant class per ~55 km cell: a cell with 40 % basalt and 60 % sediments counts as sediments, so the fraction **underestimates**; (2) that is why the window is 75 km (~2 × 2 to 3 × 3 cells), larger than the 25 km of the other variables; (3) Earth's basalt fraction (rock area) **does not measure the same** as the lunar and Martian proxy (based on FeO); (4) under ice (Antarctica) GLiM gives the subglacial rock, which is not a visible surface.
- **Exception to the "NASA only" rule:** decided by the team; the rest of the Moon and Mars geology dimension remains from the PDS.

**Limitations of snow as "ice":** it is not subsurface ice (the Moon measures stable ice at ≤ 1 m and Mars soil water). In polar night the product has no data, so the annual mean of the polar cells uses only the months with light (7 to 11 of 12); bias towards high values. 20 cells (almost all the Ross Ice Shelf) stay NaN because MODIS masks them as ocean. Sea ice can count as snow.

**Water (ocean, lakes and inland seas):** Copernicus fills water with a constant height (0 m at sea), and without a filter those cells came out as "perfect plains". Cells with **local relief < 1 m at any altitude** are discarded (14 Nov, second version; the first also required elevation ~0 and let lakes like Michigan or the Caspian through). With the 5° grid the flattest real flat terrain (Antarctic ice, wetlands, plains) has relief >= 4 m, so there is a margin. 951 cells remain. It may remove a small island (e.g. in the Faroe Islands, almost all sea in the 50 km window).

**GLDAS (15 Nov 2026):** GESDISC licence approved, download and reduction tested with real data (12 months of 2019, 300 MB downloaded and deleted). `ice_soil_moisture_m3m3` and `ice_swe_kg_m2` are in `earth*.parquet` as **diagnostics**; the preregistered comparison ([../preregistrations/ice.md](../preregistrations/ice.md)) showed it does not improve on snow, so they do not enter the model.

### Viability by proximity to populated places (Earth only; 14 Nov 2026)
**Rule decided by the team:** a point is **not viable** if there is a settlement of **1,000 inhabitants or more within 50 km**. It is a **flag** (`viable` column), not part of the score: it changes neither the ranking, the ablation nor the validation with known analogs. It can be hidden in the app (box checked by default) and in `data/results/candidates_viable.csv`.

**Source (NASA SEDAC):** *Global Rural-Urban Mapping Project, Version 1 (GRUMPv1): Settlement Points, Revision 01* (CIESIN, Columbia University, et al. 2017), https://doi.org/10.7927/H4BC3WG1. A 2.85 MB CSV (zip) with 70,629 settlements and their population, downloaded with the Earthdata login and extracted with path checking. Code: `src/astroatlas/data/settlements.py` (`python -m astroatlas.data.settlements`).

**Columns added** to `earth.parquet`, `earth_sites.parquet` and `earth_usgs.parquet` (not model variables): `dist_settlement_km`, `settlement_name`, `settlement_country`, `settlement_pop` (the nearest settlement of >= 1,000 inhabitants), `dist_any_settlement_km` (to the nearest of any kind, even without population: warning) and `viable`. The population is `ES00POP` (year 2000) if it exists, otherwise `Pop` of the available year; 1,629 points have no population and do not count for `viable`.

**Result:** 708 of the 951 grid cells are viable (74 %). **5 of the 10 known analogs are not viable** (Mauna Kea 28.6 km from Honokaa, Lanzarote 4.2 km, Río Tinto 23.5 km, Svalbard 1.1 km —its coordinate is Longyearbyen—, Craters of the Moon 28.5 km from Arco, of 1,026 inhabitants, almost at the threshold). **That is why the flag is not applied to the validation:** analog training fields are used near towns, and filtering them would penalise legitimate analogs. The filter is for **finding new candidates**.

**Important limitations (from the SEDAC documentation and checked):**
- **The list is "best available" and NOT exhaustive:** the probability that a settlement is included grows with its population, so towns of 1,000 to 10,000 inhabitants are less well covered. **Checked: San Pedro de Atacama does not appear**, and our Atacama analog comes out "viable" (150 km from Antofagasta).
- **No Antarctic stations or extreme Arctic settlements** (latitudes from -54.8° to 78.9°): the 273 cells below latitude -60° all come out "viable", which **does not mean they are uninhabited** (there are research stations).
- **Data from 1990 to 2010:** populations and settlements have changed.
- "Viable" means *"no known settlement of >= 1,000 inhabitants in this list within 50 km"*, not *"uninhabited"*. For scattered or unlisted populations a population-density layer (GPWv4, also from SEDAC) or night lights (Black Marble) would be needed; they are not used.
- Distance is measured from the point's centre, not from the 50 km window, and each grid cell is a ~550 km sample.
- The source's names carry an artefact (493 names with "ÿ" instead of a space) that is corrected on reading; they are for display only.

### Review of the PDS delivery (14 Nov 2026) and remaining limitations
Integrated with `dem.py` merged (accepts an already-created DEM and keeps the network retries). The PDS topography coincides with what had been computed before with the USGS mosaics (e.g. Shackleton 11.52° in both). Open problems:

- **Mars `thermal__*` empty (14/14 sites).** Search of 14 Nov: **there is no ready global map of maximum/minimum temperature in the PDS**, so the delivery's statement is correct in essence. There are two paths, checked:
  - **MRO MCS, DDR v5** (PDS Atmospheres Node, NMSU; `https://atmos.nmsu.edu/PDS/data/MROM_2062/...`). Each profile carries `T_SURF` (surface temperature, K), `SURF_LAT/LON`, `LTST` (local solar time) and `L_S` (checked in `MCS_DDR1.FMT`). There is no gridded product: it has to be downloaded and filtered. Files of ~7 MB per 4 h stretch (6 per day, about 393 profiles each), ~29 GB per Martian year. It would allow estimating the maximum (afternoon) and the range (afternoon − night) per site, with a few dozen profiles per site and year.
  - **MGS TES, thermal-inertia maps `MGS-M-TES-5-TIMAP-V1.0`** (PDS Geosciences, `https://pds-geosciences.wustl.edu/mgs/mgs-m-tes-5-timap-v1/mgst_9001/data/`). Global day and night maps, 7200 × 3600 int16 (20 px/°, ~3 km), 51.8 MB each, with an interpolated-pixel mask (< 8 %). **Thermal inertia only** (5 to 5000 J m⁻² K⁻¹ s⁻½), not temperature. It is what controls the diurnal amplitude, but it is not equivalent to `t_max`/`t_range`.
  - **Team decision (14 Nov): neither path is used.** Mars `thermal__*` stays NaN and the thermal dimension does not score for Martian sites (the model ignores it). Consequence: Mars sites are compared with Earth only on topography, ice and geology, and Moon sites on all four dimensions, so their scores are not comparable between bodies. It can be reopened if time allows. (Thermal inertia was later tested as an experiment: [../preregistrations/thermal-inertia.md](../preregistrations/thermal-inertia.md).)
  - Discarded: TES global temperature "sampler" (only GIF images), USGS THEMIS IR mosaics (*relative* temperature, stretched and blended, not calibrated) and TES TSDR (raw records, enormous).
- ~~Moon `ice__water_frac` = 0 by assumption~~ **Fixed (14 Nov):** the 13 sites outside Diviner's coverage (> 80° S) are now NaN; only Shackleton (0.60) and Malapert (0.42) have data. Consequence: at those 13 sites the ice dimension no longer scores (it is ignored), instead of comparing against an invented 0. The north pole is not covered by this file either.
- **Mars `geo__basalt_frac` saturates at 1.0** at almost all sites: the proxy (FeO of 5 to 20 %) is calibrated for the Moon and does not discriminate on Mars.
- ~~Ice on Mars~~ **Clarified (14 Nov):** the parser is correct. The H2O_SR_5X5 product does not cover beyond ±57.5° and has gaps between 45° and 60° (Viking 2 falls in a cell with data; Arcadia and Phoenix in cells without data). The NaNs are real. High-latitude ice data for Mars (where the water is) are not in this product; they must be sought separately (later done with Odyssey neutrons).
- **Non-comparable scales between bodies:** ice is a modelled fraction on the Moon, a measured % on Mars and a precipitation proxy on Earth (later snow cover). The lunar surface temperature (~395 K at the equator) falls outside the whole Earth range (POWER measures air and reaches ~330 K): equatorial lunar sites will score almost 0 in that dimension against any Earth cell.
- **Earth `geo__*` empty (at that time):** without lithology that dimension is not compared and the model ignores it (later filled with GLiM).
- Minor detail: `planetary.py` uses a Mars radius of 3389.5 km and `pds_dem.py` 3396 km (0.2 %, no relevant effect).

## Known problems in the sources
- ~~Longitude sign in NSSDC~~ **Resolved (14 Nov 2026):** the LROC table gives Apollo 12 at 336.5781° E and Apollo 14 at 342.52806° E, exactly what had been converted assuming the negative was west. The assumption was correct.
- **NSSDC Mars Mileage Guide:** the Spirit and Opportunity longitudes seem swapped. It was not used.
- **Viking 1 and Pathfinder:** three sources give different values (e.g. Viking 1: 22.269° N / 312.049° E in ODE, 22.54° N / 48.23° W in the Mileage Guide). The Mars Orbital Data Explorer was used without resolving which is correct.
- **Chandrayaan-3:** ISRO gives the planned site, not the real touchdown point.
- **Pages that could not be opened:** PDS Geosciences (403), Apollo Lunar Surface Journal (404), JAXA PDF (403), ESA Oxia Planum (404), Nature Astronomy (login). The USGS Gazetteer ZIP/KML files were not downloaded.

## Pending verification
1. Open the NSSDC master catalogue and the HiRISE pages for Perseverance, Zhurong and the failed missions.
2. Download the USGS Gazetteer ZIP/KML files and see whether they carry landing points.
3. Confirm the official coordinates of SLIM, Chandrayaan-3 and Chang'e 5/6 with ISRO, JAXA and CNSA sources (Chang'e 3 is already verified with LROC).
4. Replace Wikipedia coordinates with primary sources (USGS Gazetteer, NASA, GVP, GNIS) and verify the analogy of Mauna Kea, Askja and Svalbard.
5. Verify the centre of Arcadia Planitia in the SWIM PDF, and that of Oxia Planum at ESA.

## Vegetation flag (15 Nov 2026)
NASA product **MODIS MOD13C2 v061** (monthly NDVI, 0.05° CMG grid, LP DAAC), 12 months of 2019 (1,242 MB downloaded and deleted after reducing them). Code: `src/astroatlas/data/earth_vegetation.py`. Per 50 km cell: `veg_ndvi_mean`, `veg_ndvi_max` and `vegetated` (annual maximum NDVI ≥ 0.2; with no data it is not flagged). It is a **context flag**, like `viable`: it enters neither the score nor the validation. Reason: the model has no biology dimension, and without it rainforests came out as candidates "similar to Mars". With the 0.2 threshold: 551 of 951 cells with vegetation; of the 10 known analogs, 4 (Mauna Kea, Río Tinto, Svalbard, Craters of the Moon). The threshold was set by us (sparse shrub upwards) and is not calibrated against a source.

## Dust and wind (15 Nov 2026, context only)
**NASA MERRA-2** monthly: `M2TMNXAER` (dust: DUSMASS at the surface and DUCMASS in the column) and `M2TMNXSLV` (U10M, V10M), 12 months of 2019, about 80 MB per month and product (~1.9 GB downloaded and deleted). Code: `src/astroatlas/data/earth_dust_wind.py`. Per cell the MERRA-2 cell (0.5° × 0.625°) containing the centre is taken, **not** a window mean. Wind is the speed of the monthly-mean wind, which **underestimates gusts**. Diagnostic columns: `dust_surface_ugm3`, `dust_column_mgm2`, `wind10m_ms`; they do not enter the model because there is no counterpart on Mars or the Moon (see [../context/unmodeled-dimensions.md](../context/unmodeled-dimensions.md)).

## Caves and lava tubes (15 Nov 2026, context only)
See [../context/caves-and-lava-tubes.md](../context/caves-and-lava-tubes.md). **Moon:** `Pit-locations` layer (278 pits) by Losarcos and Dombard (Zenodo 10.5281/zenodo.20516852, CC BY 4.0, 28.9 kB), extracted with `safe_extract`; code `src/astroatlas/data/caves.py`. **Earth:** index of the Pyroduct Digital Catalog v1 (Zenodo 10.5281/zenodo.14535886, CC BY 4.0): the RAR file (41.7 MB) was downloaded, its contents listed (names without dangerous paths) and only the `.xlsx` index, the README and the licence were extracted into an isolated folder; the 498 MB DXF was not extracted. Result: `docs/catalog/documented_lava_tubes.csv` (93 tubes, **without coordinates**). **Mars:** Mars Global Cave Candidate Catalog (USGS, Cushing; PDS 2019), 1,062 candidates; the USGS server blocks automatic download, so a team member did it. Code: `load_mars_caves` in `caves.py`; the CSV header is scrambled and the XML order is used (`ID_Tag, Longitude, Latitude, Type_Code, Priority, …`).

## Mars thermal inertia (15 Nov 2026, experiment not adopted)
**MGS-TES, thermal-inertia map** (Putzig and Mellon 2007, *Icarus* 191, 68-94; PDS Geosciences `mgs-m-tes-5-timap-v1`, 66.4 MB zip, units J·m⁻²·K⁻¹·s⁻¹ᐟ²). Downloaded to `data/raw/tes_ti/` and only the `data/` directory extracted; the night map and its mask are kept, and the zip and the day files were deleted. Code: `src/astroatlas/inertia.py`. Check values: Gale 393, Jezero 295, Phoenix 88. **It does not enter the model**: the preregistered experiment worsened the result ([../preregistrations/thermal-inertia.md](../preregistrations/thermal-inertia.md)).

## MODIS emissivity as a basalt index (15 Nov 2026, tested and discarded)
The MOD11C3 emissivity contrast (`C = E29 − (E31 + E32)/2`) was tested as a measure of basalt, with a preregistered protocol ([../preregistrations/emissivity.md](../preregistrations/emissivity.md)). **Phase 1 failed** (coverage 64 % of the cells against the 80 % required; AUC 0.69 against 0.80): the index separates quartz sand seas but not basalt from vegetation-covered or quartz-free terrain. One month (July 2019) was downloaded and deleted. Code: `src/astroatlas/emissivity.py`. Geology remains GLiM.

## Limitation of Mars ice coverage (15 Nov 2026)
Mars Odyssey GRS's `h2o_sr_5x5.tab` map (hydrogen, PDS `ody-m-grs-5-elements-v1`) **has no values between ≈ 57° and 90° latitude** in either hemisphere and has gaps between 42° and 57° N (1,084 of 2,592 cells without data). **Phoenix (68.2° N) and Arcadia Planitia (47.25° N) end up with `ice__water_frac` = NaN**; Viking 2 (47.7° N) has 0.046. The 12 Mars targets with data have between 0.03 and 0.07 of water (all dry). Details and implications: [../preregistrations/models.md](../preregistrations/models.md).

## Mars hydrogen at the poles: Odyssey epithermal neutrons (15 Nov 2026)
**NASA PDS, Mars Odyssey GRS, Averaged Neutron Data v2.0** (`ODY-M-GRS-5-AND-V2.0`, DOI 10.17189/1522868): 287 binary tables of 5° × 5° with the epithermal count rate (`CEPI`) per 15° Ls interval, with pole-to-pole coverage (about 33 MB, in `data/raw/ody_and/`, not versioned). Code: `src/astroatlas/polar_ice.py`. It is used for a **relative hydrogen index** `H` (not water-equivalent) with a season rule fixed beforehand; the validity gate against the already-measured hydrogen is met (Spearman ρ = 0.816). Phoenix comes out clearly ice-rich (`H` = 1.30) and Arcadia is a borderline case (0.39). See [../preregistrations/polar-ice.md](../preregistrations/polar-ice.md). The permafrost variable built with it is **not adopted** (inconclusive result).

## Second set of analogs (15 Nov 2026; `docs/catalog/analogs_set2.csv`)
Reason for each analog (open source that names it; coordinates to be verified): Wudalianchi ([Wikipedia](https://en.wikipedia.org/wiki/Wudalianchi_volcanic_field), citing Xiao and Wang 2009), Namib ([Lorenz 2016, Geological Survey of Namibia](https://mme.gov.na/files/publications/0b4_Comms%20GSN%2017%203.%20Lorenz%2C%20Titan-Namibia%2C%202016.pdf)), Bruneau ([Smithsonian](https://repository.si.edu/server/api/core/bitstreams/49d010e0-a4a4-4b18-a1d6-22bbe5d1f5fe/content)), Maspalomas ([Cornwall et al., Icarus 2018](https://pure.ulster.ac.uk/ws/files/12423600/Cornwall_et_al_Icarus_article_2018.pdf)), MDRS ([Mars Society](https://wikipedia.com/wiki/Mars_Desert_Research_Station)), Strelley Pool ([NASA NTRS](https://ntrs.nasa.gov/api/citations/20160006681/downloads/20160006681.pdf)), CRREL/Fairbanks ([Boisson et al.](https://openpolar.no/Record/ftinsu:oai:HAL:insu-02564101v1)), Tuktoyaktuk ([NWT licence](https://data.researchlicensing.ece.gov.nt.ca/Scientific/17243)), Teide ([ESA via TechRadar](https://www.techradar.com/news/want-to-visit-the-moon-here-on-earth-try-tenerife-like-the-esas-new-rover-robots)). Feature data: the same as the earlier 23 (Copernicus GLO-90, MODIS MOD11C3/MOD10CM 2019, GLiM).

## Shallow-ice targets (15 Nov 2026; `docs/catalog/dundas_ice_targets.csv`)
Coordinates of 8 sites with exposed ice read from the text, figures and Table 1 of Dundas et al. (2021), *Widespread Exposures of Extensive Clean Shallow Ice in the Mid-Latitudes of Mars*, JGR Planets 126, e2020JE006617 (open copy: [HAL hal-03186594](https://hal.science/hal-03186594)). The full catalogue (USGS data release [10.5066/P9Y8FR1R](https://doi.org/10.5066/P9Y8FR1R), CC0) could not be downloaded because of ScienceBase's anti-bot check and is not used.

## Third set of analogs (15 Nov 2026; `docs/catalog/analogs_set3.csv`)
Expert catalogue: Preston, L., Grady, M. and Barber, S. (2012), *The Catalogue of Planetary Analogues* (CAFE TN2, The Open University for ESA, contract 4000104716/11/NL/AF), [PDF](https://freight.cargo.site/m/D1821053255089660420449933921929/The-Catalogue-of-Planetary-Analogues.pdf). Only names, Moon/Mars assignment (the "Directory" table) and coordinates are taken from it; the PDF stays in `data/raw/cafe/` (not versioned).

## Permafrost map (15 Nov 2026)
Obu, J., Westermann, S., Kääb, A. and Bartsch, A. (2018), *Ground Temperature Map, 2000-2016, Northern Hemisphere Permafrost*, PANGAEA, [doi:10.1594/PANGAEA.888600](https://doi.org/10.1594/PANGAEA.888600), ESA GlobPermafrost project. 25 km file (`UiO_PEX_5.0_20181127_2000_2016_25km.nc`, variable `PerProb`); it stays in `data/raw/permafrost/` (not versioned).

## Place and country names in the app (15 Nov 2026)
Natural Earth 1:110m, layers `ne_110m_admin_0_countries` and `ne_110m_geography_regions_polys` (public domain; https://www.naturalearthdata.com). They are simplified in `src/astroatlas/data/places.json` (`python -m astroatlas.places --build`; the raw data stay in `data/raw/naturalearth/`, not versioned). The app's place and country names are available in English (`NAME_EN`) and Spanish (`NAME_ES`).

## Orbital images of the visual comparison (15 Nov 2026)
- **Earth:** NASA GIBS (Global Imagery Browse Services), WMS service `https://gibs.earthdata.nasa.gov/wms/epsg4326/best/wms.cgi`; layers `MODIS_Terra_CorrectedReflectance_TrueColor` (day 2023-07-15) and `BlueMarble_NextGeneration` (2004-07-01).
- **Mars:** NASA Trek, `Mars_Viking_MDIM21_ClrMosaic_global_232m` (WMTS tiles `default028mm`, levels 0 to 7).
- **Moon:** NASA Trek, `LRO_WAC_Mosaic_Global_303ppd_v02` (WMTS tiles `default028mm`, levels 0 to 8).
The images are downloaded live (not stored in the repository) and shown with their credit.
