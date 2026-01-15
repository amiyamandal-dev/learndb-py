import { useState } from 'react';
import { useSessionStore } from '../../store/sessionStore';

export default function Sidebar() {
  const { tables, refreshSchema, resetDatabase } = useSessionStore();
  const [expandedTables, setExpandedTables] = useState<Set<string>>(new Set());

  const toggleTable = (tableName: string) => {
    setExpandedTables(prev => {
      const next = new Set(prev);
      if (next.has(tableName)) {
        next.delete(tableName);
      } else {
        next.add(tableName);
      }
      return next;
    });
  };

  return (
    <aside className="w-64 bg-vscode-sidebar border-r border-vscode-border flex flex-col">
      {/* Header */}
      <div className="p-3 border-b border-vscode-border flex items-center justify-between">
        <span className="text-xs uppercase text-vscode-text-dim font-semibold">
          Schema Explorer
        </span>
        <div className="flex gap-1">
          <button
            onClick={() => refreshSchema()}
            className="p-1 hover:bg-vscode-border rounded text-vscode-text-dim hover:text-vscode-text"
            title="Refresh schema"
          >
            ↻
          </button>
          <button
            onClick={() => {
              if (confirm('Reset database? This will delete all tables and data.')) {
                resetDatabase();
              }
            }}
            className="p-1 hover:bg-vscode-border rounded text-vscode-text-dim hover:text-vscode-error"
            title="Reset database"
          >
            ⟲
          </button>
        </div>
      </div>

      {/* Tables list */}
      <div className="flex-1 overflow-y-auto p-2">
        {tables.length === 0 ? (
          <div className="text-center py-8 text-vscode-text-dim text-sm">
            <p>No tables yet</p>
            <p className="mt-2 text-xs">Create a table using:</p>
            <code className="block mt-1 text-xs bg-vscode-bg p-2 rounded">
              CREATE TABLE ...
            </code>
          </div>
        ) : (
          <div className="space-y-1">
            {tables.map(table => (
              <div key={table.name}>
                <button
                  onClick={() => toggleTable(table.name)}
                  className="w-full flex items-center gap-2 px-2 py-1 rounded hover:bg-vscode-border text-left"
                >
                  <span className="text-vscode-text-dim">
                    {expandedTables.has(table.name) ? '▼' : '▶'}
                  </span>
                  <span className="text-vscode-accent">⊞</span>
                  <span className="text-sm text-vscode-text">{table.name}</span>
                </button>

                {expandedTables.has(table.name) && (
                  <div className="ml-6 mt-1 space-y-0.5">
                    {table.columns.map(col => (
                      <div
                        key={col.name}
                        className="flex items-center gap-2 px-2 py-0.5 text-xs"
                      >
                        <span className={col.is_primary_key ? 'text-vscode-warning' : 'text-vscode-text-dim'}>
                          {col.is_primary_key ? '🔑' : '○'}
                        </span>
                        <span className="text-vscode-text">{col.name}</span>
                        <span className="text-vscode-text-dim ml-auto">
                          {col.datatype}
                        </span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Footer with tips */}
      <div className="p-3 border-t border-vscode-border text-xs text-vscode-text-dim">
        <p className="mb-1">💡 Tip:</p>
        <p>Press <kbd className="px-1 bg-vscode-bg rounded">Ctrl+Enter</kbd> to run query</p>
      </div>
    </aside>
  );
}
