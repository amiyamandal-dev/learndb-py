"""Challenge registry - collects all challenges from modules."""

from typing import Dict, List, Optional

from backend.models.challenge import Challenge, ChallengeCategory, Difficulty
from backend.content.challenges.select_basics import SELECT_BASICS_CHALLENGES
from backend.content.challenges.joins import JOIN_CHALLENGES
from backend.content.challenges.aggregation import AGGREGATION_CHALLENGES


class ChallengeRegistry:
    """Registry of all available challenges."""

    def __init__(self):
        self._challenges: Dict[str, Challenge] = {}
        self._load_challenges()

    def _load_challenges(self):
        """Load all challenges from modules."""
        all_challenges = (
            SELECT_BASICS_CHALLENGES +
            JOIN_CHALLENGES +
            AGGREGATION_CHALLENGES
        )

        for challenge in all_challenges:
            self._challenges[challenge.id] = challenge

    def get(self, challenge_id: str) -> Optional[Challenge]:
        """Get a challenge by ID."""
        return self._challenges.get(challenge_id)

    def list_all(self) -> List[Challenge]:
        """List all challenges."""
        return list(self._challenges.values())

    def list_by_category(self, category: ChallengeCategory) -> List[Challenge]:
        """List challenges by category."""
        return [c for c in self._challenges.values() if c.category == category]

    def list_by_difficulty(self, difficulty: Difficulty) -> List[Challenge]:
        """List challenges by difficulty."""
        return [c for c in self._challenges.values() if c.difficulty == difficulty]

    def get_categories(self) -> List[dict]:
        """Get all categories with their challenges."""
        categories = {}

        for challenge in self._challenges.values():
            cat_name = challenge.category.value

            if cat_name not in categories:
                categories[cat_name] = {
                    "name": cat_name,
                    "display_name": cat_name.replace("_", " ").title(),
                    "challenges": []
                }

            categories[cat_name]["challenges"].append({
                "id": challenge.id,
                "title": challenge.title,
                "difficulty": challenge.difficulty.value,
                "xp_reward": challenge.xp_reward,
            })

        return list(categories.values())


# Global registry instance
_registry: Optional[ChallengeRegistry] = None


def get_challenge_registry() -> ChallengeRegistry:
    """Get the global challenge registry."""
    global _registry
    if _registry is None:
        _registry = ChallengeRegistry()
    return _registry
