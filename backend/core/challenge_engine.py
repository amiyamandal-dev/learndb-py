"""
Challenge Engine - Validates challenge submissions and tracks progress.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from backend.models.challenge import (
    Challenge,
    ChallengeSubmission,
    ValidationRule,
    ValidationType,
    UserProgress,
    LEVELS,
    BADGES,
)
from backend.core.session_manager import SessionManager, get_session_manager
from backend.core.learndb_adapter import QueryResult


class ChallengeEngine:
    """
    Handles challenge setup, submission validation, and progress tracking.
    """

    def __init__(self, session_manager: SessionManager = None):
        self.session_manager = session_manager or get_session_manager()
        self._user_progress: Dict[str, UserProgress] = {}

    def setup_challenge(self, session_id: str, challenge: Challenge) -> Tuple[bool, str]:
        """
        Set up the database for a challenge.

        Args:
            session_id: The session ID
            challenge: The challenge to set up

        Returns:
            Tuple of (success, message)
        """
        # Reset the session database
        self.session_manager.reset_session(session_id)

        # Execute setup SQL
        for sql in challenge.setup_sql:
            result = self.session_manager.execute_query(session_id, sql)
            if not result.success:
                return False, f"Setup failed: {result.error_message}"

        return True, "Challenge setup complete"

    def validate_submission(
        self,
        session_id: str,
        challenge: Challenge,
        submitted_sql: str,
        hints_used: int = 0
    ) -> ChallengeSubmission:
        """
        Validate a challenge submission.

        Args:
            session_id: The session ID
            challenge: The challenge being attempted
            submitted_sql: The user's SQL solution
            hints_used: Number of hints used

        Returns:
            ChallengeSubmission with results
        """
        # Execute the submitted query
        result = self.session_manager.execute_query(session_id, submitted_sql)

        # Check if query executed successfully
        if not result.success:
            return ChallengeSubmission(
                challenge_id=challenge.id,
                session_id=session_id,
                submitted_sql=submitted_sql,
                submitted_at=datetime.utcnow().isoformat(),
                passed=False,
                execution_time_ms=result.execution_time_ms,
                hints_used=hints_used,
                xp_earned=0,
                feedback=f"Query error: {result.error_message}",
                actual_output=None
            )

        # Validate against rules
        passed, feedback = self._validate_against_rules(result, challenge.validation_rules)

        # Calculate XP earned
        xp_earned = 0
        if passed:
            xp_earned = challenge.xp_reward - (hints_used * challenge.hint_penalty_xp)
            xp_earned = max(xp_earned, challenge.xp_reward // 4)  # Minimum 25% XP

        return ChallengeSubmission(
            challenge_id=challenge.id,
            session_id=session_id,
            submitted_sql=submitted_sql,
            submitted_at=datetime.utcnow().isoformat(),
            passed=passed,
            execution_time_ms=result.execution_time_ms,
            hints_used=hints_used,
            xp_earned=xp_earned,
            feedback=feedback,
            actual_output=result.rows
        )

    def _validate_against_rules(
        self,
        result: QueryResult,
        rules: List[ValidationRule]
    ) -> Tuple[bool, str]:
        """
        Validate query result against validation rules.

        Returns:
            Tuple of (passed, feedback_message)
        """
        for rule in rules:
            passed, feedback = self._check_rule(result, rule)
            if not passed:
                return False, feedback

        return True, "All validations passed! Great job!"

    def _check_rule(self, result: QueryResult, rule: ValidationRule) -> Tuple[bool, str]:
        """Check a single validation rule."""

        if rule.type == ValidationType.ROW_COUNT:
            expected = rule.expected_value
            actual = result.row_count
            if actual != expected:
                return False, f"Expected {expected} rows, got {actual}"
            return True, "Row count matches"

        elif rule.type == ValidationType.EXACT_MATCH:
            expected_rows = rule.expected_value
            actual_rows = result.rows

            if len(actual_rows) != len(expected_rows):
                return False, f"Expected {len(expected_rows)} rows, got {len(actual_rows)}"

            if rule.order_matters:
                for i, (expected, actual) in enumerate(zip(expected_rows, actual_rows)):
                    if not self._rows_equal(expected, actual, rule.case_sensitive):
                        return False, f"Row {i+1} doesn't match expected output"
            else:
                # Order doesn't matter - check all expected rows exist
                for expected in expected_rows:
                    found = False
                    for actual in actual_rows:
                        if self._rows_equal(expected, actual, rule.case_sensitive):
                            found = True
                            break
                    if not found:
                        return False, f"Missing expected row: {expected}"

            return True, "Output matches expected"

        elif rule.type == ValidationType.CONTAINS_ROWS:
            expected_rows = rule.expected_value
            actual_rows = result.rows

            for expected in expected_rows:
                found = False
                for actual in actual_rows:
                    if self._rows_equal(expected, actual, rule.case_sensitive):
                        found = True
                        break
                if not found:
                    return False, f"Missing required row in output"

            return True, "Contains all required rows"

        elif rule.type == ValidationType.COLUMN_CHECK:
            expected_columns = set(c.lower() for c in rule.expected_value)
            actual_columns = set(c.lower() for c in result.columns)

            if expected_columns != actual_columns:
                missing = expected_columns - actual_columns
                extra = actual_columns - expected_columns
                msg = "Column mismatch."
                if missing:
                    msg += f" Missing: {missing}."
                if extra:
                    msg += f" Unexpected: {extra}."
                return False, msg

            return True, "Columns match"

        return True, "Unknown rule type (skipped)"

    def _rows_equal(self, expected: Dict, actual: Dict, case_sensitive: bool) -> bool:
        """Check if two rows are equal."""
        # Normalize keys to lowercase
        expected_norm = {k.lower(): v for k, v in expected.items()}
        actual_norm = {k.lower(): v for k, v in actual.items()}

        if set(expected_norm.keys()) != set(actual_norm.keys()):
            return False

        for key in expected_norm:
            exp_val = expected_norm[key]
            act_val = actual_norm.get(key)

            # Handle string comparison
            if isinstance(exp_val, str) and isinstance(act_val, str):
                if not case_sensitive:
                    exp_val = exp_val.lower()
                    act_val = act_val.lower()

            # Handle numeric comparison with tolerance
            if isinstance(exp_val, float) and isinstance(act_val, float):
                if abs(exp_val - act_val) > 0.0001:
                    return False
            elif exp_val != act_val:
                return False

        return True

    def get_user_progress(self, user_id: str) -> UserProgress:
        """Get or create user progress."""
        if user_id not in self._user_progress:
            self._user_progress[user_id] = UserProgress(user_id=user_id)
        return self._user_progress[user_id]

    def update_progress(self, user_id: str, submission: ChallengeSubmission):
        """Update user progress based on submission."""
        progress = self.get_user_progress(user_id)

        if submission.passed and submission.challenge_id not in progress.completed_challenges:
            progress.completed_challenges.append(submission.challenge_id)
            progress.total_xp += submission.xp_earned
            progress.current_level = self._calculate_level(progress.total_xp)

            # Update streak
            today = datetime.utcnow().date().isoformat()
            if progress.last_activity_date:
                last_date = progress.last_activity_date
                if last_date != today:
                    # Check if consecutive day
                    # Simple check - just increment for now
                    progress.current_streak += 1
            else:
                progress.current_streak = 1

            progress.last_activity_date = today
            progress.longest_streak = max(progress.longest_streak, progress.current_streak)

            # Check for new badges
            self._check_badges(progress)

        progress.hints_used += submission.hints_used

    def _calculate_level(self, xp: int) -> int:
        """Calculate level from XP."""
        level = 1
        for level_def in LEVELS:
            if xp >= level_def.xp_required:
                level = level_def.level
        return level

    def _check_badges(self, progress: UserProgress):
        """Check and award any earned badges."""
        for badge in BADGES:
            if badge.id in progress.earned_badges:
                continue

            earned = False

            if badge.criteria_type == "challenge_count":
                earned = len(progress.completed_challenges) >= badge.criteria_value

            elif badge.criteria_type == "streak":
                earned = progress.current_streak >= badge.criteria_value

            elif badge.criteria_type == "query_count":
                earned = progress.total_queries_executed >= badge.criteria_value

            if earned:
                progress.earned_badges.append(badge.id)
                progress.total_xp += badge.xp_bonus


# Global challenge engine instance
_challenge_engine: Optional[ChallengeEngine] = None


def get_challenge_engine() -> ChallengeEngine:
    """Get the global challenge engine instance."""
    global _challenge_engine
    if _challenge_engine is None:
        _challenge_engine = ChallengeEngine()
    return _challenge_engine
