import json
import sys
from pathlib import Path

STORE_URL = "https://openmetro-src.creepernet.qzz.io"
APPS_DIR = Path.home() / ".openmetro" / "apps"
CACHE_DIR = Path.home() / ".openmetro" / "cache"
CONFIG_FILE = Path.home() / ".openmetro" / "config.json"

ACCENT = "#0078D4"
BG = "#1E1E1E"
BG_CARD = "#2D2D2D"
BG_HOVER = "#3D3D3D"
FG = "#FFFFFF"
FG_DIM = "#AAAAAA"
FONT = "Segoe UI"

CHUNK_SIZE = 8192

def get_base_path():
    """Returns the base path whether running frozen (PyInstaller) or as script."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).parent

def get_executable():
    """Returns the path to use when spawning subprocesses."""
    if getattr(sys, "frozen", False):
        return sys.executable  # openmetro.exe
    return sys.executable  # python.exe

def get_runner_args(entry, name):
    """Returns the args list to launch an app, works both frozen and unfrozen."""
    if getattr(sys, "frozen", False):
        return [sys.executable, "--run", str(entry), name]
    else:
        runner = get_base_path() / "runner.py"
        return [sys.executable, str(runner), str(entry), name]

def load_config():
    if CONFIG_FILE.exists():
        return json.loads(CONFIG_FILE.read_text())
    return {}

def save_config(data):
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(data, indent=2))
