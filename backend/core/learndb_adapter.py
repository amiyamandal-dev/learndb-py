"""
LearnDB Adapter - Wraps the LearnDB interface for web API usage.

This provides a clean interface for executing SQL queries and
extracting schema/metadata from LearnDB instances.
"""

import sys
import os
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

# Add the parent directory to path so we can import learndb
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from learndb.interface import LearnDB
from learndb.dataexchange import Response


@dataclass
class QueryResult:
    """Result of a query execution."""
    success: bool
    rows: List[Dict[str, Any]] = field(default_factory=list)
    columns: List[str] = field(default_factory=list)
    row_count: int = 0
    error_message: Optional[str] = None
    execution_time_ms: float = 0.0


@dataclass
class ColumnInfo:
    """Information about a table column."""
    name: str
    datatype: str
    is_primary_key: bool
    is_nullable: bool


@dataclass
class TableInfo:
    """Information about a database table."""
    name: str
    sql_text: str
    columns: List[ColumnInfo] = field(default_factory=list)


class LearnDBAdapter:
    """
    Adapter class that wraps LearnDB for web API usage.

    Provides methods for:
    - Executing SQL queries and returning structured results
    - Getting schema information
    - Resetting the database
    """

    def __init__(self, db_filepath: str, nuke_db_file: bool = False):
        """
        Initialize the LearnDB adapter.

        Args:
            db_filepath: Path to the database file
            nuke_db_file: If True, delete existing db file on init
        """
        self.db_filepath = db_filepath
        self._db = LearnDB(db_filepath, nuke_db_file=nuke_db_file)

    def execute_query(self, sql: str) -> QueryResult:
        """
        Execute a SQL query and return structured results.

        Args:
            sql: SQL statement to execute

        Returns:
            QueryResult with success status, rows, and metadata
        """
        start_time = time.time()

        try:
            # Execute the query
            response = self._db.handle_input(sql)
            execution_time = (time.time() - start_time) * 1000

            if not response.success:
                return QueryResult(
                    success=False,
                    error_message=response.error_message,
                    execution_time_ms=execution_time
                )

            # Collect results from the pipe
            rows = []
            columns = []
            pipe = self._db.get_pipe()

            while pipe.has_msgs():
                record = pipe.read()
                # Convert record to dictionary
                if hasattr(record, 'to_dict'):
                    row_dict = record.to_dict()
                elif hasattr(record, 'values'):
                    row_dict = dict(record.values)
                else:
                    # Handle string output (like from meta commands)
                    row_dict = {"result": str(record)}

                # Extract column names from first row
                if not columns and row_dict:
                    columns = list(row_dict.keys())

                rows.append(row_dict)

            return QueryResult(
                success=True,
                rows=rows,
                columns=columns,
                row_count=len(rows),
                execution_time_ms=execution_time
            )

        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            return QueryResult(
                success=False,
                error_message=str(e),
                execution_time_ms=execution_time
            )

    def get_tables(self) -> List[TableInfo]:
        """
        Get list of all tables with their schemas.

        Returns:
            List of TableInfo objects
        """
        tables = []

        # Query the catalog to get table information
        result = self.execute_query("SELECT name, sql_text FROM catalog")

        if not result.success:
            return tables

        for row in result.rows:
            table_name = row.get('name', '')
            sql_text = row.get('sql_text', '')

            # Skip the catalog table itself in the list
            if table_name.lower() == 'catalog':
                continue

            # Get column information for this table
            columns = self._get_table_columns(table_name)

            tables.append(TableInfo(
                name=table_name,
                sql_text=sql_text,
                columns=columns
            ))

        return tables

    def _get_table_columns(self, table_name: str) -> List[ColumnInfo]:
        """
        Get column information for a specific table.

        Args:
            table_name: Name of the table

        Returns:
            List of ColumnInfo objects
        """
        columns = []

        try:
            # Access the state manager to get schema
            if self._db.virtual_machine and self._db.virtual_machine.state_manager:
                state_manager = self._db.virtual_machine.state_manager
                if state_manager.has_schema(table_name):
                    schema = state_manager.get_schema(table_name)
                    for col in schema.columns:
                        columns.append(ColumnInfo(
                            name=col.name,
                            datatype=col.datatype.typename if hasattr(col.datatype, 'typename') else str(col.datatype),
                            is_primary_key=col.is_primary_key,
                            is_nullable=col.is_nullable
                        ))
        except Exception:
            # If we can't get schema info, return empty list
            pass

        return columns

    def get_table_schema(self, table_name: str) -> Optional[TableInfo]:
        """
        Get schema information for a specific table.

        Args:
            table_name: Name of the table

        Returns:
            TableInfo or None if table doesn't exist
        """
        # First check if table exists
        result = self.execute_query(f"SELECT sql_text FROM catalog WHERE name = '{table_name}'")

        if not result.success or result.row_count == 0:
            return None

        sql_text = result.rows[0].get('sql_text', '') if result.rows else ''
        columns = self._get_table_columns(table_name)

        return TableInfo(
            name=table_name,
            sql_text=sql_text,
            columns=columns
        )

    def get_table_preview(self, table_name: str, limit: int = 10) -> QueryResult:
        """
        Get a preview of table data (first N rows).

        Args:
            table_name: Name of the table
            limit: Maximum number of rows to return

        Returns:
            QueryResult with preview data
        """
        # First get the columns for this table
        columns = self._get_table_columns(table_name)

        if not columns:
            return QueryResult(
                success=False,
                error_message=f"Table '{table_name}' not found or has no columns"
            )

        # Build SELECT query with all columns
        column_names = ", ".join([col.name for col in columns])
        sql = f"SELECT {column_names} FROM {table_name} LIMIT {limit}"

        return self.execute_query(sql)

    def execute_multi(self, sql_statements: List[str]) -> List[QueryResult]:
        """
        Execute multiple SQL statements sequentially.

        Args:
            sql_statements: List of SQL statements

        Returns:
            List of QueryResult objects
        """
        results = []
        for sql in sql_statements:
            sql = sql.strip()
            if sql:
                results.append(self.execute_query(sql))
        return results

    def reset(self):
        """Reset the database to a clean state."""
        self._db.nuke_dbfile()

    def close(self):
        """Close the database connection."""
        self._db.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False
