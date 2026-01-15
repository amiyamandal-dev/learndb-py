"""Challenge and gamification data models."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class Difficulty(Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class ChallengeCategory(Enum):
    SELECT_BASICS = "select_basics"
    FILTERING = "filtering"
    JOINS = "joins"
    AGGREGATION = "aggregation"
    DDL = "ddl"
    DML = "dml"


class ValidationType(Enum):
    EXACT_MATCH = "exact_match"
    ROW_COUNT = "row_count"
    CONTAINS_ROWS = "contains_rows"
    COLUMN_CHECK = "column_check"


@dataclass
class ValidationRule:
    """Defines how to validate a challenge submission."""
    type: ValidationType
    expected_value: Any
    order_matters: bool = False
    case_sensitive: bool = False


@dataclass
class Challenge:
    """A SQL challenge for users to solve."""
    id: str
    title: str
    description: str  # Markdown
    category: ChallengeCategory
    difficulty: Difficulty
    xp_reward: int

    # Setup SQL to create tables and insert initial data
    setup_sql: List[str]

    # Validation rules for checking solutions
    validation_rules: List[ValidationRule]

    # Optional reference solution
    expected_query: Optional[str] = None

    # Hints (progressively revealed)
    hints: List[str] = field(default_factory=list)
    hint_penalty_xp: int = 5

    # Metadata
    estimated_time_minutes: int = 5
    prerequisites: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)

    # Shown after completion
    concept_explanation: Optional[str] = None


@dataclass
class ChallengeSubmission:
    """A user's submission for a challenge."""
    challenge_id: str
    session_id: str
    submitted_sql: str
    submitted_at: str
    passed: bool
    execution_time_ms: float
    hints_used: int
    xp_earned: int
    feedback: str
    actual_output: Any = None


# Level definitions for gamification
@dataclass
class LevelDefinition:
    level: int
    name: str
    xp_required: int


LEVELS: List[LevelDefinition] = [
    LevelDefinition(1, "SQL Novice", 0),
    LevelDefinition(2, "Query Apprentice", 100),
    LevelDefinition(3, "Data Explorer", 300),
    LevelDefinition(4, "Table Master", 600),
    LevelDefinition(5, "Join Journeyman", 1000),
    LevelDefinition(6, "Aggregate Adept", 1500),
    LevelDefinition(7, "Schema Sage", 2100),
    LevelDefinition(8, "Index Innovator", 2800),
    LevelDefinition(9, "Database Architect", 3600),
    LevelDefinition(10, "SQL Grandmaster", 5000),
]


@dataclass
class Badge:
    """An achievement badge."""
    id: str
    name: str
    description: str
    icon: str
    criteria_type: str
    criteria_value: Any
    xp_bonus: int = 0


BADGES: List[Badge] = [
    Badge("first_query", "First Steps", "Execute your first SQL query", "rocket", "query_count", 1),
    Badge("first_challenge", "Challenge Accepted", "Complete your first challenge", "trophy", "challenge_count", 1),
    Badge("streak_3", "Consistent", "Maintain a 3-day streak", "fire", "streak", 3),
    Badge("streak_7", "Dedicated", "Maintain a 7-day streak", "fire", "streak", 7),
    Badge("select_master", "SELECT Master", "Complete all SELECT challenges", "star", "category_complete", "select_basics"),
    Badge("join_expert", "Join Expert", "Complete all JOIN challenges", "link", "category_complete", "joins"),
    Badge("speed_demon", "Speed Demon", "Complete a challenge in under 30 seconds", "bolt", "speed", 30),
    Badge("ten_challenges", "Getting Serious", "Complete 10 challenges", "award", "challenge_count", 10),
]


@dataclass
class UserProgress:
    """Tracks a user's progress and achievements."""
    user_id: str
    total_xp: int = 0
    current_level: int = 1
    current_streak: int = 0
    longest_streak: int = 0
    last_activity_date: Optional[str] = None
    completed_challenges: List[str] = field(default_factory=list)
    earned_badges: List[str] = field(default_factory=list)
    total_queries_executed: int = 0
    hints_used: int = 0

    def get_level_info(self) -> LevelDefinition:
        """Get current level information."""
        for level in reversed(LEVELS):
            if self.total_xp >= level.xp_required:
                return level
        return LEVELS[0]

    def xp_to_next_level(self) -> int:
        """Get XP needed for next level."""
        current = self.get_level_info()
        for level in LEVELS:
            if level.level > current.level:
                return level.xp_required - self.total_xp
        return 0  # Max level reached
