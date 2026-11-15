"""NASA Earthdata login reading EARTHDATA_USERNAME / EARTHDATA_PASSWORD from `.env`.

Never prints or logs the credentials. `.env` is in .gitignore.
"""
import os
from pathlib import Path

from ..config import ROOT


def load_env(path: Path = ROOT / ".env") -> list[str]:
    """Loads KEY=VALUE from `.env` into os.environ WITHOUT overriding variables already defined. Returns the keys loaded."""
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
    """Returns the already-authenticated `earthaccess` module."""
    load_env()
    try:
        import earthaccess
    except ImportError as e:  # pragma: no cover
        raise ImportError('Falta earthaccess: pip install -e ".[data]"') from e
    if not (os.environ.get("EARTHDATA_USERNAME") and os.environ.get("EARTHDATA_PASSWORD")):
        raise RuntimeError("EARTHDATA_USERNAME and EARTHDATA_PASSWORD are missing from .env (see .env.example)")
    if not earthaccess.login(strategy="environment").authenticated:
        raise RuntimeError("Earthdata login failed: check the user name and password in .env")
    return earthaccess
