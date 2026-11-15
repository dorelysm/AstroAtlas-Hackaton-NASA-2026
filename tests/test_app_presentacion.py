"""Presentación de la app (docs de diseño en Figma) en español e inglés: nombres de lugar, textos y reglas; el modelo no cambia."""
import pandas as pd
import pytest

from analogos.config import DIMENSIONS
from analogos.i18n import CASOS_EN, TEXTOS, t
from analogos.lugares import etiqueta
from analogos.presentacion import (CONFIABILIDAD, IMPORTANCIA, aviso_confiabilidad, confiabilidad, coordenadas, describir_terreno,
                                   descripcion_sitio, explicar, glosario, id_de_la_tabla, id_del_mapa, limites_cortos, nivel_parecido,
                                   pct, pesos_desde_importancia, seleccion_nueva, traducir_caso, traducir_confianza, traducir_why)


def test_lugares_curados_y_paises_en_los_dos_idiomas():
    assert etiqueta(32.5, 37.5, "es") == ("Harrat ash-Shamah", "Siria / Jordania")
    assert etiqueta(32.5, 37.5, "en") == ("Harrat ash-Shamah", "Syria / Jordan")
    assert etiqueta(27.5, 17.5, "en") == ("Haruj", "Libya")
    assert etiqueta(19.8, -155.5, "es") == ("Isla de Hawái", "Estados Unidos")
    assert etiqueta(19.8, -155.5, "en")[0] == "Hawaii"
    assert etiqueta(-24.5, -69.25, "es")[1] == "Chile"
    assert etiqueta(37.5, -2.5, "en") == ("Iberian Peninsula", "Spain")


def test_lugares_longitud_0_360_y_sin_nombre():
    assert etiqueta(27.5, 17.5 + 360, "es") == etiqueta(27.5, 17.5, "es")
    assert etiqueta(0.0, -30.0, "es") == ("Zona sin nombre", "Sin país")  # mar abierto
    assert etiqueta(0.0, -30.0, "en") == ("Unnamed area", "No country")
    assert etiqueta(0.0, -30.0) == etiqueta(0.0, -30.0, "es")             # español por defecto
    assert etiqueta(0.0, -30.0, "fr") == etiqueta(0.0, -30.0, "es")       # idioma desconocido → español


def test_todos_los_textos_existen_en_los_dos_idiomas():
    assert not [k for k, v in TEXTOS.items() if "es" not in v or "en" not in v]
    for k, v in TEXTOS.items():  # las listas y los textos tienen la misma forma en los dos idiomas
        assert type(v["es"]) is type(v["en"]), k
        if isinstance(v["es"], list):
            assert len(v["es"]) == len(v["en"]), k
        if isinstance(v["es"], str):  # los {campos} de formato son los mismos
            import re

            assert set(re.findall(r"\{(\w+)\}", v["es"])) == set(re.findall(r"\{(\w+)\}", v["en"])), k


def test_importancia_y_pesos():
    w = pesos_desde_importancia({"topo": "none", "ice": "low"})
    assert w["topo"] == 0.0 and w["ice"] == IMPORTANCIA["low"]
    assert w["thermal"] == 1.0 and set(w) == set(DIMENSIONS)  # lo que falta vale «high»
    assert t("es", "imp_high") == "Mucho" and t("en", "imp_high") == "A lot"


@pytest.mark.parametrize("score,clave", [(0.95, "nivel_alto"), (0.53, "nivel_medio"), (0.2, "nivel_bajo")])
def test_nivel_parecido_en_los_dos_idiomas(score, clave):
    assert nivel_parecido(score, "es")[0] == t("es", clave)
    assert nivel_parecido(score, "en")[0] == t("en", clave)
    assert nivel_parecido(0.95, "en")[0] == "Strong match" and nivel_parecido(0.53, "en")[0] == "Moderate match"


def test_pct_y_confiabilidad_coherente_con_los_docs():
    assert pct(0.823) == "82 %" and pct(0.823, "en") == "82%"
    for c in CONFIABILIDAD.values():
        assert c["lo"] < c["pct"] < c["hi"] and c["pct"] > 50
    assert "50 %" in aviso_confiabilidad("es") and "58" in aviso_confiabilidad("es") and "60" in aviso_confiabilidad("es")
    assert "50%" in aviso_confiabilidad("en") and "58%" in aviso_confiabilidad("en")
    assert confiabilidad("mars", "en")["nivel"] == "Low confidence" and confiabilidad("mars", "es")["nivel"] == "Confianza baja"


def test_explicaciones_dicen_los_datos_que_faltan_y_el_aviso_de_nieve():
    cell = pd.Series({"topo__slope_mean_deg": 4.0, "ice__water_frac": 0.0, "geo__basalt_frac": 0.9})
    prof = pd.Series({"topo__slope_mean_deg": 2.0})
    assert "mapa de temperatura de Marte" in explicar("thermal", None, cell, prof, "mars", "Jezero")
    assert "Mars temperature map" in explicar("thermal", None, cell, prof, "mars", "Jezero", "en")
    assert "no porque haya hielo" in explicar("ice", 0.92, cell, prof, "mars", "Jezero")
    assert "not because there is ice" in explicar("ice", 0.92, cell, prof, "mars", "Jezero", "en")
    assert "más rugoso" in explicar("topo", 0.5, cell, prof, "mars", "Jezero")
    assert "rougher than at Jezero" in explicar("topo", 0.5, cell, prof, "mars", "Jezero", "en")
    assert "basalto" in explicar("geo", 1.0, cell, prof, "mars", "Jezero")
    assert "basalt" in explicar("geo", 1.0, cell, prof, "mars", "Jezero", "en")


def test_descripcion_de_sitio_y_terreno():
    assert "Perseverance" in descripcion_sitio("Jezero") and "Perseverance" in descripcion_sitio("Jezero", "en")
    assert descripcion_sitio("Apollo 11 LM").startswith("Sitio de aterrizaje")
    assert descripcion_sitio("Apollo 11 LM", "en").startswith("Landing site")
    fila = pd.Series({"geo__basalt_frac": 0.8, "topo__slope_mean_deg": 1.0})
    assert describir_terreno(fila) == "roca volcánica, llano" and describir_terreno(fila, "en") == "volcanic rock, flat"


def test_coordenadas_y_orientaciones():
    assert coordenadas(32.5, 37.5) == "32.5° N, 37.5° E"
    assert coordenadas(-24.5, 290.75, "es") == "24.5° S, 69.2° O"  # 290,75 E = 69,25 O
    assert coordenadas(-24.5, 290.75, "en") == "24.5° S, 69.2° W"


def test_seleccion_nueva_solo_cuenta_una_vez():
    assert seleccion_nueva(None, "earth_1_2") == "earth_1_2"
    assert seleccion_nueva("earth_1_2", "earth_1_2") is None   # la misma selección no vuelve a pisar la ficha
    assert seleccion_nueva("earth_1_2", "earth_3_4") == "earth_3_4"
    assert seleccion_nueva("earth_1_2", None) is None


def test_ids_de_seleccion_del_mapa_y_la_tabla():
    estado_mapa = {"selection": {"objects": {"candidatos": [{"cell_id": "earth_24_43", "lat": 27.5}]}, "indices": {"candidatos": [3]}}}
    assert id_del_mapa(estado_mapa) == "earth_24_43"
    assert id_del_mapa({"selection": {"objects": {"conocidos": [{"name": "Atacama"}]}}}) is None   # solo cuentan los puntos naranjas
    assert id_del_mapa({"selection": {"objects": {}}}) is None and id_del_mapa(None) is None
    tabla = pd.DataFrame({"cell_id": ["a", "b", "c"]})
    assert id_de_la_tabla({"selection": {"rows": [1]}}, tabla) == "b"
    assert id_de_la_tabla({"selection": {"rows": []}}, tabla) is None and id_de_la_tabla(None, tabla) is None


def test_glosario_y_limites_en_los_dos_idiomas():
    es, en = glosario("es"), glosario("en")
    assert len(es) == len(en) and all(len(d) > 20 for _, d in es + en)
    assert [t_ for t_, _ in es][:2] == ["Análogo", "Candidato"] and [t_ for t_, _ in en][:2] == ["Analog", "Candidate"]
    assert limites_cortos("mars", "en")[0] == "Gravity: 38% of Earth's" and len(limites_cortos("moon", "es")) == 4


def test_traducciones_de_textos_de_resultados():
    assert traducir_caso("Terreno basáltico (Marte)", "en") == "Basaltic terrain (Mars)"
    assert traducir_caso("Terreno basáltico (Marte)", "es") == "Terreno basáltico (Marte)"
    assert traducir_caso("Un caso que no existe", "en") == "Un caso que no existe"   # sin traducción se muestra el original
    assert traducir_confianza("baja", "en") == "low" and traducir_confianza("baja", "es") == "baja"
    assert traducir_why("texto sin traducción", "en") == "texto sin traducción"
    # los 7 casos de uso del archivo de resultados tienen traducción
    uc = pd.read_csv("demo_data/results/usecases.csv")
    assert all(x in CASOS_EN for x in uc["title"].unique())
    reg = pd.read_csv("demo_data/results/atlas_regiones.csv")
    from analogos.i18n import ATLAS_WHY_EN

    assert all(w in ATLAS_WHY_EN for w in reg["why"].dropna().unique())


def test_pie_de_pagina_en_los_dos_idiomas():
    es, en = t("es", "pie"), t("en", "pie")
    assert "AstroAtlas" in es and "AstroAtlas" in en and "2026" in es and "2026" in en
    assert "Hackatón" in es and "Hackathon" in en and "Space Apps Challenge" in es and "Space Apps Challenge" in en
