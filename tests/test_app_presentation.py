"""App presentation (design docs in Figma) in Spanish and English: place names, texts and rules; the model does not change."""
import pandas as pd
import pytest

from astroatlas.config import DIMENSIONS
from astroatlas.i18n import CASES_EN, TEXTS, t
from astroatlas.places import label
from astroatlas.presentation import (RELIABILITY, IMPORTANCE, reliability_notice, reliability, coordinates, describe_terrain,
                                   site_description, explain, glossary, table_selection_id, map_selection_id, short_limits, match_level,
                                   pct, weights_from_importance, new_selection, translate_case, translate_confidence, translate_why)


def test_curated_places_and_countries_in_both_languages():
    assert label(32.5, 37.5, "es") == ("Harrat ash-Shamah", "Siria / Jordania")
    assert label(32.5, 37.5, "en") == ("Harrat ash-Shamah", "Syria / Jordan")
    assert label(27.5, 17.5, "en") == ("Haruj", "Libya")
    assert label(19.8, -155.5, "es") == ("Isla de Hawái", "Estados Unidos")
    assert label(19.8, -155.5, "en")[0] == "Hawaii"
    assert label(-24.5, -69.25, "es")[1] == "Chile"
    assert label(37.5, -2.5, "en") == ("Iberian Peninsula", "Spain")


def test_places_longitude_0_360_and_unnamed():
    assert label(27.5, 17.5 + 360, "es") == label(27.5, 17.5, "es")
    assert label(0.0, -30.0, "es") == ("Zona sin nombre", "Sin país")  # mar abierto
    assert label(0.0, -30.0, "en") == ("Unnamed area", "No country")
    assert label(0.0, -30.0) == label(0.0, -30.0, "en")             # English by default
    assert label(0.0, -30.0, "fr") == label(0.0, -30.0, "en")       # unknown language -> English


def test_all_texts_exist_in_both_languages():
    assert not [k for k, v in TEXTS.items() if "es" not in v or "en" not in v]
    for k, v in TEXTS.items():  # lists and texts have the same shape in both languages
        assert type(v["es"]) is type(v["en"]), k
        if isinstance(v["es"], list):
            assert len(v["es"]) == len(v["en"]), k
        if isinstance(v["es"], str):  # the format {fields} are the same
            import re

            assert set(re.findall(r"\{(\w+)\}", v["es"])) == set(re.findall(r"\{(\w+)\}", v["en"])), k


def test_importancia_y_pesos():
    w = weights_from_importance({"topo": "none", "ice": "low"})
    assert w["topo"] == 0.0 and w["ice"] == IMPORTANCE["low"]
    assert w["thermal"] == 1.0 and set(w) == set(DIMENSIONS)  # what is missing counts as "high"
    assert t("es", "imp_high") == "Mucho" and t("en", "imp_high") == "A lot"


@pytest.mark.parametrize("score,clave", [(0.95, "nivel_alto"), (0.53, "nivel_medio"), (0.2, "nivel_bajo")])
def test_match_level_in_both_languages(score, clave):
    assert match_level(score, "es")[0] == t("es", clave)
    assert match_level(score, "en")[0] == t("en", clave)
    assert match_level(0.95, "en")[0] == "Strong match" and match_level(0.53, "en")[0] == "Moderate match"


def test_pct_and_reliability_consistent_with_docs():
    assert pct(0.823, "es") == "82 %" and pct(0.823) == "82%"
    for c in RELIABILITY.values():
        assert c["lo"] < c["pct"] < c["hi"] and c["pct"] > 50
    assert "50 %" in reliability_notice("es") and "58" in reliability_notice("es") and "60" in reliability_notice("es")
    assert "50%" in reliability_notice("en") and "58%" in reliability_notice("en")
    assert reliability("mars", "en")["nivel"] == "Early-stage confidence" and reliability("mars", "es")["nivel"] == "Confianza inicial"


def test_explanations_name_missing_data_and_the_snow_warning():
    cell = pd.Series({"topo__slope_mean_deg": 4.0, "ice__water_frac": 0.0, "geo__basalt_frac": 0.9})
    prof = pd.Series({"topo__slope_mean_deg": 2.0})
    assert "mapa de temperatura de Marte" in explain("thermal", None, cell, prof, "mars", "Jezero", "es")
    assert "Mars temperature map" in explain("thermal", None, cell, prof, "mars", "Jezero", "en")
    assert "no porque haya hielo" in explain("ice", 0.92, cell, prof, "mars", "Jezero", "es")
    assert "not because there is ice" in explain("ice", 0.92, cell, prof, "mars", "Jezero", "en")
    assert "más rugoso" in explain("topo", 0.5, cell, prof, "mars", "Jezero", "es")
    assert "rougher than at Jezero" in explain("topo", 0.5, cell, prof, "mars", "Jezero", "en")
    assert "basalto" in explain("geo", 1.0, cell, prof, "mars", "Jezero", "es")
    assert "basalt" in explain("geo", 1.0, cell, prof, "mars", "Jezero", "en")


def test_site_description_and_terrain():
    assert "Perseverance" in site_description("Jezero", "es") and "Perseverance" in site_description("Jezero")
    assert site_description("Apollo 11 LM", "es").startswith("Sitio de aterrizaje")
    assert site_description("Apollo 11 LM", "en").startswith("Landing site")
    fila = pd.Series({"geo__basalt_frac": 0.8, "topo__slope_mean_deg": 1.0})
    assert describe_terrain(fila, "es") == "roca volcánica, llano" and describe_terrain(fila, "en") == "volcanic rock, flat"


def test_coordinates_and_orientations():
    assert coordinates(32.5, 37.5, "es") == "32.5° N, 37.5° E"
    assert coordinates(-24.5, 290.75, "es") == "24.5° S, 69.2° O"  # 290,75 E = 69,25 O
    assert coordinates(-24.5, 290.75, "en") == "24.5° S, 69.2° W"


def test_seleccion_nueva_solo_cuenta_una_vez():
    assert new_selection(None, "earth_1_2") == "earth_1_2"
    assert new_selection("earth_1_2", "earth_1_2") is None   # the same selection does not overwrite the profile again
    assert new_selection("earth_1_2", "earth_3_4") == "earth_3_4"
    assert new_selection("earth_1_2", None) is None


def test_ids_de_seleccion_del_mapa_y_la_tabla():
    estado_mapa = {"selection": {"objects": {"candidatos": [{"cell_id": "earth_24_43", "lat": 27.5}]}, "indices": {"candidatos": [3]}}}
    assert map_selection_id(estado_mapa) == "earth_24_43"
    assert map_selection_id({"selection": {"objects": {"conocidos": [{"name": "Atacama"}]}}}) is None   # only the orange points count
    assert map_selection_id({"selection": {"objects": {}}}) is None and map_selection_id(None) is None
    tabla = pd.DataFrame({"cell_id": ["a", "b", "c"]})
    assert table_selection_id({"selection": {"rows": [1]}}, tabla) == "b"
    assert table_selection_id({"selection": {"rows": []}}, tabla) is None and table_selection_id(None, tabla) is None


def test_glosario_y_limites_en_los_dos_idiomas():
    es, en = glossary("es"), glossary("en")
    assert len(es) == len(en) and all(len(d) > 20 for _, d in es + en)
    assert [t_ for t_, _ in es][:2] == ["Análogo", "Candidato"] and [t_ for t_, _ in en][:2] == ["Analog", "Candidate"]
    assert short_limits("mars", "en")[0] == "Gravity: 38% of Earth's" and len(short_limits("moon", "es")) == 4


def test_traducciones_de_textos_de_resultados():
    assert translate_case("Terreno basáltico (Marte)", "en") == "Basaltic terrain (Mars)"
    assert translate_case("Terreno basáltico (Marte)", "es") == "Terreno basáltico (Marte)"
    assert translate_case("Un caso que no existe", "en") == "Un caso que no existe"   # without a translation the original is shown
    assert translate_confidence("baja", "en") == "low" and translate_confidence("baja", "es") == "baja"
    assert translate_why("texto sin traducción", "en") == "texto sin traducción"
    # the 7 use cases of the results file have a translation
    uc = pd.read_csv("demo_data/results/usecases.csv")
    assert all(x in CASES_EN for x in uc["title"].unique())
    reg = pd.read_csv("demo_data/results/atlas_regions.csv")
    from astroatlas.i18n import ATLAS_WHY_EN

    assert all(w in ATLAS_WHY_EN for w in reg["why"].dropna().unique())


def test_pie_de_pagina_en_los_dos_idiomas():
    es, en = t("es", "pie"), t("en", "pie")
    assert "AstroAtlas" in es and "AstroAtlas" in en and "2026" in es and "2026" in en
    assert "Hackatón" in es and "Hackathon" in en and "Space Apps Challenge" in es and "Space Apps Challenge" in en
