import json
from pathlib import Path
from typing import List, Dict


def _normalize_path(path: str | Path) -> Path:
    return Path(path)


def ensure_data_file(path: str | Path) -> None:
    file_path = _normalize_path(path)

    file_path.parent.mkdir(parents=True, exist_ok=True)

    if not file_path.exists():
        file_path.write_text("[]", encoding="utf-8")


def load_ideas(path: str | Path) -> List[Dict]:
    file_path = _normalize_path(path)
    ensure_data_file(file_path)

    try:
        data = json.loads(file_path.read_text(encoding="utf-8"))

        if isinstance(data, list):
            return data

        return []
    except (json.JSONDecodeError, OSError):
        return []


def save_ideas(path: str | Path, ideas: List[Dict]) -> None:
    file_path = _normalize_path(path)
    ensure_data_file(file_path)

    file_path.write_text(
        json.dumps(ideas, ensure_ascii=False, indent=4),
        encoding="utf-8",
    )