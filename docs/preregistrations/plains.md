# Preregistration: flat-terrain control in the USGS test (15 Nov 2026, written BEFORE measuring)

Question: does the advantage of craters over controls (Mars 0.567) survive when craters and controls **equally flat** are compared?

Method: stratify by `topo__slope_mean_deg` (mean slope of the 50 km window) into 5 quantiles computed over craters + dunes + controls together.
Within each stratum the rank AUC (crater/dune > control) is computed with the u of the current test (topography alone, mean over the body's targets).
Stratified AUC = mean of the stratum AUCs weighted by n_pos × n_ctrl; strata with fewer than 3 positives or 3 controls are omitted.
95 % CI by bootstrap within each stratum (2,000 replicates, seed 0).

**Criterion (the same as the original test):** there is signal if the lower bound of the CI > 0.5. The Moon and Mars are reported.
Neither strata nor the control variable are changed after seeing the numbers.

## Result (preregistration hash `fd6303ddeaf5ab57`)

| Body | AUC without control (original test) | AUC stratified by slope | 95 % CI | Signal? |
|---|---|---|---|---|
| Moon | 0.531 | 0.476 | 0.418-0.534 | No |
| Mars | 0.567 | 0.494 | 0.436-0.552 | **No** |

**Verdict:** when craters and equally flat controls are compared, the Mars advantage disappears (0.567 → 0.494, chance is 0.5). The Mars signal is explained by craters lying on flatter terrain than the controls, not by their crater shape. Topography is **not validated as an aspect** with this layer. This confirms the bias already pointed out in [../validation/per-aspect-validation.md](../validation/per-aspect-validation.md); the earlier Mars result must be presented as confounded by flatness.
Limit: mean slope is a single control variable; others (relief, roughness) could leave some residual confounding, but in the sense of reducing the signal further, not of creating it.
