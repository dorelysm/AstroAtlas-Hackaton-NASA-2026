"""Presentación de la app (docs de diseño en Figma): nombres de lugar, textos y reglas; el modelo no cambia."""
import pandas as pd
import pytest

from analogos.config import DIMENSIONS
from analogos.lugares import etiqueta
from analogos.presentacion import (CONFIABILIDAD, IMPORTANCIA, aviso_confiabilidad, describir_terreno, descripcion_sitio, explicar,
                                   nivel_parecido, pct, pesos_desde_importancia, seleccion_nueva,
                                   id_de_la_tabla, id_del_mapa)


def test_lugares_curados_y_paises():
    assert etiqueta(32.5, 37.5) == ("Harrat ash-Shamah", "Siria / Jordania")
    assert etiqueta(27.5, 17.5) == ("Haruj", "Libia")
    lugar, pais = etiqueta(19.8, -155.5)
    assert pais == "Estados Unidos" and lugar == "Isla de Hawái"
    assert etiqueta(-24.5, -69.25)[1] == "Chile"


def test_lugares_longitud_0_360_y_sin_nombre():
    assert etiqueta(27.5, 17.5 + 360) == etiqueta(27.5, 17.5)
    assert etiqueta(0.0, -30.0) == ("Zona sin nombre", "Sin país")  # mar abierto


def test_importancia_y_pesos():
    w = pesos_desde_importancia({"topo": "Nada", "ice": "Poco"})
    assert w["topo"] == 0.0 and w["ice"] == IMPORTANCIA["Poco"]
    assert w["thermal"] == 1.0 and set(w) == set(DIMENSIONS)  # lo que falta vale «Mucho»


@pytest.mark.parametrize("score,etiqueta_esperada", [(0.95, "Muy parecido"), (0.53, "Parecido medio"), (0.2, "Poco parecido")])
def test_nivel_parecido(score, etiqueta_esperada):
    assert nivel_parecido(score)[0] == etiqueta_esperada


def test_pct_y_confiabilidad_coherente_con_los_docs():
    assert pct(0.823) == "82 %"
    for c in CONFIABILIDAD.values():
        assert c["lo"] < c["pct"] < c["hi"] and c["pct"] > 50
    assert "50 %" in aviso_confiabilidad() and "58" in aviso_confiabilidad() and "60" in aviso_confiabilidad()


def test_explicaciones_dicen_los_datos_que_faltan_y_el_aviso_de_nieve():
    cell = pd.Series({"topo__slope_mean_deg": 4.0, "ice__water_frac": 0.0, "geo__basalt_frac": 0.9})
    prof = pd.Series({"topo__slope_mean_deg": 2.0})
    assert "mapa de temperatura de Marte" in explicar("thermal", None, cell, prof, "mars", "Jezero")
    assert "no porque haya hielo" in explicar("ice", 0.92, cell, prof, "mars", "Jezero")
    assert "más rugoso" in explicar("topo", 0.5, cell, prof, "mars", "Jezero")
    assert "basalto" in explicar("geo", 1.0, cell, prof, "mars", "Jezero")


def test_descripcion_de_sitio_y_terreno():
    assert "Perseverance" in descripcion_sitio("Jezero")
    assert descripcion_sitio("Apollo 11 LM").startswith("Sitio de aterrizaje")
    assert describir_terreno(pd.Series({"geo__basalt_frac": 0.8, "topo__slope_mean_deg": 1.0})) == "roca volcánica, llano"


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


def test_glosario_define_los_terminos_de_la_app():
    from analogos.presentacion import GLOSARIO

    terminos = [t for t, _ in GLOSARIO]
    for esperado in ("Análogo", "Candidato", "Parecido", "Aspecto", "Confianza"):
        assert esperado in terminos
    assert all(len(d) > 20 for _, d in GLOSARIO)  # definiciones completas, no etiquetas sueltas
