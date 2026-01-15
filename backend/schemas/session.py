"""Pydantic schemas for session-related API endpoints."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class SessionCreate(BaseModel):
    """Request to create a new session."""
    user_id: Optional[str] = None


class SessionResponse(BaseModel):
    """Response containing session information."""
    session_id: str
    created_at: str
    last_activity_at: str
    current_mode: str = "sandbox"


class SessionListResponse(BaseModel):
    """Response containing list of sessions."""
    sessions: List[SessionResponse]


class QueryRequest(BaseModel):
    """Request to execute a SQL query."""
    sql: str = Field(..., min_length=1, description="SQL statement to execute")


class QueryResponse(BaseModel):
    """Response from query execution."""
    success: bool
    rows: List[Dict[str, Any]] = []
    columns: List[str] = []
    row_count: int = 0
    error_message: Optional[str] = None
    execution_time_ms: float = 0.0


class QueryHistoryItem(BaseModel):
    """A single query history entry."""
    sql: str
    timestamp: str
    success: bool
    execution_time_ms: float
    row_count: int = 0
    error_message: Optional[str] = None


class QueryHistoryResponse(BaseModel):
    """Response containing query history."""
    history: List[QueryHistoryItem]
