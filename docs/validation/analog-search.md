# Search for cited analogs for thermal and ice (15 Nov 2026)

Goal: see whether there are more terrestrial analogs with an open source that are analogs **for thermal or ice**, to extend the per-aspect validation.
`docs/catalog/analog_aspects.csv` was not modified (its sha256 fingerprint is recorded in the results of [per-aspect-validation.md](per-aspect-validation.md)).
Searches made: analogs of the Moon's shadowed polar regions; ice/permafrost analogs of Mars; analogs of Mars' thermal regime.

## What turned up
| Aspect | Candidate | Source | New and independent? |
|---|---|---|---|
| Ice (Mars) | Antarctic Dry Valleys: "best Earth analog of Mars subsurface ice" | [NASA NTRS 20150023012](https://ntrs.nasa.gov/citations/20150023012) | No: already labelled |
| Ice/thermal (Mars) | Beacon Valley / University Valley | same line of work | No: sub-areas of the Dry Valleys (same 50 km cell) |
| Ice (Mars) | Hyper-arid Atacama (dryness similar to Mars) | [Frontiers 2021](https://www.frontiersin.org/journals/astronomy-and-space-sciences/articles/10.3389/fspas.2021.797591/pdf) | No: already labelled as "general" |
| Thermal (Mars) | Atacama / Andes (sharp day-night swings from the thin atmosphere) | same source | Yes, but **not evaluable**: Mars has no thermal data |
| Thermal (Moon, polar) | Shadowed polar regions (<100 K) | NASA LSSW / NLSI | **No named terrestrial analog found** |
| Ice/thermal | Devon Island, Axel Heiberg | not confirmed in this search | Cannot be labelled without a source |

## Conclusion
The search **adds no evaluable analogs**:
- Mars thermal cannot be validated because that dimension is empty by decision.
- For lunar thermal (only meaningful for the two polar targets) the sources name no terrestrial site.
- Mars ice already has the Dry Valleys and Atacama, and the new findings fall in the same area.
- A useful note: one source says no place on Earth reproduces the temperature swings of a single Martian day, so the thermal comparison has a fundamental limit, not only a data one.

To go further it would be necessary to read the full literature (not only search results) and fix beforehand which targets are relevant for each aspect. That was not done: without that reading, labelling more analogs would be fitting the test to the data.
