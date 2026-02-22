import requests
import hashlib
import zipfile
import json
import sys
import subprocess
import tempfile
import os
from pathlib import Path
from config import APPS_DIR, CHUNK_SIZE, CACHE_DIR, get_runner_args, get_executable

START_MENU = Path.home() / "AppData/Roaming/Microsoft/Windows/Start Menu/Programs/OpenMetro"

def register_start_menu(app_id, app_name, entry):
    if sys.platform != "win32":
        return
    try:
        args = get_runner_args(entry, app_name)
        # args[0] is the executable, rest are arguments
        target = args[0]
        arguments = " ".join(f'"{a}"' for a in args[1:])

        ps_script = f"""New-Item -ItemType Directory -Force -Path '{START_MENU}' | Out-Null
$ws = New-Object -ComObject WScript.Shell
$s = $ws.CreateShortcut('{START_MENU}\\{app_name}.lnk')
$s.TargetPath = '{target}'
$s.Arguments = '{arguments}'
$s.WorkingDirectory = '{Path(target).parent}'
$s.Description = '{app_name} - OpenMetro App'
$s.Save()
"""
        tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".ps1", delete=False, encoding="utf-8")
        tmp.write(ps_script)
        tmp.close()

        result = subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", tmp.name],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        os.unlink(tmp.name)

        if result.returncode != 0:
            print(f"PowerShell error: {result.stderr}")
    except Exception as e:
        print(f"Warning: could not create Start Menu shortcut: {e}")

def unregister_start_menu(app_name):
    if sys.platform != "win32":
        return
    shortcut = START_MENU / f"{app_name}.lnk"
    shortcut.unlink(missing_ok=True)

def _verify_checksum(file_path, expected_hash):
    sha = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(CHUNK_SIZE), b""):
            sha.update(chunk)
    return sha.hexdigest() == expected_hash

def download_app(app_meta, progress_callback=None, cancel_flag=None):
    APPS_DIR.mkdir(parents=True, exist_ok=True)
    tmp_path = CACHE_DIR / f"{app_meta['id']}.zip"
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    url = app_meta["download"]
    expected_hash = app_meta["checksum"].split(":")[1]

    headers = {}
    downloaded = 0
    if tmp_path.exists():
        downloaded = tmp_path.stat().st_size
        headers["Range"] = f"bytes={downloaded}-"

    try:
        with requests.get(url, headers=headers, stream=True, timeout=30) as r:
            if r.status_code == 416:
                tmp_path.unlink(missing_ok=True)
                downloaded = 0
                r = requests.get(url, stream=True, timeout=30)
                r.raise_for_status()

            r.raise_for_status()
            total = int(r.headers.get("content-length", 0)) + downloaded

            mode = "ab" if downloaded > 0 else "wb"
            with open(tmp_path, mode) as f:
                for chunk in r.iter_content(chunk_size=CHUNK_SIZE):
                    if cancel_flag and cancel_flag[0]:
                        return None
                    f.write(chunk)
                    downloaded += len(chunk)
                    if progress_callback:
                        progress_callback(downloaded, total)
    except requests.RequestException as e:
        raise ConnectionError(f"Download failed: {e}")

    if not _verify_checksum(tmp_path, expected_hash):
        tmp_path.unlink(missing_ok=True)
        raise ValueError("Checksum mismatch — file corrupted. Please try again.")

    app_dir = APPS_DIR / app_meta["id"]
    app_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(tmp_path) as z:
        z.extractall(app_dir)
    tmp_path.unlink(missing_ok=True)

    entry = app_meta.get("entry", "index.html")
    manifest = {
        "id": app_meta["id"],
        "name": app_meta["name"],
        "version": app_meta["version"],
        "author": app_meta.get("author", ""),
        "description": app_meta.get("description", ""),
        "entry": entry,
    }
    (app_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))

    register_start_menu(app_meta["id"], app_meta["name"], app_dir / entry)

    return app_dir


def get_installed_apps():
    APPS_DIR.mkdir(parents=True, exist_ok=True)
    apps = []
    for manifest in APPS_DIR.glob("*/manifest.json"):
        try:
            apps.append(json.loads(manifest.read_text()))
        except Exception:
            pass
    return apps


def uninstall_app(app_id):
    import shutil
    app_dir = APPS_DIR / app_id
    if app_dir.exists():
        manifest_path = app_dir / "manifest.json"
        if manifest_path.exists():
            try:
                manifest = json.loads(manifest_path.read_text())
                unregister_start_menu(manifest["name"])
            except Exception:
                pass
        shutil.rmtree(app_dir)
        return True
    return False


def is_update_available(store_meta):
    manifest = APPS_DIR / store_meta["id"] / "manifest.json"
    if not manifest.exists():
        return False
    local = json.loads(manifest.read_text())
    return local["version"] != store_meta["version"]


def is_installed(app_id):
    return (APPS_DIR / app_id / "manifest.json").exists()
