# App interface (AstroAtlas)

The app follows the design proposal **"AstroAtlas — Interface proposal"** (a Figma file shared by the team). **Only the way results are displayed changes: the model, the data and the validation figures do not.** Code: `app/streamlit_app.py`; texts: `src/astroatlas/i18n.py`; presentation rules: `src/astroatlas/presentation.py`; place names: `src/astroatlas/places.py`; imagery: `src/astroatlas/imagery.py`; theme: `.streamlit/config.toml`.

## What was applied from the proposal
| Proposal | In the app |
|---|---|
| 1 · Clear names | `topo`, `thermal`, `ice`, `geo` are shown as **Terrain, Temperature, Ice or water, Geology**, each with a sentence that explains it. Weights become **"Doesn't matter / Matters a little / Matters somewhat / Matters a lot"** (weights 0, 0.33, 0.66 and 1 in the model) |
| 2 · Named places | Instead of `earth_24_43` the app shows the **place and country** (e.g. "Harrat ash-Shamah, Syria / Jordan"). Names come from Natural Earth 1:110m (public domain) with two curated proper names (Harrat ash-Shamah and Haruj); no external services. Hovering over the map shows the name and the similarity |
| 3 · Three-step guide | Three cards at the top: choose a site, look at the map, read the profile |
| 4 · Explained metrics | A "These are leads, not certainties" notice with the method's hit rate (≈ 58 % on the Moon, ≈ 60 % on Mars; 50 % = guessing) and a "How reliable is it for …?" panel with a confidence label. AUC and recall stay in "Technical details and validation" |
| 5 · Missing data | If an aspect has no data (e.g. Mars temperature) the card says "No data / Could not compare" and explains why; the profile says "Computed with N of 4 aspects" |
| 6 · Similarity as a percentage | The 0-to-1 score is shown as a percentage (0.82 → 82 %), with the label "Very similar / Moderate match / Low match" per aspect |

Also: the "Most similar places" table (with the rank in the full list), the profile with one text per aspect, and "What Earth cannot imitate" as labels. The expanders for candidates, aspect atlas, use cases (including the cold case with the permafrost map) and credits follow below.

## Where the reliability figures come from
They are constants in `presentation.py` (`RELIABILITY`) taken from the validation with the three analog sets together ([preregistrations/validation-set-3.md](../preregistrations/validation-set-3.md), descriptive): **Moon 58 % (55 % to 62 %; 20 analogs) and Mars 60 % (52 % to 67 %; 40 analogs)**. If the validation changes they have to be updated by hand; a test checks that they are consistent (value inside its interval and above 50 %).

## Differences from the mock-up
- Per-aspect explanations come from each cell's data (e.g. "somewhat flatter than Jezero" or "rougher" depending on slope), so they can differ from the mock-up's example sentences.
- Place names are those of Natural Earth at 1:110m scale, coarser than the mock-up's: many Sahara cells appear as "Sahara (Sudan)" instead of "Red Sea coast" or "Eastern Desert"; cells in areas without a named region appear as "Area of <country>". Adding finer proper names is a small change (`CURATED_NAMES`).
- **Colours:** sampled from the mock-up and set in `.streamlit/config.toml`: background `#0E1117`, sidebar `#161A23`, surfaces `#1B2030`, border `#242A3B`, orange accent `#FF8C42`, amber `#FBBF24` (moderate match, low confidence), green `#34D399` (very similar) and blue `#4C8DF6` (known analogs and limits). Streamlit's native dark theme is used, with no custom CSS.
- **What Streamlit does not allow without CSS:** the mock-up's cards have a `#1B2030` fill, here they are just a bordered box; progress bars are all the accent colour instead of amber or green depending on level; and the sidebar controls are orange to match the accent.
- The "Only new places" filter and the town and vegetation filters are kept; "Places to show" became "Advanced options".

## Usability and accessibility (15 Nov 2026)
The app was evaluated in production (accessible structure, contrast, keyboard, 375 px mobile and usage flow) with automatic checks in the browser; **it was not tested with a real screen reader or with users**. Adjustments applied:

| Adjustment | Result |
|---|---|
| Page language | Streamlit marks `lang="en"`; a minimal `st.html` script sets it to the chosen language. Without JavaScript the app works the same, but with the wrong voice |
| Headings | Only `H1` (AstroAtlas) and `H2` (map section and place name). The profile numbers are no longer headings (`st.metric`) and the sidebar uses no headings |
| Icons as text | Steps are numbered "1 · 2 · 3" in text (it used to be read as "counter_1") |
| Site selector | It is in the page, not in the sidebar (on mobile the sidebar starts closed); a text says where to adjust aspects and filters |
| Borders | `borderColor #667085` and `showWidgetBorder` so fields and boxes can be told apart (≥ 3:1 against the background). The look differs from the mock-up |
| Choosing a place | Besides the "See the profile of" dropdown, you can **pick a row of "Most similar places"** (verified in the browser) or **click an orange point on the map** (logic covered by automatic tests; **the real click on the map could not be verified in the test browser**, where not even hovering showed the name: worth testing by hand) |
| Help hidden in "?" | The filter criteria and reliability figures are visible text, with no help icons |
| Importance control | "None / Little / Some / A lot" buttons (`st.segmented_control`) instead of four sliders |
| Loading | Slow steps show a message ("Loading the Earth, Moon and Mars data…") |
| Mouse wheel over the map | No wheel zoom (there are + and − buttons), so the wheel keeps scrolling the page |
| Expander titles | No file paths in the title; the `docs/...` reference goes inside |

**Low priority (applied):**
- **Map legend by shape and not only colour:** candidates are filled orange dots, known analogs are blue rings and the chosen place is a large white ring. The legend says so in words.
- **Glossary** ("What do these words mean?", an expander under the notice): analog, candidate, similarity, aspect, confidence and chance.
- **Shorter profile on mobile:** the four aspect cards go in a grid (`st.grid`, minimum width 125 px): 4 in a row on desktop and 2 per row on mobile. "No data" was cut off when narrow, so that card uses normal text and the label "Not compared".

**Remaining limits:** Streamlit's controls (13 px checkboxes, 16–28 px buttons) are smaller than 44 px and cannot be controlled without CSS; Streamlit's own texts ("Show/hide columns", "Download as CSV", "Main menu", "Skip to main content") stay in English and cannot be translated by configuration; the real click on the map could not be verified in the test browser.

## Languages: English and Spanish (15 Nov 2026)
The app is available in **English and Spanish**. The selector is **at the very top of the sidebar** ("Idioma / Language"). You can open it directly in a language with the address: `…/?lang=en` or `…/?lang=es` (the address updates when the selector changes, so it can be shared). English is the default.

- **Texts:** all in `src/astroatlas/i18n.py` (a dictionary with both versions of every text). The English follows the "Main screen (EN)" version of the Figma mock-up. A test checks that every text exists in both languages and carries the same `{…}` fields.
- **Logic:** `src/astroatlas/presentation.py` receives the language in every function (per-aspect sentences, match levels, glossary, site descriptions, coordinates with W/O).
- **Place and country names:** `places.py` stores Natural Earth's names in Spanish (`NAME_ES`) and English (`NAME_EN`), e.g. "Meseta Tibetana, China" / "Tibetan Plateau, China".
- **What changes with the language:** the interface, messages, place and country names, the glossary, the atlas texts and the use cases (titles and explanations from the results file are translated by exact text) and the page's `lang` attribute, set to `es` or `en` for screen readers.
- **What does not change:** the model, the data and the figures. The **documents** (`docs/*.md`) are English only. Proper names of analogs and sites (Atacama, Dry Valleys…) and technical codes in the tables (`cell_id`, `rank`…) are not translated.
- **Note:** results-file text without an exact translation is shown in Spanish (all are translated today: 8 atlas explanations and 7 use cases; a test checks it, so a new untranslated text makes the tests fail). Streamlit's own texts stay in English in both versions.

**Footer:** at the end of the page (also when the page stops for lack of aspects or places) there is one line with the authorship in the chosen language: "Developed by the AstroAtlas team for the NASA Space Apps Challenge 2026 Hackathon." / its Spanish version (key `pie` in `i18n.py`).

## Visual comparison with NASA imagery (15 Nov 2026)
In each place's profile, under the name, there is a **visual comparison**: on the left the chosen Moon or Mars site and on the right the Earth place, as **150 × 150 km orbital views** centred on each (same size in kilometres, so the shape of the terrain can be compared at a glance). Each image carries its credit and the title says which are compared.

| Body | Source (open NASA service, no key) | Resolution |
|---|---|---|
| Earth | **NASA GIBS**: MODIS Terra true colour (a day in 2023) or Blue Marble Next Generation (cloud-free); chosen with the "Earth image" control | 250 m and 500 m per pixel |
| Mars | **NASA Trek**: Viking MDIM 2.1 colour mosaic | 232 m per pixel |
| Moon | **NASA Trek**: LRO WAC mosaic | ≈ 100 m per pixel |

- **How it works** (`src/astroatlas/imagery.py`): for Earth, GIBS is asked for an image of the window (WMS); for the Moon and Mars the Trek tiles that cover the window are downloaded (in parallel, ~1.5 s), stitched and a 512 px square is cropped. The window widens with latitude so that it is square in kilometres. Images are kept in the app cache for a week.
- **If NASA fails:** the app shows "Could not load the NASA image right now" instead of the image and everything else keeps working (checked with the NASA network cut); exceptions are not cached, so it retries.
- **Limits:** beyond **84° latitude** (the poles: Shackleton and Malapert on the Moon) the Trek map distorts too much and the view of that site is not shown (the Earth place's view is); the colour and sensor of each body differ (Mars and the Moon in orbiter mosaics, Earth in true colour), so they are for comparing shapes (craters, lava fields, valleys), not colours; the MODIS image is a single day and can have clouds (hence the blurrier Blue Marble option); Earth's 250–500 m per pixel is coarser than what NASA's rover photos show.
- **It is not a ground-level photo:** for that NASA has the Image and Video Library (`images.nasa.gov`, with an open API), which could be used to add a hand-picked photo per site (left as an improvement).

## Sensitivity, field-site risks and PDF report (15 Nov 2026)
Three additions that turn the profile from a display into decision support. None of them changes the model or the score.

- **Rank sensitivity** (`src/astroatlas/sensitivity.py`, expander "How robust is this place's rank?"): the ranking is recomputed with the current weights and, one at a time, with each aspect switched off. A bar chart and a table give the place's rank (among the places visible after the town and vegetation filters) and the top place in every scenario, with a plain-language reading: *robust* if the rank hardly moves, *sensitive* if one aspect carries the match (for example Harrat ash-Shamah is #1 overall but drops to #22 without geology).
- **Field-site risk indicators** (`src/astroatlas/risks.py`, section "Field-site risks (indicative)" in the profile and a "Color the map by: Field risk" option): eight rules of thumb computed from data the project already holds: 90th-percentile slope, hottest monthly daytime temperature, coldest monthly night temperature, surface dust, wind, perennial snow, altitude and distance to the nearest town. Each is low, medium or high with its value shown as text; the overall level is *high* if the mean level is ≥ 1 or two indicators are high, and *medium* if the mean is ≥ 0.5 or any one is high. The profile also reports the 90th-percentile slope of the Moon or Mars target itself. **Limits:** thresholds are indicative and not mission-certified; values are monthly means or grid-cell statistics, not extremes; **radiation and security/access are not assessed** (the app says so) because this project has no data for them.
- **PDF site report** (`src/astroatlas/report_pdf.py`, button "Download site report (PDF)"): a two-page document with the match per aspect, the method's reliability and interval, the sensitivity table, the risk indicators, where the analogy breaks down, both orbital views with credits and the "hypothesis, not recommendation" notice. It is generated only when the button is clicked, in the interface language, with the core PDF fonts (text is sanitised to Latin-1).

## Featured case and filters by region and terrain (15 Nov 2026)
- **Featured mission case** (card under the three steps): *rehearse Mars lava-field operations*. It shows the top two cells of the "Basaltic terrain (Mars)" use case from `usecases.csv` (Harrat ash-Shamah 78 % and Haruj 69 % average match with 9 Mars sites), what makes each interesting (planetary-pit analog and 8 documented lava tubes; no analog study of its own found), their overall field-risk level, and an **Explore this case** button. The button selects Jezero, turns on *Volcanic terrain only* and opens the first candidate's profile. A note reminds that the model sees terrain and geology, not caves. It was chosen because it is the best-supported use of the method in the results ([use cases](../results/use-cases.md)).
- **Regions to show** (sidebar, `src/astroatlas/regions.py`): a multi-select of Africa, Europe, Asia and Middle East, North America, South America, Oceania, polar regions (beyond 60°) and other islands. The boxes are deliberately coarse and approximate: they narrow the list and the map, they are not a geography product. It affects only what is shown, like the town and vegetation filters; the score does not change.
- **Volcanic terrain only** (sidebar): keeps places where half or more of the window's rock is basalt (GLiM `geo__basalt_frac` ≥ 0.5; 19 of 951 cells), a quick way to work at the scale of a volcanic field.
- Both filters also drive the rank sensitivity chart (it ranks among the places that remain visible). Tests: `tests/test_sensitivity_risks_pdf.py`; the filters and the button were also exercised end to end with Streamlit's `AppTest`.
