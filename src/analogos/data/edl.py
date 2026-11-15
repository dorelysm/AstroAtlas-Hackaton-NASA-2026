"""Login de NASA Earthdata leyendo EARTHDATA_USERNAME / EARTHDATA_PASSWORD de `.env`.

Nunca imprime ni registra las credenciales. `.env` está en .gitignore.
"""
import os
from pathlib import Path

from ..config import ROOT


def load_env(path: Path = ROOT / ".env") -> list[str]:
    """Carga KEY=VALUE de `.env` en os.environ SIN pisar variables ya definidas. Devuelve las claves cargadas."""
    loaded = []
    if not path.exists():
        return loaded
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key, value = key.strip(), value.strip().strip('"').strip("'")
        if value and key not in os.environ:
            os.environ[key] = value
            loaded.append(key)
    return loaded


def login():
    """Devuelve el módulo `earthaccess` ya autenticado."""
    load_env()
    try:
        import earthaccess
    except ImportError as e:  # pragma: no cover
        raise ImportError('Falta earthaccess: pip install -e ".[data]"') from e
    if not (os.environ.get("EARTHDATA_USERNAME") and os.environ.get("EARTHDATA_PASSWORD")):
        raise RuntimeError("Faltan EARTHDATA_USERNAME y EARTHDATA_PASSWORD en .env (ver .env.example)")
    if not earthaccess.login(strategy="environment").authenticated:
        raise RuntimeError("Login de Earthdata fallido: revisa usuario y contraseña en .env")
    return earthaccess
