"""Pydantic schemas for database schema-related API endpoints."""

from typing import List, Optional
from pydantic import BaseModel


class ColumnSchema(BaseModel):
    """Schema information for a single column."""
    name: str
    datatype: str
    is_primary_key: bool
    is_nullable: bool


class TableSchema(BaseModel):
    """Schema information for a table."""
    name: str
    sql_text: str
    columns: List[ColumnSchema] = []


class SchemaResponse(BaseModel):
    """Response containing all table schemas."""
    tables: List[TableSchema]


class TablePreviewResponse(BaseModel):
    """Response containing table preview data."""
    table_name: str
    columns: List[str]
    rows: List[dict]
    row_count: int
    success: bool
    error_message: Optional[str] = None
