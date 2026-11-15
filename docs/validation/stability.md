# Stability of the predictions (15 Nov 2026)

**Question:** do the candidate cells depend on arbitrary model decisions? Code: `src/astroatlas/stability.py` (`python -m astroatlas.stability`).
**Method:** 150 replicates per body. In each one the following are perturbed: (1) the weights per dimension (uniform Dirichlet), (2) the Earth sample used to standardise and fit the topography PCA (cell bootstrap) and (3) the variance explained by the PCA (80 to 95 %). The mean score of each cell over all the body's targets is computed and it is recorded whether it stays in the best 5 % of the 384 viable, non-vegetated cells. `freq_top5` is the fraction of replicates in which that happens.
It does not use the known analogs and **does not measure whether the prediction is correct**, only whether it is robust to decisions with no data behind them.

## Results
| Body | Cell | Place | `freq_top5` | Mean rank (0 = best) |
|---|---|---|---|---|
| Mars | 32.5° N, 37.5° E | Harrat ash-Shamah | **1.00** | 0.00 |
| Mars | 27.5° N, 17.5° E | Haruj | **0.79** | 0.04 |
| Mars | 17.5° N, 27.5° E | Eastern Sahara | 0.65 | 0.10 |
| Mars | 17.5° N, 32.5° E and 27.5° N, 22.5° E | Sahara | 0.59 and 0.55 | 0.11 |
| Moon | −77.5° to −82.5° (several cells) | Antarctica | 0.82 to 0.86 | 0.03 to 0.06 |
| Moon | 32.5° N, 37.5° E (Harrat) | | 0.23 | 0.11 |
| Moon | 27.5° N, 17.5° E (Haruj) | | 0.04 | 0.20 |

## How to read it
- **The two Mars candidates are robust:** Harrat ash-Shamah stays among the best 5 % in **all** replicates and Haruj in 79 %. They do not depend on a particular weight or PCA. It is a reason to rank them above others, although it does not prove they are good analogs.
- **Robustness is not validity.** The Antarctic cells for the Moon come out just as robust (0.82 to 0.86) and we already know they are an artefact: they only have topography data and are flat. A prediction can be stable and wrong.
- **For the Moon there are no solid Earth candidates:** the Harrat and Haruj cells appear rarely (0.23 and 0.04), so the Mars result does not transfer.
- **What was not perturbed:** the variables themselves, the 50 km window, the data sources and the targets. High stability against what was perturbed does not cover those decisions.
