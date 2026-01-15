"""Schema browsing API routes."""

from fastapi import APIRouter, HTTPException, Depends

from backend.core.session_manager import SessionManager, get_session_manager
from backend.schemas.schema import (
    ColumnSchema,
    TableSchema,
    SchemaResponse,
    TablePreviewResponse,
)

router = APIRouter(prefix="/sessions/{session_id}/schema", tags=["schema"])


def get_manager() -> SessionManager:
    """Dependency to get session manager."""
    return get_session_manager()


@router.get("", response_model=SchemaResponse)
async def get_all_schemas(
    session_id: str,
    manager: SessionManager = Depends(get_manager)
):
    """Get all table schemas in the session's database."""
    session = manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found")

    tables = manager.get_tables(session_id)

    return SchemaResponse(
        tables=[
            TableSchema(
                name=t.name,
                sql_text=t.sql_text,
                columns=[
                    ColumnSchema(
                        name=c.name,
                        datatype=c.datatype,
                        is_primary_key=c.is_primary_key,
                        is_nullable=c.is_nullable
                    )
                    for c in t.columns
                ]
            )
            for t in tables
        ]
    )


@router.get("/{table_name}", response_model=TableSchema)
async def get_table_schema(
    session_id: str,
    table_name: str,
    manager: SessionManager = Depends(get_manager)
):
    """Get schema for a specific table."""
    session = manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found")

    table = manager.get_table_schema(session_id, table_name)
    if not table:
        raise HTTPException(status_code=404, detail=f"Table '{table_name}' not found")

    return TableSchema(
        name=table.name,
        sql_text=table.sql_text,
        columns=[
            ColumnSchema(
                name=c.name,
                datatype=c.datatype,
                is_primary_key=c.is_primary_key,
                is_nullable=c.is_nullable
            )
            for c in table.columns
        ]
    )


@router.get("/{table_name}/preview", response_model=TablePreviewResponse)
async def get_table_preview(
    session_id: str,
    table_name: str,
    limit: int = 10,
    manager: SessionManager = Depends(get_manager)
):
    """Get preview data for a table (first N rows)."""
    session = manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found")

    result = manager.get_table_preview(session_id, table_name, limit)

    return TablePreviewResponse(
        table_name=table_name,
        columns=result.columns,
        rows=result.rows,
        row_count=result.row_count,
        success=result.success,
        error_message=result.error_message
    )
