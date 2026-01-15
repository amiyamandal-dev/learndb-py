import { QueryResult } from '../../store/sessionStore';

interface ResultsPanelProps {
  result: QueryResult | null;
  isExecuting: boolean;
}

export default function ResultsPanel({ result, isExecuting }: ResultsPanelProps) {
  if (isExecuting) {
    return (
      <div className="h-full flex items-center justify-center bg-vscode-bg">
        <div className="text-center">
          <div className="animate-spin text-2xl mb-2">⏳</div>
          <p className="text-vscode-text-dim">Executing query...</p>
        </div>
      </div>
    );
  }

  if (!result) {
    return (
      <div className="h-full flex items-center justify-center bg-vscode-bg">
        <div className="text-center text-vscode-text-dim">
          <p className="text-lg mb-2">📊 Results</p>
          <p className="text-sm">Run a query to see results here</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col bg-vscode-bg">
      {/* Status bar */}
      <div className={`px-3 py-2 flex items-center justify-between border-b border-vscode-border ${
        result.success ? 'bg-vscode-sidebar' : 'bg-red-900/30'
      }`}>
        <div className="flex items-center gap-3">
          <span className={result.success ? 'text-vscode-success' : 'text-vscode-error'}>
            {result.success ? '✓' : '✗'}
          </span>
          <span className="text-sm text-vscode-text">
            {result.success
              ? `${result.rowCount} row${result.rowCount !== 1 ? 's' : ''} returned`
              : 'Query failed'}
          </span>
        </div>
        <span className="text-xs text-vscode-text-dim">
          {result.executionTimeMs.toFixed(2)} ms
        </span>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto p-2">
        {!result.success ? (
          <div className="p-4 bg-red-900/20 rounded border border-vscode-error">
            <p className="text-vscode-error font-semibold mb-2">Error</p>
            <pre className="text-sm text-vscode-text whitespace-pre-wrap">
              {result.errorMessage}
            </pre>
          </div>
        ) : result.rows.length === 0 ? (
          <div className="text-center py-8 text-vscode-text-dim">
            <p>Query executed successfully</p>
            <p className="text-sm mt-1">No rows returned</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="result-table">
              <thead>
                <tr>
                  {result.columns.map(col => (
                    <th key={col}>{col}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {result.rows.map((row, i) => (
                  <tr key={i}>
                    {result.columns.map(col => (
                      <td key={col}>
                        {formatValue(row[col])}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

function formatValue(value: unknown): string {
  if (value === null || value === undefined) {
    return 'NULL';
  }
  if (typeof value === 'object') {
    return JSON.stringify(value);
  }
  return String(value);
}
