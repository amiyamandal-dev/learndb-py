"""
Session Manager - Manages isolated database sessions for each user.

Each session gets its own database file, ensuring complete isolation
between users (required since LearnDB is single-writer only).
"""

import os
import shutil
import uuid
import time
import threading
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

from .learndb_adapter import LearnDBAdapter, QueryResult


@dataclass
class QueryHistoryItem:
    """A single item in query history."""
    sql: str
    timestamp: str
    success: bool
    execution_time_ms: float
    row_count: int = 0
    error_message: Optional[str] = None


@dataclass
class Session:
    """Represents a user session with its own database."""
    session_id: str
    db_path: str
    created_at: str
    last_activity_at: str
    is_active: bool = True
    current_mode: str = "sandbox"  # sandbox, challenge, tutorial
    current_challenge_id: Optional[str] = None
    current_tutorial_id: Optional[str] = None
    query_history: List[QueryHistoryItem] = field(default_factory=list)

    # Runtime state (not serialized)
    _adapter: Optional[LearnDBAdapter] = field(default=None, repr=False)


class SessionManager:
    """
    Manages database sessions with isolation.

    Each session gets:
    - Unique session ID
    - Isolated database file in temp directory
    - Query history tracking
    - Automatic cleanup of stale sessions
    """

    def __init__(
        self,
        sessions_dir: str = "/tmp/learndb_sessions",
        max_session_age_hours: int = 24,
        max_history_items: int = 100
    ):
        """
        Initialize the session manager.

        Args:
            sessions_dir: Base directory for session database files
            max_session_age_hours: Sessions older than this are cleaned up
            max_history_items: Maximum query history items per session
        """
        self.sessions_dir = Path(sessions_dir)
        self.sessions_dir.mkdir(parents=True, exist_ok=True)

        self.max_session_age_hours = max_session_age_hours
        self.max_history_items = max_history_items

        self._sessions: Dict[str, Session] = {}
        self._lock = threading.RLock()

        # Clean up any orphaned session directories on startup
        self._cleanup_orphaned_sessions()

    def create_session(self, user_id: Optional[str] = None) -> Session:
        """
        Create a new session with an isolated database.

        Args:
            user_id: Optional user ID to associate with session

        Returns:
            New Session object
        """
        with self._lock:
            session_id = str(uuid.uuid4())
            now = datetime.utcnow().isoformat()

            # Create session directory
            session_dir = self.sessions_dir / session_id
            session_dir.mkdir(parents=True, exist_ok=True)

            db_path = str(session_dir / "db.file")

            session = Session(
                session_id=session_id,
                db_path=db_path,
                created_at=now,
                last_activity_at=now,
                is_active=True
            )

            # Initialize the adapter
            session._adapter = LearnDBAdapter(db_path, nuke_db_file=True)

            self._sessions[session_id] = session
            return session

    def get_session(self, session_id: str) -> Optional[Session]:
        """
        Get an existing session by ID.

        Args:
            session_id: The session ID

        Returns:
            Session object or None if not found
        """
        with self._lock:
            session = self._sessions.get(session_id)

            if session and session.is_active:
                # Update last activity time
                session.last_activity_at = datetime.utcnow().isoformat()

                # Ensure adapter is initialized
                if session._adapter is None:
                    session._adapter = LearnDBAdapter(session.db_path)

                return session

            return None

    def execute_query(self, session_id: str, sql: str) -> QueryResult:
        """
        Execute a query in the given session.

        Args:
            session_id: The session ID
            sql: SQL statement to execute

        Returns:
            QueryResult
        """
        session = self.get_session(session_id)
        if not session:
            return QueryResult(
                success=False,
                error_message=f"Session '{session_id}' not found"
            )

        # Execute query
        result = session._adapter.execute_query(sql)

        # Add to history
        history_item = QueryHistoryItem(
            sql=sql,
            timestamp=datetime.utcnow().isoformat(),
            success=result.success,
            execution_time_ms=result.execution_time_ms,
            row_count=result.row_count,
            error_message=result.error_message
        )
        session.query_history.append(history_item)

        # Trim history if too long
        if len(session.query_history) > self.max_history_items:
            session.query_history = session.query_history[-self.max_history_items:]

        return result

    def get_tables(self, session_id: str):
        """Get all tables in a session's database."""
        session = self.get_session(session_id)
        if not session:
            return []
        return session._adapter.get_tables()

    def get_table_schema(self, session_id: str, table_name: str):
        """Get schema for a specific table."""
        session = self.get_session(session_id)
        if not session:
            return None
        return session._adapter.get_table_schema(table_name)

    def get_table_preview(self, session_id: str, table_name: str, limit: int = 10):
        """Get preview data for a table."""
        session = self.get_session(session_id)
        if not session:
            return QueryResult(
                success=False,
                error_message=f"Session '{session_id}' not found"
            )
        return session._adapter.get_table_preview(table_name, limit)

    def reset_session(self, session_id: str) -> bool:
        """
        Reset a session's database to clean state.

        Args:
            session_id: The session ID

        Returns:
            True if successful
        """
        session = self.get_session(session_id)
        if not session:
            return False

        session._adapter.reset()
        session.query_history.clear()
        return True

    def load_preset(self, session_id: str, preset_sql: List[str]) -> List[QueryResult]:
        """
        Load a preset schema/data into a session.

        Args:
            session_id: The session ID
            preset_sql: List of SQL statements to execute

        Returns:
            List of QueryResult objects
        """
        session = self.get_session(session_id)
        if not session:
            return [QueryResult(
                success=False,
                error_message=f"Session '{session_id}' not found"
            )]

        # Reset first
        session._adapter.reset()
        session.query_history.clear()

        # Execute preset SQL
        return session._adapter.execute_multi(preset_sql)

    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session and clean up its resources.

        Args:
            session_id: The session ID

        Returns:
            True if successful
        """
        with self._lock:
            session = self._sessions.get(session_id)
            if not session:
                return False

            # Close adapter
            if session._adapter:
                try:
                    session._adapter.close()
                except Exception:
                    pass

            # Mark as inactive
            session.is_active = False
            session._adapter = None

            # Remove session directory
            session_dir = self.sessions_dir / session_id
            if session_dir.exists():
                try:
                    shutil.rmtree(session_dir)
                except Exception:
                    pass

            # Remove from sessions dict
            del self._sessions[session_id]
            return True

    def get_query_history(self, session_id: str) -> List[QueryHistoryItem]:
        """Get query history for a session."""
        session = self.get_session(session_id)
        if not session:
            return []
        return session.query_history.copy()

    def list_sessions(self) -> List[Dict]:
        """List all active sessions."""
        with self._lock:
            return [
                {
                    "session_id": s.session_id,
                    "created_at": s.created_at,
                    "last_activity_at": s.last_activity_at,
                    "current_mode": s.current_mode
                }
                for s in self._sessions.values()
                if s.is_active
            ]

    def cleanup_stale_sessions(self):
        """Remove sessions that have been inactive too long."""
        with self._lock:
            now = datetime.utcnow()
            stale_ids = []

            for session_id, session in self._sessions.items():
                last_activity = datetime.fromisoformat(session.last_activity_at)
                age_hours = (now - last_activity).total_seconds() / 3600

                if age_hours > self.max_session_age_hours:
                    stale_ids.append(session_id)

            for session_id in stale_ids:
                self.delete_session(session_id)

            return len(stale_ids)

    def _cleanup_orphaned_sessions(self):
        """Clean up session directories without active sessions."""
        if not self.sessions_dir.exists():
            return

        for item in self.sessions_dir.iterdir():
            if item.is_dir() and item.name not in self._sessions:
                try:
                    shutil.rmtree(item)
                except Exception:
                    pass


# Global session manager instance
_session_manager: Optional[SessionManager] = None


def get_session_manager() -> SessionManager:
    """Get the global session manager instance."""
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager()
    return _session_manager
