import { create } from 'zustand';
import { sessionApi, schemaApi } from '../api/client';

export interface QueryResult {
  success: boolean;
  rows: Record<string, unknown>[];
  columns: string[];
  rowCount: number;
  errorMessage: string | null;
  executionTimeMs: number;
}

export interface Column {
  name: string;
  datatype: string;
  is_primary_key: boolean;
  is_nullable: boolean;
}

export interface Table {
  name: string;
  sql_text: string;
  columns: Column[];
}

export interface QueryHistoryItem {
  sql: string;
  timestamp: string;
  success: boolean;
  executionTimeMs: number;
  rowCount: number;
}

interface SessionState {
  sessionId: string | null;
  isLoading: boolean;
  error: string | null;

  // Query state
  currentQuery: string;
  lastResult: QueryResult | null;
  isExecuting: boolean;
  queryHistory: QueryHistoryItem[];

  // Schema state
  tables: Table[];

  // Actions
  createSession: () => Promise<void>;
  executeQuery: (sql: string) => Promise<QueryResult | null>;
  setCurrentQuery: (sql: string) => void;
  refreshSchema: () => Promise<void>;
  resetDatabase: () => Promise<void>;
}

export const useSessionStore = create<SessionState>((set, get) => ({
  sessionId: null,
  isLoading: false,
  error: null,
  currentQuery: '-- Write your SQL here\n',
  lastResult: null,
  isExecuting: false,
  queryHistory: [],
  tables: [],

  createSession: async () => {
    set({ isLoading: true, error: null });
    try {
      const response = await sessionApi.create();
      const sessionId = response.data.session_id;
      set({ sessionId, isLoading: false });

      // Load schema after creating session
      await get().refreshSchema();
    } catch (err) {
      set({
        error: err instanceof Error ? err.message : 'Failed to create session',
        isLoading: false
      });
    }
  },

  executeQuery: async (sql: string) => {
    const { sessionId } = get();
    if (!sessionId) return null;

    set({ isExecuting: true, error: null });
    try {
      const response = await sessionApi.query(sessionId, sql);
      const result: QueryResult = {
        success: response.data.success,
        rows: response.data.rows,
        columns: response.data.columns,
        rowCount: response.data.row_count,
        errorMessage: response.data.error_message,
        executionTimeMs: response.data.execution_time_ms,
      };

      // Add to history
      const historyItem: QueryHistoryItem = {
        sql,
        timestamp: new Date().toISOString(),
        success: result.success,
        executionTimeMs: result.executionTimeMs,
        rowCount: result.rowCount,
      };

      set(state => ({
        lastResult: result,
        isExecuting: false,
        queryHistory: [historyItem, ...state.queryHistory].slice(0, 50),
      }));

      // Refresh schema if it was a DDL command
      const lowerSql = sql.toLowerCase().trim();
      if (lowerSql.startsWith('create') || lowerSql.startsWith('drop')) {
        await get().refreshSchema();
      }

      return result;
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Query execution failed';
      set({
        error: errorMsg,
        isExecuting: false,
        lastResult: {
          success: false,
          rows: [],
          columns: [],
          rowCount: 0,
          errorMessage: errorMsg,
          executionTimeMs: 0,
        }
      });
      return null;
    }
  },

  setCurrentQuery: (sql: string) => {
    set({ currentQuery: sql });
  },

  refreshSchema: async () => {
    const { sessionId } = get();
    if (!sessionId) return;

    try {
      const response = await schemaApi.getAll(sessionId);
      set({ tables: response.data.tables });
    } catch (err) {
      console.error('Failed to refresh schema:', err);
    }
  },

  resetDatabase: async () => {
    const { sessionId } = get();
    if (!sessionId) return;

    try {
      await sessionApi.reset(sessionId);
      set({
        tables: [],
        lastResult: null,
        queryHistory: [],
      });
    } catch (err) {
      set({ error: err instanceof Error ? err.message : 'Failed to reset database' });
    }
  },
}));
