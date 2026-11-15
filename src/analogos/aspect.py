"""Validación por aspecto: cada dimensión debe recuperar los análogos que lo son POR ESE aspecto.

La ablación global (ablation.py) exigía a cada dimensión recuperar TODOS los análogos, aunque Atacama lo sea por su
sequedad y Mauna Kea por su basalto. Aquí cada análogo lleva etiquetas de aspecto (docs/aspectos_analogos.csv), sacadas
de las fuentes ya citadas y fijadas ANTES de medir (se registra su huella sha256 en los resultados).

Para cada cuerpo y dimensión D se usa la configuración "solo D" y se compara u (probabilidad de que el análogo puntúe
más que una celda típica, 0.5 = azar):
  - positivos: análogos etiquetados con D;
  - negativos: análogos que tienen etiquetas, pero ninguna es D.
Un análogo SIN etiquetas (a ese nivel de evidencia) no entra en ningún grupo: no sabemos por qué lo es.
`gap` = u medio de positivos - u medio de negativos. Con 2 a 6 análogos por grupo se usa una PRUEBA DE PERMUTACIÓN
EXACTA (una cola) y un bootstrap sobre los análogos; nada de supuestos de normalidad.

Niveles de evidencia de cada etiqueta: 1 fuente (la página citada nombra el aspecto), 2 nota (solo nuestra nota),
3 general (conocimiento sin fuente abierta). Se evalúa con los niveles <= 1, <= 2 y <= 3 para ver si el resultado
depende de cuánto se confía en las etiquetas.

    python -m analogos.aspect
"""
import argparse
import hashlib
import itertools
import json
from math import comb
from pathlib import Path

import numpy as np
import pandas as pd

from .ablation import run as run_ablation
from .config import DIMENSIONS, DOCS, RESULTS_DIR
from .validate import known_for_body, load_known

TAGS_CSV = DOCS / "aspectos_analogos.csv"
LEVELS = {"fuente": 1, "nota": 2, "general": 3}
LEVEL_NAMES = {1: "solo fuente", 2: "fuente + nota (principal)", 3: "fuente + nota + general"}
ASPECTS = list(DIMENSIONS)


def load_tags(path: Path = TAGS_CSV) -> pd.DataFrame:
    tags = pd.read_csv(path)
    bad = set(tags["nivel"]) - set(LEVELS)
    if bad:
        raise ValueError(f"niveles desconocidos en {path.name}: {bad}")
    bad = set(tags["aspect"]) - set(ASPECTS) - {"ninguno"}
    if bad:
        raise ValueError(f"aspectos desconocidos en {path.name}: {bad}")
    tags["level"] = tags["nivel"].map(LEVELS)
    return tags


def tags_hash(path: Path = TAGS_CSV) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def split_groups(tags: pd.DataFrame, analogs, aspect: str, max_level: int) -> tuple[list[str], list[str]]:
    """(positivos, negativos) entre `analogs` a un nivel de evidencia máximo."""
    t = tags[tags["level"] <= max_level]
    pos = sorted(set(t.loc[t["aspect"] == aspect, "name"]) & set(analogs))
    tagged = set(t["name"]) & set(analogs)
    return pos, sorted(tagged - set(pos))


def permutation_p(vals_on: np.ndarray, vals_off: np.ndarray, max_exact: int = 50_000, n_mc: int = 20_000, seed: int = 0) -> float:
    """P(gap aleatorio >= gap observado), una cola. Exacta si hay <= max_exact asignaciones; si no, Monte Carlo."""
    on, off = np.asarray(vals_on, float), np.asarray(vals_off, float)
    allv, k = np.concatenate([on, off]), len(on)
    obs = on.mean() - off.mean()
    n = len(allv)
    gaps = []
    if comb(n, k) <= max_exact:
        for idx in itertools.combinations(range(n), k):
            m = np.zeros(n, bool)
            m[list(idx)] = True
            gaps.append(allv[m].mean() - allv[~m].mean())
    else:
        rng = np.random.default_rng(seed)
        for _ in range(n_mc):
            m = np.zeros(n, bool)
            m[rng.choice(n, k, replace=False)] = True
            gaps.append(allv[m].mean() - allv[~m].mean())
    return float((np.asarray(gaps) >= obs - 1e-12).mean())


def evaluate_aspect(analog_u: pd.Series, tags: pd.DataFrame, aspect: str, max_level: int,
                    n_boot: int = 2000, seed: int = 0) -> dict:
    """analog_u: u medio de cada análogo (índice = nombre) con la dimensión `aspect` sola."""
    analog_u = analog_u.dropna()
    pos, neg = split_groups(tags, analog_u.index, aspect, max_level)
    out = {"aspect": aspect, "n_on": len(pos), "n_off": len(neg), "on": pos, "off": neg}
    if not pos or not neg:
        return {**out, "u_on": np.nan, "u_off": np.nan, "gap": np.nan, "gap_lo": np.nan, "gap_hi": np.nan,
                "p_perm": np.nan, "auc_rank": np.nan, "estado": "no evaluable (falta un grupo)"}
    on, off = analog_u[pos].to_numpy(), analog_u[neg].to_numpy()
    rng = np.random.default_rng(seed)
    boots = [rng.choice(on, len(on)).mean() - rng.choice(off, len(off)).mean() for _ in range(n_boot)]
    pairs = [(a > b) + 0.5 * (a == b) for a in on for b in off]
    return {**out, "u_on": float(on.mean()), "u_off": float(off.mean()), "gap": float(on.mean() - off.mean()),
            "gap_lo": float(np.percentile(boots, 2.5)), "gap_hi": float(np.percentile(boots, 97.5)),
            "p_perm": permutation_p(on, off), "auc_rank": float(np.mean(pairs)), "estado": "ok"}


def analog_means(df: pd.DataFrame, body: str, aspect: str) -> pd.Series:
    """u medio por análogo (sobre los objetivos del cuerpo con dato) con la dimensión `aspect` sola."""
    g = df[(df["body"] == body) & (df["config"] == f"solo {aspect}")]
    return g.groupby("analog")["u"].mean()


def run(df: pd.DataFrame | None = None, tags: pd.DataFrame | None = None, n_boot: int = 2000) -> pd.DataFrame:
    df = run_ablation() if df is None else df
    tags = load_tags() if tags is None else tags
    rows = []
    for level in (1, 2, 3):
        for body in ("moon", "mars"):
            for aspect in ASPECTS:
                r = evaluate_aspect(analog_means(df, body, aspect), tags, aspect, level, n_boot)
                rows.append({"nivel": level, "evidencia": LEVEL_NAMES[level], "body": body, **r})
    return pd.DataFrame(rows)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--boot", type=int, default=2000)
    ap.add_argument("--out", type=Path, default=RESULTS_DIR)
    a = ap.parse_args()
    res = run(n_boot=a.boot)
    a.out.mkdir(parents=True, exist_ok=True)
    res.drop(columns=["on", "off"]).to_csv(a.out / "aspect_summary.csv", index=False)
    meta = {"tags_sha256": tags_hash(), "tags_file": str(TAGS_CSV.name)}
    (a.out / "aspect_summary.json").write_text(json.dumps({**meta, "rows": res.round(4).to_dict("records")},
                                                          indent=2, ensure_ascii=False, default=str))
    pd.set_option("display.width", 230)
    print(f"etiquetas: {meta['tags_file']}  sha256 {meta['tags_sha256'][:16]}")
    for (level, body), g in res.groupby(["nivel", "body"]):
        print(f"\n=== {LEVEL_NAMES[level]} | {body}")
        print(g[["aspect", "n_on", "n_off", "u_on", "u_off", "gap", "gap_lo", "gap_hi", "p_perm", "auc_rank", "estado"]]
              .round(2).to_string(index=False))


if __name__ == "__main__":
    main()
