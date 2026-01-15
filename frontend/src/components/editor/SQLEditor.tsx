import Editor, { OnMount } from '@monaco-editor/react';
import { useRef, useCallback } from 'react';
import type { editor } from 'monaco-editor';

interface SQLEditorProps {
  value: string;
  onChange: (value: string) => void;
  onRun: () => void;
  isExecuting?: boolean;
}

export default function SQLEditor({ value, onChange, onRun, isExecuting }: SQLEditorProps) {
  const editorRef = useRef<editor.IStandaloneCodeEditor | null>(null);

  const handleEditorMount: OnMount = useCallback((editor, monaco) => {
    editorRef.current = editor;

    // Add keyboard shortcut for running query
    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter, () => {
      onRun();
    });

    // Configure SQL language
    monaco.languages.registerCompletionItemProvider('sql', {
      provideCompletionItems: () => {
        const suggestions = [
          // Keywords
          ...['SELECT', 'FROM', 'WHERE', 'INSERT', 'INTO', 'VALUES', 'UPDATE', 'SET',
             'DELETE', 'CREATE', 'TABLE', 'DROP', 'ALTER', 'INDEX', 'JOIN', 'INNER',
             'LEFT', 'RIGHT', 'OUTER', 'FULL', 'CROSS', 'ON', 'AND', 'OR', 'NOT',
             'NULL', 'IS', 'IN', 'BETWEEN', 'LIKE', 'ORDER', 'BY', 'ASC', 'DESC',
             'GROUP', 'HAVING', 'LIMIT', 'OFFSET', 'AS', 'DISTINCT', 'COUNT', 'SUM',
             'AVG', 'MIN', 'MAX', 'PRIMARY', 'KEY', 'INTEGER', 'TEXT', 'REAL', 'BLOB'
          ].map(keyword => ({
            label: keyword,
            kind: monaco.languages.CompletionItemKind.Keyword,
            insertText: keyword,
            detail: 'SQL Keyword',
          })),
        ];

        return { suggestions };
      },
    });

    // Focus editor
    editor.focus();
  }, [onRun]);

  return (
    <div className="h-full flex flex-col bg-vscode-bg">
      {/* Toolbar */}
      <div className="flex items-center justify-between px-3 py-2 bg-vscode-sidebar border-b border-vscode-border">
        <span className="text-xs text-vscode-text-dim uppercase">SQL Query</span>
        <div className="flex items-center gap-2">
          <button
            onClick={onRun}
            disabled={isExecuting}
            className={`flex items-center gap-1.5 px-3 py-1 rounded text-sm transition-colors ${
              isExecuting
                ? 'bg-vscode-border text-vscode-text-dim cursor-not-allowed'
                : 'bg-vscode-accent hover:bg-vscode-accent-hover text-white'
            }`}
          >
            {isExecuting ? (
              <>
                <span className="animate-spin">⏳</span>
                Running...
              </>
            ) : (
              <>
                <span>▶</span>
                Run (Ctrl+Enter)
              </>
            )}
          </button>
        </div>
      </div>

      {/* Editor */}
      <div className="flex-1">
        <Editor
          height="100%"
          defaultLanguage="sql"
          theme="vs-dark"
          value={value}
          onChange={(v) => onChange(v || '')}
          onMount={handleEditorMount}
          options={{
            minimap: { enabled: false },
            fontSize: 14,
            fontFamily: 'Consolas, Monaco, "Courier New", monospace',
            lineNumbers: 'on',
            roundedSelection: false,
            scrollBeyondLastLine: false,
            automaticLayout: true,
            tabSize: 2,
            wordWrap: 'on',
            padding: { top: 10 },
            suggestOnTriggerCharacters: true,
            quickSuggestions: true,
          }}
        />
      </div>
    </div>
  );
}
