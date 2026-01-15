"""Session management API routes."""

from fastapi import APIRouter, HTTPException, Depends

from backend.core.session_manager import SessionManager, get_session_manager
from backend.schemas.session import (
    SessionCreate,
    SessionResponse,
    SessionListResponse,
    QueryRequest,
    QueryResponse,
    QueryHistoryResponse,
    QueryHistoryItem,
)

router = APIRouter(prefix="/sessions", tags=["sessions"])


def get_manager() -> SessionManager:
    """Dependency to get session manager."""
    return get_session_manager()


@router.post("", response_model=SessionResponse)
async def create_session(
    request: SessionCreate = None,
    manager: SessionManager = Depends(get_manager)
):
    """Create a new isolated database session."""
    user_id = request.user_id if request else None
    session = manager.create_session(user_id)

    return SessionResponse(
        session_id=session.session_id,
        created_at=session.created_at,
        last_activity_at=session.last_activity_at,
        current_mode=session.current_mode
    )


@router.get("", response_model=SessionListResponse)
async def list_sessions(manager: SessionManager = Depends(get_manager)):
    """List all active sessions."""
    sessions = manager.list_sessions()
    return SessionListResponse(
        sessions=[
            SessionResponse(
                session_id=s["session_id"],
                created_at=s["created_at"],
                last_activity_at=s["last_activity_at"],
                current_mode=s["current_mode"]
            )
            for s in sessions
        ]
    )


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: str,
    manager: SessionManager = Depends(get_manager)
):
    """Get session status and metadata."""
    session = manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found")

    return SessionResponse(
        session_id=session.session_id,
        created_at=session.created_at,
        last_activity_at=session.last_activity_at,
        current_mode=session.current_mode
    )


@router.delete("/{session_id}")
async def delete_session(
    session_id: str,
    manager: SessionManager = Depends(get_manager)
):
    """Delete a session and clean up resources."""
    success = manager.delete_session(session_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found")

    return {"status": "deleted", "session_id": session_id}


@router.post("/{session_id}/query", response_model=QueryResponse)
async def execute_query(
    session_id: str,
    request: QueryRequest,
    manager: SessionManager = Depends(get_manager)
):
    """Execute a SQL query in the session's database."""
    session = manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found")

    result = manager.execute_query(session_id, request.sql)

    return QueryResponse(
        success=result.success,
        rows=result.rows,
        columns=result.columns,
        row_count=result.row_count,
        error_message=result.error_message,
        execution_time_ms=result.execution_time_ms
    )


@router.post("/{session_id}/reset")
async def reset_session(
    session_id: str,
    manager: SessionManager = Depends(get_manager)
):
    """Reset session database to clean state."""
    success = manager.reset_session(session_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found")

    return {"status": "reset", "session_id": session_id}


@router.get("/{session_id}/history", response_model=QueryHistoryResponse)
async def get_query_history(
    session_id: str,
    manager: SessionManager = Depends(get_manager)
):
    """Get query history for a session."""
    session = manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found")

    history = manager.get_query_history(session_id)

    return QueryHistoryResponse(
        history=[
            QueryHistoryItem(
                sql=h.sql,
                timestamp=h.timestamp,
                success=h.success,
                execution_time_ms=h.execution_time_ms,
                row_count=h.row_count,
                error_message=h.error_message
            )
            for h in history
        ]
    )
