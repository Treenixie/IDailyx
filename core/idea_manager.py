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