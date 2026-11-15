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
