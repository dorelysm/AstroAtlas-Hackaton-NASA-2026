"""Objetivos de hielo somero (docs/PREREGISTRO_HIELO_SOMERO.md): integridad de la lista congelada."""
import hashlib

import pandas as pd

from analogos.hielo_somero import CSV


def test_frozen_ice_targets_unchanged():
    assert hashlib.sha256(CSV.read_bytes().replace(b"\r\n", b"\n")).hexdigest()[:16] == "02867f4eecc514ad"


def test_ice_targets_are_valid_mars_midlatitude_sites():
    t = pd.read_csv(CSV)
    assert len(t) == 8 and (t["body"] == "mars").all()
    assert t["lat"].abs().between(39, 70).all()
    assert (t["lon"] % 360).between(0, 360).all()
    assert t["coord_source"].str.contains("Dundas et al. 2021").all()


def test_pf2_class_and_ice_sheet_rule():
    import numpy as np

    from analogos.frio import on_ice_sheet, pf2_class

    t = pd.Series([260.0, 260.0, 280.0, np.nan])
    s = pd.Series([0.5, 0.95, 0.1, 0.1])
    c = pf2_class(t, s)
    assert list(c.iloc[:3]) == [1.0, 0.0, 0.0] and np.isnan(c.iloc[3])
    assert on_ice_sheet(-82.5, 167.5, float("nan")) and on_ice_sheet(75.0, -40.0, 0.95)
    assert not on_ice_sheet(72.5, -102.5, 0.65)


def test_permafrost_map_class_threshold():
    import numpy as np

    from analogos.permafrost_mapa import pf3_class

    c = pf3_class(np.array([1.0, 0.5, 0.49, np.nan, 0.0]))
    assert list(c) == [1.0, 1.0, 0.0, 0.0, 0.0]
