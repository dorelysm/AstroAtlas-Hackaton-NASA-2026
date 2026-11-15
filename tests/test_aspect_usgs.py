import numpy as np

from analogos.aspect_usgs import auc_rank, compare_stratified


def _data(effect: float, n: int = 400, seed: int = 0):
    rng = np.random.default_rng(seed)
    flat = rng.uniform(0, 5, 2 * n)                     # variable de control (pendiente)
    pos = np.r_[np.ones(n, bool), np.zeros(n, bool)]
    u = rng.normal(0.5, 0.05, 2 * n) + effect * pos - 0.05 * flat  # la planitud aumenta u
    return u, pos, ~pos, flat


def test_stratified_detects_real_effect():
    u, pos, ctrl, flat = _data(effect=0.1)
    r = compare_stratified(u, pos, ctrl, flat, n_boot=200)
    assert r["estado"] == "ok" and r["senal"] and r["auc_estratificado"] > 0.7


def test_stratified_removes_confound():
    """Los positivos solo son más llanos: sin efecto propio, el AUC estratificado debe estar cerca de 0.5."""
    rng = np.random.default_rng(1)
    pos = np.r_[np.ones(400, bool), np.zeros(400, bool)]
    flat = np.where(pos, rng.uniform(0, 2, 800), rng.uniform(1, 5, 800))
    u = 0.9 - 0.15 * flat + rng.normal(0, 0.02, 800)
    r = compare_stratified(u, pos, ~pos, flat, n_boot=200)
    raw = auc_rank(u[pos], u[~pos])
    assert raw > 0.9                                   # sin control parece una señal enorme
    assert r["auc_estratificado"] < raw - 0.25         # el control la reduce mucho (queda confusión residual dentro de cada estrato)


def test_stratified_not_evaluable_when_empty():
    u = np.array([0.5, 0.6, 0.7])
    r = compare_stratified(u, np.array([True, False, False]), np.array([False, True, True]), np.array([1.0, 2.0, 3.0]))
    assert r["estado"] == "no evaluable"
