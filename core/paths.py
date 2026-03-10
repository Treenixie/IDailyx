from pathlib import Path
import sys


APP_NAME = "IDailyx"


def get_project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def get_base_path() -> Path:
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)
    return get_project_root()


def get_runtime_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return get_project_root()


def get_asset_path(filename: str) -> str | None:
    candidates = [
        get_base_path() / "assets" / filename,
        get_runtime_root() / "assets" / filename,
        get_base_path() / filename,
    ]

    for path in candidates:
        if path.exists():
            return str(path)

    return None


def get_data_dir() -> Path:
    return get_runtime_root() / "data"


def get_ideas_file_path() -> Path:
    return get_data_dir() / "ideas.json"


def get_legacy_ideas_file_path() -> Path:
    return get_project_root() / "data" / "ideas.json"


def get_old_appdata_ideas_file_path() -> Path:
    return Path.home() / "AppData" / "Roaming" / APP_NAME / "ideas.json"