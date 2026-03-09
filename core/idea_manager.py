import random
import uuid
from copy import deepcopy
from datetime import datetime
from typing import List, Dict, Optional

from core.constants import DEFAULT_IDEA


class IdeaManager:
    def __init__(self, ideas: Optional[List[Dict]] = None):
        self.ideas = ideas if ideas is not None else []

    def get_all(self) -> List[Dict]:
        return self.ideas

    def add_idea(self, idea_data: Dict) -> Dict:
        new_idea = deepcopy(DEFAULT_IDEA)
        new_idea.update(idea_data)

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_idea["id"] = str(uuid.uuid4())
        new_idea["created_at"] = current_time
        new_idea["updated_at"] = current_time

        self.ideas.append(new_idea)
        return new_idea

    def get_by_id(self, idea_id: str) -> Optional[Dict]:
        for idea in self.ideas:
            if idea["id"] == idea_id:
                return idea
        return None

    def update_idea(self, idea_id: str, updated_data: Dict) -> Optional[Dict]:
        idea = self.get_by_id(idea_id)
        if idea is None:
            return None

        protected_fields = {"id", "created_at"}

        for key, value in updated_data.items():
            if key not in protected_fields:
                idea[key] = value

        idea["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return idea

    def delete_idea(self, idea_id: str) -> bool:
        for index, idea in enumerate(self.ideas):
            if idea["id"] == idea_id:
                del self.ideas[index]
                return True
        return False

    def toggle_favorite(self, idea_id: str) -> bool:
        idea = self.get_by_id(idea_id)
        if idea is None:
            return False

        idea["favorite"] = not idea["favorite"]
        idea["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return True

    def filter_ideas(
        self,
        query: str = "",
        genre: Optional[str] = None,
        status: Optional[str] = None,
        readiness: Optional[str] = None,
        mechanic: Optional[str] = None,
        favorites_only: bool = False,
    ) -> List[Dict]:
        query = query.strip().lower()
        filtered = []

        for idea in self.ideas:
            if favorites_only and not idea["favorite"]:
                continue

            if genre and idea["genre"] != genre:
                continue

            if status and idea["status"] != status:
                continue

            if readiness and idea["readiness"] != readiness:
                continue

            if mechanic and idea["mechanic"] != mechanic:
                continue

            if query:
                searchable_text = " ".join([
                    idea.get("title", ""),
                    idea.get("short_description", ""),
                    idea.get("notes", ""),
                ]).lower()

                if query not in searchable_text:
                    continue

            filtered.append(idea)

        return filtered

    def sort_ideas(self, ideas: List[Dict], sort_mode: str) -> List[Dict]:
        def parse_date(date_string: str) -> datetime:
            try:
                return datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                return datetime.min

        if sort_mode == "Сначала старые":
            return sorted(ideas, key=lambda idea: parse_date(idea["created_at"]))

        if sort_mode == "Недавно изменённые":
            return sorted(ideas, key=lambda idea: parse_date(idea["updated_at"]), reverse=True)

        if sort_mode == "По названию (А-Я)":
            return sorted(ideas, key=lambda idea: idea["title"].lower())

        if sort_mode == "По названию (Я-А)":
            return sorted(ideas, key=lambda idea: idea["title"].lower(), reverse=True)

        return sorted(ideas, key=lambda idea: parse_date(idea["created_at"]), reverse=True)

    def get_random_idea(self, ideas: Optional[List[Dict]] = None) -> Optional[Dict]:
        pool = ideas if ideas is not None else self.ideas

        if not pool:
            return None

        return random.choice(pool)