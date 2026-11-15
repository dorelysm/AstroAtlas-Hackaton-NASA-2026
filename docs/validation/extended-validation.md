# Validation with the extended set of analogs (15 Nov 2026)

Protocol and list frozen **before** computing anything: [../preregistrations/analog-validation.md](../preregistrations/analog-validation.md) (protocol hash recorded when the list was frozen; lists `catalog/extended_analogs.csv` `0f234908cd16ce94` and `catalog/extended_analog_aspects.csv` `3cc33c3ddf4c8a6f`). Frozen model (commit `0b8a0a2`): nothing was tuned after seeing these numbers.
Code: `src/astroatlas/validation_ext.py` (`python -m astroatlas.validation_ext --build`, then without `--build`). **23 analogs** = 10 original + 13 new (Moon: 12 with some applicable aspect; Mars: 20).

## Result according to the fixed criterion
Criterion: the lower bound of the 95 % CI of the mean u ("all dimensions") must be > 0.5 in every body with ≥ 8 analogs. u = P(analog > typical cell), 0.5 = chance; bootstrap over the analogs.

| Body | Group | Analogs | Mean u | 95 % CI | Met? |
|---|---|---|---|---|---|
| **Moon** | all | 12 | **0.595** | 0.545 to 0.644 | **Yes** (narrowly) |
| Moon | original / new | 4 / 8 | 0.637 / 0.575 | 0.558 to 0.682 / 0.509 to 0.635 | (new: yes; original: n < 8) |
| **Mars** | all | 20 | **0.564** | 0.448 to 0.678 | **No** (the lower bound is below 0.5) |
| Mars | original / new | 8 / 12 | 0.493 / 0.612 | 0.301 to 0.674 / 0.468 to 0.737 | No / No |

**Honest reading:** on the Moon the model beats chance by a small margin; on Mars the mean is somewhat above 0.5 but the interval includes chance, **so it cannot be claimed to work**. It is the first time a body passes the criterion, and it should not be oversold: the margin is about 0.05, the lunar analogs that count are 12 (several impact craters that serve both the Moon and Mars), and the coordinates of the new ones are not verified.

## Which analogs the model recovers and which it does not (Mars, mean u over the 14 targets)
- **High (≥ 0.65):** Lanzarote 0.96, Rochechouart 0.87, Vredefort 0.84, Pinacate 0.79, Ries 0.75, Lava Beds 0.75, Salar Grande 0.74, Danakil 0.73, Meteor Crater 0.69, Río Tinto 0.68, Atacama 0.65.
- **Near zero:** Dry Valleys 0.04, **Axel Heiberg 0.10**, Svalbard 0.18, Salar de Uyuni 0.25 (see note), Eureka 0.38.

**The pattern is clear:** the model recognises **arid, volcanic or impact** analogs and **fails on cold and ice** ones (Dry Valleys, Axel Heiberg, Svalbard, Eureka). It is the already-known problem of the ice (snow) variable, now confirmed with a larger sample of permafrost sites. Note: Uyuni comes out with mean "snow" 1.00 because the MODIS product confuses bright salt with snow, a source failure.

## By aspect (source + note; n_on = analogs with the aspect)
| Body | Aspect | n_on / n_off | Difference | 95 % CI | p (permutation) |
|---|---|---|---|---|---|
| Moon | Geology | 5 / 6 | **+0.41** | 0.06 to 0.69 | **0.05** |
| Mars | Geology | 2 / 11 | **+0.86** | 0.66 to 0.97 | 0.04 |
| Mars | Topography | 8 / 6 | +0.12 | −0.05 to 0.30 | 0.11 |
| Moon | Topography | 6 / 5 | +0.03 | −0.13 to 0.18 | 0.37 |
| Mars | **Ice** | 3 / 11 | **−0.51** | −0.75 to −0.30 | 1.00 |
| Moon | Thermal | 1 / 10 | −0.51 | −0.59 to −0.42 | 1.00 |

- **Geology:** the only one with signal in the right direction, in both bodies. Mars rests on just **2 analogs** (Craters of the Moon and Pinacate), below the protocol's minimum of 3, so it **does not count as evidence**. The lunar one has 5 and p = 0.05 (borderline).
- **Topography:** a small difference in favour on Mars, not significant. Remember that 5 of the 13 new sites are impact craters and that we already saw the topographic signal is explained by flat terrain ([../preregistrations/plains.md](../preregistrations/plains.md)).
- **Mars ice:** fails consistently (−0.51 with 3 sites; earlier −0.75 with 1). It is the aspect to fix.

## Limits
- The list did not reach 30 sites and is biased towards impact craters (5 of 13).
- The coordinates of the 13 new ones come from general knowledge and still have to be verified.
- Thermal of the new sites: MODIS monthly means of 2019, with the limitations already described. Geology: the 0.5° GLiM gives 0.14 for Pinacate (a small field) and 0 for Etna, so it **underestimates** basalt in small fields.
- No flat-terrain correction nor population or vegetation flags were applied: it is the same measurement as for the originals.
- With 23 analogs the intervals are still wide; a second independent set would give more power.

## What it suggests for improving the model
1. **Ice/cold is what prevents recovering a third of the Mars analogs** (**correction:** not because of the snow variable but because the polar Mars targets have no ice data; see [../preregistrations/models.md](../preregistrations/models.md)). Any improvement must tackle that: a comparable physical variable (thermal inertia or emissivity) and filling Mars thermal, which is the dimension that tells cold analogs from warm ones.
2. Improvements will be tested against **this same frozen set**, without touching it, and reported separately.
