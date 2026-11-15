# Preregistration: third set of analogs, taken from an expert catalogue (15 Nov 2026, written BEFORE computing any feature or score)

**Why:** the two earlier sets were assembled by me (the first with 8 fixed searches, the second with another 8). A catalogue made by experts and published years ago reduces the risk that my selection favours the model, and gives more analogs for the Moon. **Source:** *The Catalogue of Planetary Analogues* (CAFE TN2, Preston, Grady and Barber, Open University, for ESA, 5 Dec 2012; [PDF](https://freight.cargo.site/m/D1821053255089660420449933921929/The-Catalogue-of-Planetary-Analogues.pdf)). **Model A:** the frozen one (commit `0b8a0a2`); nothing is changed. **Earlier sets:** the 23 of [analog-validation.md](analog-validation.md) and the 9 of [validation-set-2.md](validation-set-2.md).

## Selection rule (mechanical; applied to the 30 entries of the catalogue)
1. **Unit:** each "site" of the catalogue with a **point coordinate given in the catalogue itself** (at chapter level, or in a "Site Specific Details" entry with explicit coordinates). Regional entries without a point (Atacama "20-30° S", Namib, Kamchatka "51-61° N", Columbia River "Various", Central Australia) and entries without coordinates are excluded.
2. **Body (`analog_of`):** that of the catalogue's "Directory" table (which lunar and Martian features each chapter covers; the "Astrobiology" row does not count). Moon: chapters 1-4, 6-8, 10, 12-18, 22, 24-27; Mars: all except 17 (and 29, 30 do).
3. **Independence:** any site **within 100 km** of any of the 32 earlier analogs or of another already accepted site of this set is excluded (in a tie, the lower chapter number wins). By this rule the following are left out, among others: Etna, Tenerife, Utah/MDRS, Namib, Pilbara, Atacama/Yungay, Dry Valleys (and Blood Falls, Wright Valley, Beacon Valley), Ries, Sudbury, Rio Tinto, Meteor Crater, Cinder Lake, Black Point, Sunset Crater, Haughton and its "supersites", Kilauea, Askja and central Svalbard.
4. **No aspect labels** (the catalogue does not give them by a measurable criterion): only the global validation is evaluated.
5. **Frozen list** (13 sites; no pair within 100 km): `docs/catalog/analogs_set3.csv`, sha256 `2f3d816540d1cbf5`. **Moon: 7** (Lonar, Mistastin, Pampas de La Joya, Eyjafjallajökull, Krýsuvík, Bockfjord, Murchison Fjord). **Mars: 12** (all except Mistastin). Minimum distance to an earlier analog: 153 km (Bockfjord-Svalbard). The nearest pairs among the new ones are 113 and 124 km apart.

## Evaluation (fixed)
Same 50 km windows, dimensions and metrics as [validation-set-2.md](validation-set-2.md).
- **V1, base model A:** mean u over the body's targets, 95 % bootstrap CI over the analogs. **Mars:** the 12 new ones; criterion: lower bound > 0.5. **Moon:** the 7 new ones **plus the lunar analog of the second set (Teide)**, 8 in total, all after the first set's freeze; criterion: lower bound > 0.5. (The Moon with only the 7 new ones is also reported, without a verdict because it has fewer than 8.)
- **V2, "A or B" union:** as in the second set, with **the 32 earlier analogs as the only references** of model B. Criterion: lower bound of u > 0.5 **and** paired difference with `P_A` with a lower bound > 0 in at least one body and no upper bound < 0. Mars with the 12 new ones; Moon with the 7 (no verdict if < 8).
- **Descriptive:** u per analog; the total set of 45 analogs; the cold sites (rule of [cold-warm-groups.md](cold-warm-groups.md)).

## What is not done
The model, weights, list or criteria are not changed after seeing the results; any variant is reported separately as exploratory.

## Limits known beforehand
Coordinates taken from the catalogue without verification in a primary source (possible typos, such as a space in the seconds of Bockfjord); the catalogue is from 2012 and is biased towards sites with logistics and publications; the Moon depends on combining two sets; the Svalbard and Iceland entries are several sites of one region (113-124 km apart), with possible correlation; 0.5° GLiM and monthly MODIS 2019 as before.

## Results (protocol hash `897392c2135d60fd`; list `2f3d816540d1cbf5`; no changes to the protocol after seeing the numbers)
Code: `src/astroatlas/validation3.py` (`python -m astroatlas.validation3 --build`, then without `--build`).

| Test | Body | Analogs | Result | Met? |
|---|---|---|---|---|
| **V1 base model A** | **Mars** (new set only) | 12 | **u = 0.577 (CI 0.423 to 0.726)** | **No** (lower bound < 0.5) |
| **V1 base model A** | **Moon** (7 new + Teide, preregistered) | 8 | **u = 0.565 (CI 0.515 to 0.611)** | **Yes** (narrowly) |
| V1 | Moon (7 new only) | 7 | 0.570 (0.510 to 0.622) | No verdict (< 8) |
| V2 "A or B" union | Mars | 12 | u = 0.581 (0.428 to 0.725); difference with `P_A` +0.011 (−0.071 to +0.105) | **No** |
| V2 "A or B" union | Moon | 7 | u = 0.560 (0.413 to 0.710); difference with `P_A` **−0.123 (−0.157 to −0.086)** | No verdict, and the union **worsens** A |

**Preregistered verdicts:** **the A-or-B union is not adopted** (again: +0.011 on Mars and significantly worse on the Moon). **The base model is NOT confirmed on Mars with this set** (lower bound 0.423) and **is on the Moon by a small margin** (lower bound 0.515).

### Descriptive (not preregistered as a test; mixes sets)
- **Mars, the three sets together (40 analogs):** u = **0.595 (CI 0.515 to 0.670)**; only the second set met the criterion on its own (0.698), the first (0.564) and third (0.577) did not. The three averages are above 0.5 but two of the three intervals include chance.
- **Moon, the three sets together (20 analogs):** u = **0.583 (CI 0.545 to 0.619)**: it beats chance narrowly, consistent with the first set (0.595).
- **Per analog (Mars):** high Lonar 0.95, Krýsuvík 0.95, Turpan 0.85, Eyjafjallajökull 0.80, Ibn Battuta 0.65, Pampas de La Joya 0.63, Barberton 0.59; **low the cold and lake ones**: Bockfjord 0.11, Pavilion Lake 0.30, Murchison Fjord 0.31, Yellowstone 0.35, Golden Deposit 0.46. It is the usual pattern: it recognises the arid, volcanic and impact ones and fails on the cold, hydrothermal and lake ones.

### Honest reading
- **The strictest independent result (expert catalogue, 12 analogs) does not pass:** the base model stays above chance on average (0.577) but the interval includes it. It is the second time a Mars set does not pass (the first one did) and the first time one assembled by others does not either; the confirmation of the second set (0.698) may be partly due to my 8 queries favouring deserts and dunes.
- **The most reasonable estimate with all the data is modest:** u ≈ 0.6 on Mars (0.515 to 0.670) and ≈ 0.58 on the Moon (0.545 to 0.619): the method discriminates somewhat better than chance, not by much.
- **Warning:** in the ESA set, several sites (Iceland, Svalbard) are from the same regional setting (113 to 124 km), so they are not entirely independent.
- **Moon:** the union worsens consistently (−0.12): B (Earth-to-Earth analogs) is almost useless for the Moon with 13 references.
