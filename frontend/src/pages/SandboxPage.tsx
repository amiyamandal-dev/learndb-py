import { useState, useCallback } from 'react';
import { useSessionStore } from '../store/sessionStore';
import SQLEditor from '../components/editor/SQLEditor';
import ResultsPanel from '../components/results/ResultsPanel';

export default function SandboxPage() {
  const {
    currentQuery,
    setCurrentQuery,
    executeQuery,
    lastResult,
    isExecuting,
    queryHistory,
  } = useSessionStore();

  const [showHistory, setShowHistory] = useState(false);

  const handleRun = useCallback(async () => {
    if (currentQuery.trim()) {
      await executeQuery(currentQuery);
    }
  }, [currentQuery, executeQuery]);

  const handleLoadFromHistory = useCallback((sql: string) => {
    setCurrentQuery(sql);
    setShowHistory(false);
  }, [setCurrentQuery]);

  return (
    <div className="h-full flex flex-col">
      {/* Split panels */}
      <div className="flex-1 flex flex-col min-h-0">
        {/* Editor panel (top) */}
        <div className="h-1/2 min-h-[200px] border-b border-vscode-border">
          <SQLEditor
            value={currentQuery}
            onChange={setCurrentQuery}
            onRun={handleRun}
            isExecuting={isExecuting}
          />
        </div>

        {/* Results panel (bottom) */}
        <div className="h-1/2 min-h-[200px] flex">
          <div className="flex-1">
            <ResultsPanel result={lastResult} isExecuting={isExecuting} />
          </div>

          {/* History sidebar */}
          {showHistory && (
            <div className="w-72 border-l border-vscode-border bg-vscode-sidebar">
              <div className="p-3 border-b border-vscode-border flex items-center justify-between">
                <span className="text-xs uppercase text-vscode-text-dim">Query History</span>
                <button
                  onClick={() => setShowHistory(false)}
                  className="text-vscode-text-dim hover:text-vscode-text"
                >
                  ✕
                </button>
              </div>
              <div className="overflow-y-auto max-h-[calc(100%-40px)]">
                {queryHistory.length === 0 ? (
                  <p className="p-4 text-sm text-vscode-text-dim">No queries yet</p>
                ) : (
                  queryHistory.map((item, i) => (
                    <button
                      key={i}
                      onClick={() => handleLoadFromHistory(item.sql)}
                      className="w-full text-left p-3 border-b border-vscode-border hover:bg-vscode-border"
                    >
                      <div className="flex items-center gap-2 mb-1">
                        <span className={item.success ? 'text-vscode-success' : 'text-vscode-error'}>
                          {item.success ? '✓' : '✗'}
                        </span>
                        <span className="text-xs text-vscode-text-dim">
                          {new Date(item.timestamp).toLocaleTimeString()}
                        </span>
                      </div>
                      <pre className="text-xs text-vscode-text truncate">
                        {item.sql.substring(0, 100)}
                      </pre>
                    </button>
                  ))
                )}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Bottom toolbar */}
      <div className="h-8 bg-vscode-sidebar border-t border-vscode-border flex items-center px-3 text-xs">
        <button
          onClick={() => setShowHistory(!showHistory)}
          className={`px-2 py-1 rounded ${
            showHistory ? 'bg-vscode-accent text-white' : 'text-vscode-text-dim hover:text-vscode-text'
          }`}
        >
          📜 History ({queryHistory.length})
        </button>

        <div className="ml-auto flex items-center gap-4 text-vscode-text-dim">
          {lastResult && (
            <>
              <span>{lastResult.rowCount} rows</span>
              <span>{lastResult.executionTimeMs.toFixed(2)}ms</span>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
