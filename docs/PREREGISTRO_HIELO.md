# Preregistro: variable de hielo/agua de la Tierra (14 nov 2026, escrito ANTES de medir)

Variantes de `ice__water_frac` en la Tierra, sin tocar Luna ni Marte:
- **A (actual):** cobertura de nieve media anual (MODIS MOD10CM).
- **B:** humedad del suelo 0-10 cm media anual (GLDAS Noah 0.25°, 2019), `ice_soil_moisture_m3m3`.

Métrica: ablación por dimensión (`analogos.ablation`), u = P(análogo > celda típica), IC por bootstrap de análogos.
**Criterio (fijado antes de ver resultados):** se adopta B solo si, para Luna y Marte, u("todas") con B es mayor que con A
y u("solo ice") con B es > 0,5. Si no, se deja A y se reporta que B no ayudó. No se prueban más variantes después de ver los números.

## Resultado (misma sesión; hash del preregistro `805c751d6e61d88d`)

u medio (IC 95 % por bootstrap de análogos), 0,5 = azar:

| Cuerpo | Config | A nieve | B humedad del suelo |
|---|---|---|---|
| Luna | todas | 0,637 [0,555-0,682] | 0,642 [0,563-0,687] |
| Luna | solo ice | 0,684 [0,332-0,870] | 0,669 [0,354-0,985] |
| Marte | todas | 0,493 [0,305-0,679] | 0,469 [0,302-0,626] |
| Marte | solo ice | 0,623 [0,368-0,859] | 0,578 [0,230-0,864] |

**Veredicto:** el criterio exigía mejorar en Luna Y Marte; en Marte "todas" empeora (0,493 → 0,469). **Se mantiene A (nieve).**
Las diferencias son mucho menores que los IC (4-8 análogos), así que tampoco hay evidencia de que B sea peor: simplemente no ayuda.
GLDAS queda en `earth*.parquet` como columnas de diagnóstico (`ice_soil_moisture_m3m3`, `ice_swe_kg_m2`; esta última está dominada por los casquetes de hielo) y no entra al modelo.
