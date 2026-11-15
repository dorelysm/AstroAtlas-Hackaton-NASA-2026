"""Field-site risk indicators for an Earth place, from the data the model already holds.

Mission teams look for where to survive, not only where to land. These indicators flag conditions that make an Earth analog harder
or riskier to use as a field site. They are RULES OF THUMB, not a safety assessment: thresholds are indicative, the values are
50 km-window or grid-cell statistics (monthly means, not extremes), and some risks cannot be measured with our data (radiation,
security and access). They never enter the similarity score.

Levels: 0 = low, 1 = medium, 2 = high, NaN = no data.
"""
import numpy as np
import pandas as pd

# key: (column, medium threshold, high threshold, direction). direction "up": larger is riskier; "down": smaller is riskier.
RULES: dict[str, tuple[str, float, float, str]] = {
    "slope": ("topo__slope_p90_deg", 8.0, 15.0, "up"),         # 90th-percentile slope at a 500 m baseline (degrees)
    "heat": ("thermal__t_max_k", 308.0, 320.0, "up"),          # hottest monthly mean daytime surface temperature (K)
    "cold": ("thermal_lst_night_min_k", 250.0, 235.0, "down"),  # coldest monthly mean night-time surface temperature (K)
    "dust": ("dust_surface_ugm3", 50.0, 150.0, "up"),          # mean annual surface dust concentration (ug/m3)
    "wind": ("wind10m_ms", 4.0, 6.0, "up"),                    # mean annual 10 m wind speed (m/s)
    "ice": ("ice__water_frac", 0.6, 0.9, "up"),                # mean annual snow cover (perennial snow/ice terrain)
    "altitude": ("elev_mean_m", 2500.0, 4000.0, "up"),         # mean elevation (m): thin air, more cosmic radiation
    "isolation": ("dist_settlement_km", 150.0, 300.0, "up"),   # distance to the nearest settlement of >= 1,000 people (km)
}
KEYS = list(RULES)
NOT_ASSESSED = ("radiation", "security")   # cannot be measured with the data of this project


def _level(values: pd.Series, medium: float, high: float, direction: str) -> pd.Series:
    v = pd.to_numeric(values, errors="coerce")
    if direction == "up":
        lvl = np.where(v >= high, 2.0, np.where(v >= medium, 1.0, 0.0))
    else:
        lvl = np.where(v <= high, 2.0, np.where(v <= medium, 1.0, 0.0))
    return pd.Series(np.where(v.isna(), np.nan, lvl), index=values.index)


def risk_levels(df: pd.DataFrame) -> pd.DataFrame:
    """Level (0/1/2/NaN) of every indicator for each row of `df`, plus `overall` (high if the mean level is >= 1 or two indicators are high; medium if the mean is >= 0.5 or one is high)."""
    out = pd.DataFrame(index=df.index)
    for key, (col, med, high, direction) in RULES.items():
        out[key] = _level(df[col], med, high, direction) if col in df.columns else np.nan
    mean = out[KEYS].mean(axis=1, skipna=True)
    n_high = (out[KEYS] == 2).sum(axis=1)
    # a single high indicator is never hidden by the average: it makes the overall level at least "medium"
    overall = np.where((mean >= 1.0) | (n_high >= 2), 2.0, np.where((mean >= 0.5) | (n_high >= 1), 1.0, 0.0))
    out["overall"] = np.where(mean.isna(), np.nan, overall)
    return out


def level_name(level: float) -> str:
    """'low' | 'medium' | 'high' | 'unknown' (key for the interface texts)."""
    if level is None or pd.isna(level):
        return "unknown"
    return ("low", "medium", "high")[int(level)]


def risk_values(row: pd.Series) -> dict[str, float]:
    """Raw value behind each indicator for one place (NaN if missing)."""
    return {k: (float(row[col]) if col in row.index and pd.notna(row[col]) else float("nan")) for k, (col, *_r) in RULES.items()}


def target_slope_level(profile: pd.Series) -> tuple[float, float]:
    """(90th-percentile slope in degrees, level) of the Moon or Mars target itself: landing and mobility hazard at the target."""
    col, med, high, direction = RULES["slope"]
    v = profile.get(col)
    if v is None or pd.isna(v):
        return float("nan"), float("nan")
    return float(v), float(_level(pd.Series([v]), med, high, direction).iloc[0])


RGB = {0: (52, 211, 153), 1: (251, 191, 36), 2: (255, 90, 90)}   # map colours; unknown = grey
RGB_UNKNOWN = (150, 160, 175)
