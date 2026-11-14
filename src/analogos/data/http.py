"""GET JSON con reintentos y caché en disco (data/raw/cache). Solo biblioteca estándar."""
import hashlib
import json
import time
import urllib.error
import urllib.request

from ..config import RAW_DIR

CACHE_DIR = RAW_DIR / "cache"
USER_AGENT = "analogos-hackathon/0.1"


def get_json(url: str, retries: int = 4, timeout: float = 60, use_cache: bool = True) -> dict:
    cache_file = CACHE_DIR / (hashlib.sha1(url.encode()).hexdigest() + ".json")
    if use_cache and cache_file.exists():
        return json.loads(cache_file.read_text(encoding="utf-8"))

    last_err: Exception | None = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            if use_cache:
                CACHE_DIR.mkdir(parents=True, exist_ok=True)
                cache_file.write_text(json.dumps(data), encoding="utf-8")
            return data
        except urllib.error.HTTPError as e:
            last_err = e
            if e.code not in (429, 500, 502, 503, 504):  # error del cliente: no reintentar
                break
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
            last_err = e
        time.sleep(2 ** attempt)  # espera exponencial (respeta el 429 de POWER)
    raise RuntimeError(f"Fallo al consultar {url}: {last_err}")
