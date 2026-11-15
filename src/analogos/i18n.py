"""Textos de la app en español (es) e inglés (en). El inglés sigue la versión «Main screen (EN)» de la propuesta de interfaz de Figma.

`t(lang, clave, **valores)` devuelve el texto en el idioma pedido (por defecto español si falta). Las claves que acaban en `_lista`
son listas de textos. Solo textos de la interfaz: el modelo, los datos y las cifras no dependen del idioma.
"""

IDIOMAS = {"es": "Español", "en": "English"}

TEXTOS: dict[str, dict] = {
    # ---- general ----
    "subtitulo": {"es": "Lugares de la Tierra que se parecen a la Luna y a Marte", "en": "Places on Earth that resemble the Moon and Mars"},
    "idioma_label": {"es": "Idioma / Language", "en": "Idioma / Language"},
    "idioma_ayuda": {"es": "Elige Español o English arriba en el menú de la izquierda (en el móvil, ábrelo con el icono »).",
                     "en": "Choose Español or English at the top of the left menu (on a phone, open it with the » icon)."},
    "cargando": {"es": "Cargando los datos de la Tierra, la Luna y Marte… / Loading the Earth, Moon and Mars data…",
                 "en": "Cargando los datos de la Tierra, la Luna y Marte… / Loading the Earth, Moon and Mars data…"},
    "cargando_modelo": {"es": "Preparando el modelo de relieve… / Preparing the terrain model…",
                        "en": "Preparando el modelo de relieve… / Preparing the terrain model…"},
    "cuerpo_moon": {"es": "Luna", "en": "Moon"},
    "cuerpo_mars": {"es": "Marte", "en": "Mars"},
    "cuerpo_de_moon": {"es": "la Luna", "en": "the Moon"},
    "cuerpo_de_mars": {"es": "Marte", "en": "Mars"},
    # ---- pasos ----
    "paso1": {"es": "Elige un sitio", "en": "Choose a site"},
    "paso1_texto": {"es": "Un lugar de la Luna o de Marte, justo aquí debajo.", "en": "A place on the Moon or Mars, right below."},
    "paso2": {"es": "Mira el mapa", "en": "Look at the map"},
    "paso2_texto": {"es": "Los puntos naranjas son los lugares de la Tierra que más se le parecen.",
                    "en": "Orange dots are the places on Earth that resemble it most."},
    "paso3": {"es": "Lee la ficha", "en": "Read the fact sheet"},
    "paso3_texto": {"es": "Te dice en qué se parece, en qué no y qué datos faltan.",
                    "en": "It tells you what matches, what does not, and which data is missing."},
    "sitio_titulo": {"es": "1 · Elige un sitio de la Luna o de Marte", "en": "1 · Choose a site on the Moon or Mars"},
    "sitio_label": {"es": "Sitio de la Luna o de Marte", "en": "Site on the Moon or Mars"},
    "ajusta_hint": {"es": ":material/tune: ¿Qué te importa más? Ajusta los aspectos y los filtros en la barra lateral "
                          "(en el móvil, ábrela con el icono » de arriba a la izquierda).",
                    "en": ":material/tune: What matters most to you? Adjust the aspects and filters in the left sidebar "
                          "(on a phone, open it with the » icon at the top left)."},
    # ---- barra lateral ----
    "importa_titulo": {"es": "2 · ¿Qué te importa más?", "en": "2 · What matters most to you?"},
    "imp_label": {"es": "{nombre}: ¿cuánto importa?", "en": "{nombre}: how much does it matter?"},
    "imp_none": {"es": "Nada", "en": "None"},
    "imp_low": {"es": "Poco", "en": "Little"},
    "imp_some": {"es": "Algo", "en": "Some"},
    "imp_high": {"es": "Mucho", "en": "A lot"},
    "aspecto_topo": {"es": "Relieve", "en": "Terrain"},
    "aspecto_thermal": {"es": "Temperatura", "en": "Temperature"},
    "aspecto_ice": {"es": "Hielo o agua", "en": "Ice or water"},
    "aspecto_geo": {"es": "Geología", "en": "Geology"},
    "ayuda_topo": {"es": "Qué tan plano o montañoso es", "en": "How flat or rugged it is"},
    "ayuda_thermal": {"es": "Calor de día y frío de noche", "en": "Daytime heat and nighttime cold"},
    "ayuda_ice": {"es": "Si hay hielo o agua en el suelo", "en": "Whether there is ice or water in the ground"},
    "ayuda_geo": {"es": "Si es roca volcánica (basalto)", "en": "Whether it is volcanic rock (basalt)"},
    "filtros": {"es": "Filtros", "en": "Filters"},
    "f_nuevos": {"es": "Solo lugares nuevos (lejos de los ya conocidos)", "en": "Only new places (far from known analogs)"},
    "f_nuevos_ayuda": {"es": "Quita los lugares a menos de 500 km de un análogo conocido.",
                       "en": "Removes places within 500 km of a known analog."},
    "f_pueblos": {"es": "Ocultar lugares con pueblos cerca", "en": "Hide places near towns"},
    "f_pueblos_ayuda": {"es": "Pueblos de 1 000 habitantes o más a menos de 50 km (NASA SEDAC GRUMP). No cambia la nota; la lista es "
                              "incompleta para pueblos pequeños (docs/FUENTES.md).",
                        "en": "Towns of 1,000 inhabitants or more within 50 km (NASA SEDAC GRUMP). It does not change the score; the "
                              "list is incomplete for small towns (docs/FUENTES.md, in Spanish)."},
    "sin_poblacion": {"es": "Sin datos de población: ejecuta `python -m analogos.data.settlements`.",
                      "en": "No population data: run `python -m analogos.data.settlements`."},
    "f_veg": {"es": "Ocultar lugares con vegetación", "en": "Hide places with vegetation"},
    "f_veg_ayuda": {"es": "Vegetación según NASA MODIS (NDVI máximo de 0.2 o más). El modelo no tiene dimensión de biología: sin este "
                          "filtro salen selvas como «parecidas a Marte». No cambia la nota.",
                    "en": "Vegetation according to NASA MODIS (maximum NDVI of 0.2 or more). The model has no biology dimension: "
                          "without this filter, jungles show up as “similar to Mars”. It does not change the score."},
    "avanzadas": {"es": "Opciones avanzadas", "en": "Advanced options"},
    "mostrar": {"es": "Lugares a mostrar", "en": "Places to show"},
    "sin_pesos": {"es": "Pon al menos un aspecto en «Poco» o más para poder comparar.",
                  "en": "Set at least one aspect to “Little” or more so there is something to compare."},
    "sin_lugares": {"es": "Con estos filtros no queda ningún lugar. Quita alguno en la barra lateral.",
                    "en": "No places are left with these filters. Remove one in the sidebar."},
    # ---- aviso, glosario ----
    "aviso_titulo": {"es": "Son pistas, no certezas", "en": "These are leads, not certainties"},
    "aviso": {"es": "El método acierta ≈ {luna} % en la Luna y ≈ {marte} % en Marte. Como referencia: 50 % sería adivinar. Úsalo para "
                    "encontrar lugares que valga la pena revisar con expertos.",
              "en": "The method is right about {luna}% of the time for the Moon and {marte}% for Mars. For reference, 50% would be "
                    "guessing. Use it to find places worth reviewing with experts."},
    "glosario_titulo": {"es": "¿Qué significan estas palabras?", "en": "What do these words mean?"},
    # ---- mapa ----
    "mapa_titulo": {"es": "Lugares parecidos a {sitio} ({cuerpo})", "en": "Places similar to {sitio} ({cuerpo})"},
    "mapa_alt": {"es": "Mapa del mundo con los lugares más parecidos a {sitio}. Haz clic en un punto naranja para ver su ficha.",
                 "en": "World map with the places most similar to {sitio}. Click an orange dot to see its fact sheet."},
    "leyenda_lista": {"es": [":orange[●] **Punto naranja lleno:** lugares parecidos (candidatos); haz clic en uno para ver su ficha.",
                             ":blue[○] **Anillo azul:** lugares que la ciencia ya usa (para comprobar).",
                             "○ **Anillo blanco grande:** el lugar elegido."],
                      "en": [":orange[●] **Filled orange dot:** similar places (candidates); click one to see its fact sheet.",
                             ":blue[○] **Blue ring:** places that science already uses (for validation).",
                             "○ **Large white ring:** the chosen place."]},
    "tooltip_conocido": {"es": "Análogo que la ciencia ya usa (para comprobar)", "en": "Analog that science already uses (for validation)"},
    "tooltip_detalle": {"es": "{pais} · parecido {n} %", "en": "{pais} · {n}% match"},
    # ---- confiabilidad y tabla ----
    "conf_titulo": {"es": "¿Qué tan confiable es para {cuerpo}?", "en": "How reliable is it for {cuerpo}?"},
    "conf_nivel": {"es": "Confianza baja", "en": "Low confidence"},
    "conf_metrica": {"es": "de acierto (50 % = adivinar)", "en": "accuracy (50% = guessing)"},
    "conf_rango": {"es": "Entre {lo} % y {hi} % con {n} lugares de comprobación.", "en": "Between {lo}% and {hi}% with {n} validation places."},
    "conf_moon": {"es": "Supera el azar por poco. Reconoce los lugares volcánicos y de impacto; falla con los fríos.",
                  "en": "It beats chance by a small margin. It recognizes volcanic and impact places; it fails with cold ones."},
    "conf_mars": {"es": "Reconoce bien los lugares secos y volcánicos. Falla con los lugares fríos y con hielo.",
                  "en": "It recognizes dry, volcanic places well. It fails with cold, icy places."},
    "top_titulo": {"es": "Los más parecidos", "en": "Closest matches"},
    "col_lugar": {"es": "Lugar", "en": "Place"},
    "col_pais": {"es": "País", "en": "Country"},
    "col_parecido": {"es": "Parecido", "en": "Match"},
    "top_alt": {"es": "Los cinco lugares de la Tierra más parecidos a {sitio}. Elige una fila para ver su ficha.",
                "en": "The five places on Earth most similar to {sitio}. Choose a row to see its fact sheet."},
    "top_nota": {"es": "Elige una fila para ver su ficha. El número (#) es el puesto en la lista completa; se saltan los lugares con "
                       "pueblos o vegetación.",
                 "en": "Choose a row to see its fact sheet. The number (#) is the rank in the full list; places near towns or with "
                       "vegetation are skipped."},
    # ---- ficha ----
    "ver_ficha": {"es": "Ver la ficha de", "en": "Open the fact sheet for"},
    "se_parece": {"es": "Se parece a {sitio} en un {n} %", "en": "{n}% match with {sitio}"},
    "calculado": {"es": "Calculado con {n} de {total} aspectos", "en": "Based on {n} of {total} aspects"},
    "sin_dato": {"es": "Sin dato", "en": "No data"},
    "sin_comparar": {"es": "Sin comparar", "en": "Not compared"},
    "no_cuenta": {"es": "No cuenta en la nota (importancia: nada).", "en": "Does not count toward the score (importance: none)."},
    "no_imitar": {"es": "Lo que la Tierra no puede imitar de {cuerpo}", "en": "What Earth cannot reproduce from {cuerpo}"},
    "nivel_alto": {"es": "Muy parecido", "en": "Strong match"},
    "nivel_medio": {"es": "Parecido medio", "en": "Moderate match"},
    "nivel_bajo": {"es": "Poco parecido", "en": "Weak match"},
    "limites_moon": {"es": ["Gravedad: 1/6 de la terrestre", "Sin atmósfera (vacío)", "Radiación sin protección", "Polvo abrasivo en el suelo"],
                     "en": ["Gravity: 1/6 of Earth's", "No atmosphere (vacuum)", "Unshielded radiation", "Abrasive dust on the ground"]},
    "limites_mars": {"es": ["Gravedad: 38 % de la terrestre", "Atmósfera muy delgada", "Radiación alta", "Percloratos en el suelo"],
                     "en": ["Gravity: 38% of Earth's", "Very thin atmosphere", "High radiation", "Perchlorates in the soil"]},
    "limites_largos_moon": {"es": ["gravedad ~1/6 g", "vacío (sin atmósfera)", "radiación sin protección", "regolito/polvo abrasivo"],
                            "en": ["gravity ~1/6 g", "vacuum (no atmosphere)", "unshielded radiation", "abrasive regolith/dust"]},
    "limites_largos_mars": {"es": ["gravedad ~0.38 g", "atmósfera ~0.6% de la terrestre", "radiación elevada", "percloratos en el suelo"],
                            "en": ["gravity ~0.38 g", "atmosphere ~0.6% of Earth's", "elevated radiation", "perchlorates in the soil"]},
    "terreno_volcanica": {"es": "roca volcánica", "en": "volcanic rock"},
    "terreno_algo_volcanica": {"es": "algo de roca volcánica", "en": "some volcanic rock"},
    "terreno_llano": {"es": "llano", "en": "flat"},
    "terreno_ondulado": {"es": "ondulado", "en": "rolling"},
    "terreno_montanoso": {"es": "montañoso", "en": "mountainous"},
    "terreno_sin": {"es": "terreno sin descripción", "en": "terrain without a description"},
    "orient_n": {"es": "N", "en": "N"}, "orient_s": {"es": "S", "en": "S"},
    "orient_e": {"es": "E", "en": "E"}, "orient_o": {"es": "O", "en": "W"},
    # ---- explicaciones por aspecto ----
    "ex_thermal_marte": {"es": "No hay un mapa de temperatura de Marte que sirva para comparar.",
                         "en": "There is no Mars temperature map suitable for comparison."},
    "ex_thermal_falta": {"es": "Falta el dato de temperatura para comparar este lugar.",
                         "en": "The temperature data needed to compare this place is missing."},
    "ex_sin_comparar": {"es": "No se pudo comparar este aspecto.", "en": "This aspect could not be compared."},
    "ex_topo_igual": {"es": "El terreno tiene pendientes y rugosidad parecidas a {sitio}.",
                      "en": "The terrain has slopes and roughness similar to {sitio}."},
    "ex_topo_rugoso": {"es": "El terreno es algo más rugoso que en {sitio}.", "en": "The terrain is somewhat rougher than at {sitio}."},
    "ex_topo_llano": {"es": "El terreno es algo más llano que en {sitio}.", "en": "The terrain is somewhat flatter than at {sitio}."},
    "ex_topo_forma": {"es": "La pendiente media es parecida, pero la forma del relieve difiere de {sitio}.",
                      "en": "The average slope is similar, but the shape of the terrain differs from {sitio}."},
    "ex_thermal_calor": {"es": "Hace más calor que en {sitio} en el mes más cálido.", "en": "It is hotter than {sitio} in the warmest month."},
    "ex_thermal_frio": {"es": "Hace más frío que en {sitio} en el mes más cálido.", "en": "It is colder than {sitio} in the warmest month."},
    "ex_thermal_igual": {"es": "Temperaturas máximas y rango entre día y noche parecidos a {sitio}.",
                         "en": "Maximum temperatures and day-night range similar to {sitio}."},
    "ex_ice_sin_nieve": {"es": "Ojo: coincide porque no hay nieve, no porque haya hielo bajo el suelo.",
                         "en": "Note: it matches because there is no snow, not because there is ice underground."},
    "ex_ice_nieve": {"es": "Coincide en cobertura de nieve, que es solo una pista del hielo bajo el suelo.",
                     "en": "It matches in snow cover, which is only a hint of ice underground."},
    "ex_ice_no": {"es": "En la Tierra se mide con la nieve; aquí no coincide con el hielo del sitio.",
                  "en": "On Earth it is measured with snow; here it does not match the ice at the site."},
    "ex_geo_si": {"es": "Es roca volcánica (basalto), como gran parte de {de}.", "en": "It is volcanic rock (basalt), like much of {de}."},
    "ex_geo_algo": {"es": "Tiene algo de roca volcánica (basalto), el tipo de roca de {de}.",
                    "en": "It has some volcanic rock (basalt), the rock type of {de}."},
    "ex_geo_poco": {"es": "Tiene poca roca volcánica (basalto).", "en": "It has little volcanic rock (basalt)."},
    "geo_de_mars": {"es": "Marte", "en": "Mars"},
    "geo_de_moon": {"es": "los mares lunares", "en": "the lunar maria"},
    "geo_cuerpo_moon": {"es": "la Luna", "en": "the Moon"},
    "geo_cuerpo_mars": {"es": "Marte", "en": "Mars"},
    # ---- sitios ----
    "sitio_aterrizaje": {"es": "Sitio de aterrizaje ({year})", "en": "Landing site ({year})"},
    "sitio_aterrizaje_gen": {"es": "Sitio de aterrizaje o candidato", "en": "Landing site or candidate"},
    "desc_Jezero": {"es": "Cráter con un antiguo delta de río. Aquí está el rover Perseverance.",
                    "en": "Crater with an ancient river delta. The Perseverance rover is here."},
    "desc_Oxia Planum": {"es": "Llanura con arcillas, sitio del rover europeo ExoMars.", "en": "Clay-rich plain, site of the European ExoMars rover."},
    "desc_Arcadia Planitia": {"es": "Llanura del norte de Marte con hielo cerca de la superficie.",
                              "en": "Plain in northern Mars with ice near the surface."},
    "desc_Shackleton rim": {"es": "Borde de un cráter en el polo sur de la Luna, con zonas en sombra permanente.",
                            "en": "Rim of a crater at the Moon's south pole, with permanently shadowed areas."},
    "desc_Malapert massif": {"es": "Montaña cerca del polo sur de la Luna, con luz solar casi continua.",
                             "en": "Mountain near the Moon's south pole, with almost continuous sunlight."},
    "desc_Mare Tranquillitatis pit": {"es": "Hoyo en el Mar de la Tranquilidad, posible entrada a un tubo de lava.",
                                      "en": "Pit in the Sea of Tranquility, a possible entrance to a lava tube."},
    # ---- confiabilidad: glosario ----
    "glosario_lista": {"es": [("Análogo", "Lugar de la Tierra parecido a otro mundo que los científicos ya usan para ensayar (por ejemplo, Atacama o Lanzarote)."),
                              ("Candidato", "Zona de la Tierra que el método marca como parecida al sitio elegido. Es una hipótesis para revisar con expertos, no un hallazgo."),
                              ("Parecido", "Nota de 0 a 100 %: 100 % es idéntico en los aspectos medidos. No es la probabilidad de que el lugar sirva."),
                              ("Aspecto", "Cada cosa que se compara: relieve, temperatura, hielo o agua y geología. Si falta el dato de uno, no cuenta."),
                              ("Confianza", "Cuánto acierta el método al reconocer análogos conocidos. 50 % es adivinar; con la Luna y Marte queda en torno al 60 %."),
                              ("Azar (50 %)", "Lo que saldría si el método no supiera nada.")],
                       "en": [("Analog", "A place on Earth that resembles another world and that scientists already use for rehearsals (for example, Atacama or Lanzarote)."),
                              ("Candidate", "An area on Earth that the method flags as similar to the chosen site. It is a hypothesis to review with experts, not a finding."),
                              ("Match", "A score from 0 to 100%: 100% is identical in the aspects measured. It is not the probability that the place is useful."),
                              ("Aspect", "Each thing that is compared: terrain, temperature, ice or water, and geology. If the data for one is missing, it does not count."),
                              ("Confidence", "How often the method correctly recognizes known analogs. 50% is guessing; for the Moon and Mars it is around 60%."),
                              ("Chance (50%)", "What would come out if the method knew nothing.")]},
    # ---- detalles técnicos y expanders ----
    "tec_titulo": {"es": "Detalles técnicos y validación", "en": "Technical details and validation"},
    "tec_auc": {"es": "AUC contra los análogos conocidos", "en": "AUC against known analogs"},
    "tec_recall": {"es": "Recall en el {n} % mejor", "en": "Recall in the top {n}%"},
    "tec_nota": {"es": "AUC: 0,5 = azar. Es la medida de este sitio contra los análogos del cuerpo. Muy ruidosas: hay pocos análogos por "
                       "tipo y faltan dimensiones (docs/VALIDACION.md y docs/INFORME.md).",
                 "en": "AUC: 0.5 = chance. This is the measure for this site against the body's analogs. Very noisy: there are few "
                       "analogs per type and some dimensions are missing (docs/VALIDACION.md and docs/INFORME.md, in Spanish)."},
    "tec_tabla_alt": {"es": "Tabla técnica de los lugares más parecidos a {sitio}", "en": "Technical table of the places most similar to {sitio}"},
    "tec_hielo_nota": {"es": "«Hielo o agua» en la Tierra es la cobertura de nieve: coincide por ausencia de nieve, no por hielo subsuperficial "
                             "ni sequedad (docs/VALIDACION_ASPECTO.md).",
                       "en": "“Ice or water” on Earth is snow cover: it matches because there is no snow, not because of subsurface ice "
                             "or dryness (docs/VALIDACION_ASPECTO.md, in Spanish)."},
    "tec_limites": {"es": "Límites de la analogía (lo que la Tierra no reproduce)", "en": "Limits of the analogy (what Earth does not reproduce)"},
    "cand_titulo": {"es": "Candidatos destacados", "en": "Featured candidates"},
    "cand_regla": {"es": "Regla de selección y valoración honesta en docs/FICHAS_CANDIDATOS.md.",
                   "en": "Selection rule and honest assessment in docs/FICHAS_CANDIDATOS.md (in Spanish)."},
    "cand_alt": {"es": "Candidatos destacados con sus datos de contexto", "en": "Featured candidates with their context data"},
    "cand_nota": {"es": "Las candidatas lunares salen solo por topografía y se consideran pobres.",
                  "en": "The lunar candidates come out from terrain alone and are considered weak."},
    "atlas_titulo": {"es": "Atlas por aspecto: qué se parece dónde", "en": "Atlas by aspect: what resembles what, and where"},
    "atlas_mas": {"es": "Más detalles en docs/ATLAS_ASPECTOS.md.", "en": "More details in docs/ATLAS_ASPECTOS.md (in Spanish)."},
    "atlas_cuerpo": {"es": "Cuerpo", "en": "Body"},
    "atlas_aspecto": {"es": "Aspecto", "en": "Aspect"},
    "atlas_hielo": {"es": "Hielo / agua", "en": "Ice / water"},
    "atlas_confianza": {"es": "Confianza", "en": "Confidence"},
    "atlas_ninguna": {"es": "No hay ninguna región que recomendar para este aspecto.", "en": "There is no region to recommend for this aspect."},
    "atlas_tabla_alt": {"es": "Regiones recomendadas para este aspecto", "en": "Regions recommended for this aspect"},
    "atlas_mapa_alt": {"es": "Mapa del mundo con las celdas más parecidas según este aspecto",
                       "en": "World map with the cells most similar according to this aspect"},
    "atlas_nota": {"es": "Cada aspecto se evalúa por separado. Ningún aspecto llega a confianza alta: hay muy pocos análogos para validarlos.",
                   "en": "Each aspect is evaluated separately. No aspect reaches high confidence: there are too few analogs to validate them."},
    "atlas_nota_tooltip": {"es": "{cell_id}\nnota: {score}", "en": "{cell_id}\nscore: {score}"},
    "casos_titulo": {"es": "Recomendaciones por caso de uso", "en": "Recommendations by use case"},
    "casos_mas": {"es": "Más detalles en docs/CASOS_DE_USO.md.", "en": "More details in docs/CASOS_DE_USO.md (in Spanish)."},
    "casos_label": {"es": "Caso de uso", "en": "Use case"},
    "casos_alt": {"es": "Regiones recomendadas para este caso de uso", "en": "Regions recommended for this use case"},
    "casos_nota": {"es": "Solo el caso de terreno basáltico de Marte da una recomendación defendible; en frío y hielo el puntaje alto o bajo "
                         "refleja los límites de la Tierra como análogo (la «nieve» no es hielo subsuperficial). Son hipótesis. "
                         "El caso «Hielo en el suelo y permafrost» usa el mapa de permafrost de Obu et al. (2018) y objetivos de Marte con "
                         "hielo expuesto publicado; son regiones de permafrost real (Groenlandia libre de hielo y Ártico canadiense), no "
                         "una predicción.",
                   "en": "Only the basaltic terrain case for Mars gives a defensible recommendation; for cold and ice, a high or low "
                         "score reflects the limits of Earth as an analog (“snow” is not subsurface ice). These are hypotheses. The "
                         "“Ground ice and permafrost” case uses the permafrost map by Obu et al. (2018) and Mars targets with published "
                         "exposed ice; they are real permafrost regions (ice-free Greenland and the Canadian Arctic), not a prediction."},
    "creditos_titulo": {"es": "Créditos y fuentes de datos", "en": "Credits and data sources"},
    "creditos": {"es": ("- **Luna:** LRO LOLA, LRO Diviner, Lunar Prospector GRS, LROC (NASA/ASU), pits de LROC QuickMap (Losarcos y Dombard 2026, CC BY 4.0).\n"
                        "- **Marte:** MGS MOLA, Mars Odyssey GRS, Mars Global Cave Candidate Catalog (USGS, Cushing).\n"
                        "- **Tierra:** Copernicus DEM GLO-90 (ESA; contiene datos modificados de Copernicus), NASA MODIS (LST, nieve, NDVI), "
                        "NASA GLDAS y MERRA-2, NASA SEDAC GRUMP (CIESIN), GLiM (Hartmann y Moosdorf 2012, CC BY 3.0), "
                        "capa de análogos del USGS (Hunter 2020), Pyroduct (Romio y Lobosco 2024, CC BY 4.0).\n"
                        "- **Nombres de lugares y países:** Natural Earth 1:110m (dominio público).\n"
                        "- Procedencia completa, licencias y límites: docs/FUENTES.md y docs/LICENCIAS.md. "
                        "Parte de la búsqueda de fuentes y del código se hizo con asistentes de IA y se revisó por el equipo."),
                 "en": ("- **Moon:** LRO LOLA, LRO Diviner, Lunar Prospector GRS, LROC (NASA/ASU), pits from LROC QuickMap (Losarcos and Dombard 2026, CC BY 4.0).\n"
                        "- **Mars:** MGS MOLA, Mars Odyssey GRS, Mars Global Cave Candidate Catalog (USGS, Cushing).\n"
                        "- **Earth:** Copernicus DEM GLO-90 (ESA; contains modified Copernicus data), NASA MODIS (LST, snow, NDVI), "
                        "NASA GLDAS and MERRA-2, NASA SEDAC GRUMP (CIESIN), GLiM (Hartmann and Moosdorf 2012, CC BY 3.0), "
                        "USGS analog layer (Hunter 2020), Pyroduct (Romio and Lobosco 2024, CC BY 4.0).\n"
                        "- **Place and country names:** Natural Earth 1:110m (public domain).\n"
                        "- Full provenance, licenses and limits: docs/FUENTES.md and docs/LICENCIAS.md (in Spanish). "
                        "Part of the source search and of the code was done with AI assistants and reviewed by the team.")},
}

# ---- textos que vienen de archivos de resultados (en español): traducción al inglés por texto exacto; sin traducción se muestra el original ----
CASOS_EN = {
    "Hielo en el suelo y permafrost (Marte), con mapa de permafrost": "Ground ice and permafrost (Mars), with a permafrost map",
    "Hielo y permafrost en el norte de Marte": "Ice and permafrost in northern Mars",
    "Operaciones en frío en los polos lunares": "Cold operations at the lunar poles",
    "Probar movilidad y aterrizaje (Luna)": "Test mobility and landing (Moon)",
    "Probar movilidad y aterrizaje (Marte)": "Test mobility and landing (Mars)",
    "Terreno basáltico (Marte)": "Basaltic terrain (Mars)",
    "Terreno volcánico y tubos de lava (Luna)": "Volcanic terrain and lava tubes (Moon)",
}
CONFIANZA_EN = {"muy baja": "very low", "baja": "low", "media": "medium", "alta": "high", "sin datos": "no data"}
ATLAS_WHY_EN = {
    "Con la capa del USGS (cráteres frente a controles igual de llanos) no hay señal: AUC 0,48. Por análogos etiquetados, +0,14 con intervalo que incluye el cero.":
        "With the USGS layer (craters versus equally flat controls) there is no signal: AUC 0.48. By labeled analogs, +0.14 with an interval that includes zero.",
    "Dirección correcta (+0,64) pero con 1 a 3 análogos por grupo; el p mínimo alcanzable es 0,25. El proxy lunar (FeO) y la roca basáltica de la Tierra no miden lo mismo.":
        "Right direction (+0.64) but with 1 to 3 analogs per group; the smallest attainable p is 0.25. The lunar proxy (FeO) and Earth's basaltic rock do not measure the same thing.",
    "Dirección correcta (+0,97) pero descansa en un solo análogo (Craters of the Moon). La geología de Marte satura en casi todo el planeta.":
        "Right direction (+0.97) but it rests on a single analog (Craters of the Moon). Mars geology saturates over almost the whole planet.",
    "Falla donde debía acertar (Valles Secos, −0,75): la nieve no mide sequedad. La humedad del suelo (GLDAS) no mejora.":
        "It fails where it should succeed (Dry Valleys, −0.75): snow does not measure dryness. Soil moisture (GLDAS) does not help.",
    "La ventaja inicial (AUC 0,567) desaparece al controlar por terreno llano (0,494). Por análogos etiquetados, +0,15, no concluyente.":
        "The initial advantage (AUC 0.567) disappears when controlling for flat terrain (0.494). By labeled analogs, +0.15, inconclusive.",
    "Marte no tiene térmica en el modelo (decisión: no hay un mapa comparable).":
        "Mars has no thermal dimension in the model (decision: there is no comparable map).",
    "Ninguna celda de la Tierra supera 0.10 de parecido en este aspecto (máximo 0.000). En contra (−0,48) con una sola referencia (Haughton, polar) frente a objetivos casi todos ecuatoriales. La térmica de la Tierra son medias mensuales, no el pico real.":
        "No cell on Earth exceeds 0.10 similarity in this aspect (maximum 0.000). Against (−0.48) with a single reference (Haughton, polar) versus mostly equatorial targets. Earth's thermal data are monthly means, not the real peak.",
    "Solo 2 objetivos lunares (los polares) tienen dato de hielo y ningún análogo lleva esa etiqueta: no evaluable. La nieve de la Tierra no equivale al hielo de agua de la Luna.":
        "Only 2 lunar targets (the polar ones) have ice data and no analog carries that label: not evaluable. Earth's snow is not equivalent to the Moon's water ice.",
}


def t(lang: str, clave: str, **valores):
    """Texto de la interfaz en `lang` («es» o «en»; cualquier otro valor usa español). Rellena los `{campos}` con `valores`."""
    fila = TEXTOS[clave]
    texto = fila.get(lang) if lang in fila else fila["es"]
    return texto.format(**valores) if valores and isinstance(texto, str) else texto
