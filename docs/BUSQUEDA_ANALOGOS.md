# Búsqueda de análogos citados para térmica e hielo (15 nov 2026)

Objetivo: ver si hay más análogos terrestres con fuente abierta que lo sean **por térmica o por hielo**, para ampliar la validación por aspecto.
No se modificó `docs/aspectos_analogos.csv` (su huella sha256 está registrada en los resultados de `docs/VALIDACION_ASPECTO.md`).
Búsquedas hechas: análogos de regiones polares sombreadas de la Luna; análogos de hielo/permafrost de Marte; análogos del régimen térmico de Marte.

## Qué apareció
| Aspecto | Candidato | Fuente | ¿Nuevo e independiente? |
|---|---|---|---|
| Hielo (Marte) | Valles Secos de la Antártida: "mejor análogo en la Tierra del hielo subsuperficial de Marte" | [NASA NTRS 20150023012](https://ntrs.nasa.gov/citations/20150023012) | No: ya está etiquetado |
| Hielo/térmica (Marte) | Beacon Valley / University Valley | misma línea de trabajo | No: son subzonas de los Valles Secos (misma celda de 50 km) |
| Hielo (Marte) | Atacama hiperárido (sequedad parecida a la de Marte) | [Frontiers 2021](https://www.frontiersin.org/journals/astronomy-and-space-sciences/articles/10.3389/fspas.2021.797591/pdf) | No: ya está etiquetado como "general" |
| Térmica (Marte) | Atacama / Andes (cambios bruscos día-noche por atmósfera delgada) | misma fuente | Sí, pero **no evaluable**: Marte no tiene térmica |
| Térmica (Luna, polar) | Regiones polares sombreadas (<100 K) | NASA LSSW / NLSI | **No se encontró ningún análogo terrestre nombrado** |
| Hielo/térmica | Devon Island, Axel Heiberg | no confirmados en esta búsqueda | No se pueden etiquetar sin fuente |

## Conclusión
La búsqueda **no añade análogos evaluables**:
- La térmica de Marte no se puede validar porque esa dimensión está vacía por decisión.
- Para la térmica lunar (solo tiene sentido en los dos objetivos polares) las fuentes no nombran ningún sitio terrestre.
- El hielo de Marte ya tiene a los Valles Secos y Atacama, y los nuevos hallazgos caen en la misma zona.
- Una nota útil: una de las fuentes dice que ningún lugar de la Tierra reproduce los cambios de temperatura de un solo día de Marte, así que la comparación térmica tiene un límite de fondo, no solo de datos.

Sería necesario, para avanzar, leer la bibliografía completa (no solo resultados de búsqueda) y fijar de antemano qué objetivos son relevantes para cada aspecto. No se hizo: sin esa lectura, etiquetar más análogos sería ajustar la prueba a los datos.
