"""Coarse world regions (for the "Regions" filter of the app) from latitude and longitude.

The boxes are deliberately simple and APPROXIMATE (they are for narrowing a list on screen, not for geography): the first rule
that matches wins, so the order matters. Cells that match no rule (remote Atlantic and Indian Ocean islands) fall in "other".
"""
import numpy as np

REGIONS = ["africa", "europe", "asia", "north_america", "south_america", "oceania", "polar", "other"]


def macro_region(lat, lon) -> np.ndarray:
    """Region key of each (lat, lon) in degrees (longitude -180..180 or 0..360). Accepts scalars or arrays."""
    la = np.atleast_1d(np.asarray(lat, dtype=float))
    lo = np.atleast_1d(np.asarray(lon, dtype=float))
    lo = ((lo + 180.0) % 360.0) - 180.0
    rules = [
        (np.abs(la) >= 60, "polar"),                                                    # Arctic, Greenland, Antarctica
        ((lo <= -140) & (la < 30) & (la > -30), "oceania"),                             # Hawaii and the central Pacific
        ((la <= -11) & (lo >= 110) | (lo >= 150) & (la < 0), "oceania"),               # Australia, New Zealand, Melanesia
        ((lo >= -170) & (lo <= -50) & (la >= 15), "north_america"),
        ((lo >= -92) & (lo <= -30) & (la < 15), "south_america"),
        ((la <= 36) & (la >= -36) & (lo >= -20) & (lo <= 34.5) | (la < 12) & (la >= -36) & (lo > 34.5) & (lo <= 52), "africa"),
        ((la >= 36) & (lo >= -25) & (lo <= 26) | (la >= 42) & (lo > 26) & (lo <= 40), "europe"),
        ((lo >= 26) & (la >= -11), "asia"),                                             # Middle East, Central, South and East Asia
    ]
    out = np.full(la.shape, "other", dtype=object)
    done = np.zeros(la.shape, dtype=bool)
    for mask, key in rules:
        hit = mask & ~done
        out[hit] = key
        done |= hit
    return out
