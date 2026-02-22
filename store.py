import requests
import json
from config import STORE_URL, CACHE_DIR
from pathlib import Path

CACHE_DIR.mkdir(parents=True, exist_ok=True)

def _cached_get(url, cache_file, max_age=300):
    """Fetch URL, using cache if fresh enough."""
    path = CACHE_DIR / cache_file
    import time
    if path.exists() and (time.time() - path.stat().st_mtime) < max_age:
        return json.loads(path.read_text())
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        data = r.json()
        path.write_text(json.dumps(data))
        return data
    except Exception as e:
        if path.exists():
            return json.loads(path.read_text())  # serve stale cache on error
        raise e

def fetch_registry():
    """Returns list of all app metadata dicts."""
    return _cached_get(f"{STORE_URL}/index.json", "index.json")

def fetch_featured():
    return _cached_get(f"{STORE_URL}/featured.json", "featured.json")

def fetch_app_meta(app_id):
    return _cached_get(f"{STORE_URL}/apps/{app_id}/metadata.json", f"{app_id}.json", max_age=60)

def search_apps(query, registry=None):
    if registry is None:
        registry = fetch_registry()
    q = query.lower()
    return [
        a for a in registry
        if q in a["name"].lower() or q in a.get("description", "").lower() or q in a.get("tags", [])
    ]
