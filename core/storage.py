import json
import os
from typing import List, Dict


def ensure_data_file(path: str) -> None:
    folder = os.path.dirname(path)

    if folder and not os.path.exists(folder):
        os.makedirs(folder)

    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as file:
            json.dump([], file, ensure_ascii=False, indent=4)


def load_ideas(path: str) -> List[Dict]:
    ensure_data_file(path)

    try:
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)
            if isinstance(data, list):
                return data
            return []
    except (json.JSONDecodeError, OSError):
        return []


def save_ideas(path: str, ideas: List[Dict]) -> None:
    ensure_data_file(path)

    with open(path, "w", encoding="utf-8") as file:
        json.dump(ideas, file, ensure_ascii=False, indent=4)