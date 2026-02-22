import json
import subprocess
from pathlib import Path
from config import APPS_DIR, get_runner_args

def launch_app(app_id):
    app_dir = APPS_DIR / app_id
    manifest_path = app_dir / "manifest.json"

    if not manifest_path.exists():
        raise FileNotFoundError(f"App '{app_id}' is not installed.")

    manifest = json.loads(manifest_path.read_text())
    entry = app_dir / manifest.get("entry", "index.html")

    if not entry.exists():
        raise FileNotFoundError(f"App entry point not found: {entry}")

    args = get_runner_args(entry, manifest["name"])
    subprocess.Popen(args, close_fds=True)
