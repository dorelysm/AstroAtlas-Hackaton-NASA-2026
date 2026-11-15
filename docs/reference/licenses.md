# Data licences and attribution

Status as of 15 Nov 2026. **"Checked"** = the condition was read in the source's own documentation during the project.
**"To check"** = it is what we know about the source but its licence page could not be opened (in the 15 Nov check two servers, SEDAC and Copernicus, refused the connection): it must be opened before submission.

| Data | Source | Licence / conditions | Status | What to cite |
|---|---|---|---|---|
| Earth topography | Copernicus DEM GLO-90 (ESA / European Commission, via AWS Open Data) | "GLO-30 Public and GLO-90 are available on a free basis for the general public under the terms and conditions of the Licence" ([licence page](https://dataspace.copernicus.eu/explore-data/data-collections/copernicus-contributing-missions/collections-description/COP-DEM)) | Checked (15 Nov 2026) | "Contains modified Copernicus data" (year of the data) and a link to the Copernicus DEM licence page |
| Surface temperature | NASA MODIS MOD11C3 v061 | NASA EOSDIS open data | Checked (15 Nov 2026) | Wan, Z., Hook, S., & Hulley, G. (2021). MODIS/Terra Land Surface Temperature/Emissivity Monthly L3 Global 0.05Deg CMG V061 [Data set]. NASA Land Processes DAAC. https://doi.org/10.5067/MODIS/MOD11C3.061 |
| Dust and wind (context) | NASA MERRA-2 (M2TMNXAER, M2TMNXSLV v5.12.4; GES DISC) | Open, requires the GESDISC licence (accepted) | Checked (the download works) | GMAO (2015), MERRA-2 tavgM_2d_aer_Nx and tavgM_2d_slv_Nx, and the product DOI; Gelaro et al. (2017), *J. Climate* 30, 5419-5454 |
| Lunar pits | Losarcos and Dombard (2026), Zenodo 10.5281/zenodo.20516852 (from LROC QuickMap, Wagner and Robinson) | CC BY 4.0 | Checked (Zenodo API) | Losarcos and Dombard (2026) and Wagner and Robinson (2014) |
| Terrestrial lava tubes | Pyroduct Digital Catalog v1, Zenodo 10.5281/zenodo.14535886 | CC BY 4.0 | Checked (LICENSE.txt and README) | Romio, F. A. P. and Lobosco, G. (2024), doi:10.5281/zenodo.14535886 |
| Mars caves | USGS Astrogeology, Mars Global Cave Candidate Catalog (Cushing; PDS release 2019) | USGS-authored data are in the U.S. public domain (USGS copyright policy); the USGS asks for credit | Checked in the USGS policy (15 Nov 2026); the catalogue page itself has no separate licence text | Cushing, G. E., Mars Global Cave Candidate Catalog, USGS/PDS (2019). Credit: U.S. Geological Survey |
| Mars thermal inertia (experiment) | MGS-TES, Putzig and Mellon 2007; PDS Geosciences `mgs-m-tes-5-timap-v1` | Open (NASA PDS) | To check | Putzig, N. E. and Mellon, M. T. (2007), *Icarus* 191, 68-94, doi:10.1016/j.icarus.2007.05.013 |
| Mars epithermal neutrons (polar ice) | NASA PDS, Mars Odyssey GRS, Averaged Neutron Data v2.0 (`ODY-M-GRS-5-AND-V2.0`) | Open (NASA PDS) | To check | GRS Science Team (Univ. of Arizona), DOI 10.17189/1522868, PDS Geosciences Node |
| Vegetation (flag) | NASA MODIS MOD13C2 v061 | NASA EOSDIS open data | To check (citation text not yet copied) | Cite the product and its DOI (LP DAAC) |
| Snow | NASA MODIS MOD10CM v61 | NASA EOSDIS open data | Checked (15 Nov 2026) | Hall, D. K. & Riggs, G. A. (2021). MODIS/Terra Snow Cover Monthly L3 Global 0.05Deg CMG (MOD10CM, Version 61) [Data set]. Boulder, Colorado USA. NASA National Snow and Ice Data Center DAAC. https://doi.org/10.5067/MODIS/MOD10CM.061 |
| Soil moisture (diagnostic only) | NASA GLDAS Noah 2.1 (GES DISC) | Open, requires accepting the GESDISC licence in Earthdata (done) | Checked (download works) | Rodell et al. (2004), *BAMS* 85, 381-394, and the product DOI |
| Earth geology | GLiM v1.0 (Hartmann and Moosdorf 2012), PANGAEA | **CC-BY 3.0**. **Not from NASA** (exception approved by the team on 14 Nov 2026) | Checked | Hartmann, J. and Moosdorf, N. (2012), *Geochem. Geophys. Geosyst.* 13, Q12004, doi:10.1029/2012GC004370; data doi:10.1594/PANGAEA.788537 |
| Settlements | NASA SEDAC GRUMP v1 Settlement Points Rev. 01 | SEDAC open data | Checked (15 Nov 2026) | CIESIN-Columbia University, IFPRI, World Bank, & CIAT (2017). Global Rural-Urban Mapping Project, Version 1 (GRUMPv1): Settlement Points, Revision 01 (Version 1.01) [Data set]. Palisades, NY: NASA Socioeconomic Data and Applications Center (SEDAC). https://doi.org/10.7927/H4BC3WG1 |
| Analog layer | USGS, Hunter (2020) "Known Terrestrial Analog Sites for Planetary Science" | Public domain (USGS metadata); the craters come from the Earth Impact Database (Univ. of New Brunswick) | Checked in the metadata | Hunter (2020), doi:10.5066/P9J72921; also cite the Earth Impact Database |
| Moon: topography, thermal, ice | LRO LOLA, LRO Diviner, Lunar Prospector GRS (NASA PDS) | Open (PDS); cite with the PDS DOI of each bundle, the most granular product used | Checked (15 Nov 2026): PDS citation practice read; the DOI of each volume is still to be copied | Cite each instrument and its PDS bundle DOI |
| Mars: topography, ice | MGS MOLA, Mars Odyssey GRS (NASA PDS) | Open (PDS); cite with the PDS DOI of each bundle, the most granular product used | Checked (15 Nov 2026): PDS citation practice read; the DOI of each volume is still to be copied | Cite each instrument and its PDS bundle DOI (Odyssey neutrons: 10.17189/1522868) |
| Lunar site coordinates | LROC tables (Wagner et al. 2017, *Icarus* 283, 92-103; ASU/NASA) | Open scientific publication | Checked (the tables were read) | Wagner et al. 2017 |

## What is redistributed in the repository
- `demo_data/` (≈ 1.4 MB) contains **derived values** (statistics per 50 km cell), not the original data. Even so, each source above asks to be cited; the citation is in this file, in [data-sources.md](data-sources.md) and in the README.
- Raw data and downloads are **not** versioned (`data/` is in `.gitignore`).
- GLiM (CC-BY 3.0) allows redistributing derived works **if attributed**: that attribution is mandatory in the submission.

## Pending before submission
1. Copy the PDS bundle DOI of each volume used (LOLA, Diviner, Lunar Prospector, MOLA, Odyssey, TES) into the table, and the MODIS MOD13C2 citation.
2. Keep the credits line with the main sources in the presentation and in the app (the app already has a credits section, including the GIBS acknowledgement).
3. Trek: no data-use or acknowledgement text was found on the Trek home page; see "NASA imagery in the app" below.

## Dundas et al. 2021 (shallow-ice coordinates)
Citation: Dundas, C. M., Mellon, M. T., Conway, S. J., Daubar, I. J., Williams, K. E., et al. (2021). Widespread Exposures of Extensive Clean Shallow Ice in the Mid-Latitudes of Mars. *Journal of Geophysical Research: Planets*, 126(3), e2020JE006617. doi:10.1029/2020JE006617 (open copy: HAL hal-03186594). Only **eight coordinate pairs** are taken (facts, not text). The USGS data release (10.5066/P9Y8FR1R) is CC0 but was not downloaded. The PDF and its extracted text stay in `data/raw/swim/` (not versioned).

## ESA CAFE catalogue (Preston, Grady and Barber 2012)
Only facts are taken (names, body assignment and coordinates), not text. The licence or reuse conditions of the PDF (hosted on a third-party server) are **to check**; the document is a report by ESA and the Open University.

## Obu et al. (2018) permafrost map
**CC-BY 3.0** licence (stated in the PANGAEA record): the authors and the DOI must be cited. It is only used to classify cells and sites; the file is not redistributed.

## Natural Earth (place and country names)
Public domain (no attribution conditions; it is cited anyway in the app credits). The boundaries are at 1:110m scale and do not represent political positions.

## NASA imagery in the app (GIBS and Trek)
The orbital views are downloaded live from NASA's open services and shown **with each product's credit** (MODIS: NASA GIBS; Blue Marble: NASA Earth Observatory; Viking MDIM 2.1: NASA/JPL/USGS; LRO WAC: NASA/GSFC/ASU). **They are not redistributed in the repository.**

- **GIBS** (checked 15 Nov 2026): the GIBS page does not name a licence ("NASA supports full and open sharing of data") but asks that clients and presentations include an acknowledgement, which starts: *"We acknowledge the use of imagery provided by services from NASA's Global Imagery Browse Services (GIBS), part of NASA's Earth Science Data and Information System (ESDIS)."* The app's credits section carries it.
- **Trek** (checked 15 Nov 2026): no data-use or acknowledgement text was found on the Trek home page (it points to the WMTS layer documentation at trek.nasa.gov/tiles, which may hold the terms). Until a specific term is found, the app follows NASA's general media guidelines.
- **NASA media guidelines** (checked 15 Nov 2026): NASA content generally falls outside U.S. copyright and may be used for informational and educational purposes; NASA should be acknowledged as the source; the use must not imply NASA's endorsement (the app says "not endorsed by NASA").
