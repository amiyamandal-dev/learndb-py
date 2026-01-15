import { useEffect, useState, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import { useChallengeStore } from '../store/challengeStore';
import { useSessionStore } from '../store/sessionStore';
import SQLEditor from '../components/editor/SQLEditor';

export default function ChallengePage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const {
    currentChallenge,
    loadChallenge,
    setupChallenge,
    submitSolution,
    revealHint,
    resetAttempt,
    isLoading,
    isSubmitting,
    lastSubmission,
    revealedHints,
    hintsUsed,
  } = useChallengeStore();

  const { sessionId, refreshSchema } = useSessionStore();

  const [sql, setSql] = useState('-- Write your solution here\n');
  const [isSettingUp, setIsSettingUp] = useState(false);

  // Load challenge
  useEffect(() => {
    if (id) {
      loadChallenge(id);
    }
  }, [id, loadChallenge]);

  // Setup challenge when loaded
  useEffect(() => {
    const setup = async () => {
      if (currentChallenge && sessionId) {
        setIsSettingUp(true);
        await setupChallenge(sessionId);
        await refreshSchema();
        setIsSettingUp(false);
      }
    };
    setup();
  }, [currentChallenge, sessionId, setupChallenge, refreshSchema]);

  const handleSubmit = useCallback(async () => {
    if (!sessionId || !sql.trim()) return;
    await submitSolution(sessionId, sql);
  }, [sessionId, sql, submitSolution]);

  const handleGetHint = useCallback(async () => {
    await revealHint();
  }, [revealHint]);

  const handleReset = useCallback(async () => {
    if (sessionId) {
      resetAttempt();
      setSql('-- Write your solution here\n');
      await setupChallenge(sessionId);
      await refreshSchema();
    }
  }, [sessionId, resetAttempt, setupChallenge, refreshSchema]);

  if (isLoading || !currentChallenge) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="animate-spin text-2xl">⏳</div>
      </div>
    );
  }

  return (
    <div className="h-full flex">
      {/* Left panel - Challenge description */}
      <div className="w-1/2 border-r border-vscode-border overflow-y-auto">
        <div className="p-6">
          {/* Header */}
          <div className="mb-6">
            <button
              onClick={() => navigate('/challenges')}
              className="text-sm text-vscode-text-dim hover:text-vscode-accent mb-4 inline-block"
            >
              ← Back to Challenges
            </button>

            <div className="flex items-start justify-between">
              <div>
                <h1 className="text-xl font-bold text-vscode-text mb-2">
                  {currentChallenge.title}
                </h1>
                <div className="flex items-center gap-3">
                  <span className={`badge badge-${currentChallenge.difficulty}`}>
                    {currentChallenge.difficulty}
                  </span>
                  <span className="text-vscode-warning text-sm">
                    ★ {currentChallenge.xp_reward} XP
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Description */}
          <div className="prose prose-invert max-w-none mb-6">
            <ReactMarkdown
              components={{
                h1: ({ children }) => <h1 className="text-xl font-bold text-vscode-text mt-4 mb-2">{children}</h1>,
                h2: ({ children }) => <h2 className="text-lg font-semibold text-vscode-text mt-4 mb-2">{children}</h2>,
                p: ({ children }) => <p className="text-vscode-text mb-3">{children}</p>,
                code: ({ children }) => (
                  <code className="bg-vscode-sidebar px-1.5 py-0.5 rounded text-vscode-accent text-sm">
                    {children}
                  </code>
                ),
                pre: ({ children }) => (
                  <pre className="bg-vscode-sidebar p-4 rounded overflow-x-auto mb-4">{children}</pre>
                ),
                ul: ({ children }) => <ul className="list-disc list-inside mb-3 text-vscode-text">{children}</ul>,
                li: ({ children }) => <li className="mb-1">{children}</li>,
                strong: ({ children }) => <strong className="text-vscode-accent font-semibold">{children}</strong>,
              }}
            >
              {currentChallenge.description}
            </ReactMarkdown>
          </div>

          {/* Hints */}
          {currentChallenge.hints_count > 0 && (
            <div className="mb-6">
              <div className="flex items-center justify-between mb-3">
                <h3 className="font-semibold text-vscode-text">Hints</h3>
                <button
                  onClick={handleGetHint}
                  disabled={hintsUsed >= currentChallenge.hints_count}
                  className={`text-sm px-3 py-1 rounded ${
                    hintsUsed >= currentChallenge.hints_count
                      ? 'bg-vscode-border text-vscode-text-dim cursor-not-allowed'
                      : 'bg-vscode-accent hover:bg-vscode-accent-hover text-white'
                  }`}
                >
                  Get Hint ({currentChallenge.hints_count - hintsUsed} left)
                </button>
              </div>

              {revealedHints.length > 0 && (
                <div className="space-y-2">
                  {revealedHints.map((hint, i) => (
                    <div key={i} className="p-3 bg-vscode-sidebar rounded border border-vscode-border">
                      <span className="text-vscode-warning mr-2">💡</span>
                      <span className="text-sm text-vscode-text">{hint}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Submission result */}
          {lastSubmission && (
            <div className={`p-4 rounded border ${
              lastSubmission.passed
                ? 'bg-green-900/20 border-green-700'
                : 'bg-red-900/20 border-red-700'
            }`}>
              <div className="flex items-center gap-2 mb-2">
                <span className={lastSubmission.passed ? 'text-vscode-success' : 'text-vscode-error'}>
                  {lastSubmission.passed ? '✓ Passed!' : '✗ Not quite right'}
                </span>
                {lastSubmission.passed && (
                  <span className="text-vscode-warning">+{lastSubmission.xp_earned} XP</span>
                )}
              </div>
              <p className="text-sm text-vscode-text">{lastSubmission.feedback}</p>

              {lastSubmission.passed && (
                <button
                  onClick={() => navigate('/challenges')}
                  className="mt-4 btn-primary"
                >
                  Continue to Next Challenge →
                </button>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Right panel - Code editor */}
      <div className="w-1/2 flex flex-col">
        {isSettingUp ? (
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center">
              <div className="animate-spin text-2xl mb-2">⏳</div>
              <p className="text-vscode-text-dim">Setting up challenge...</p>
            </div>
          </div>
        ) : (
          <>
            <div className="flex-1">
              <SQLEditor
                value={sql}
                onChange={setSql}
                onRun={handleSubmit}
                isExecuting={isSubmitting}
              />
            </div>

            {/* Action bar */}
            <div className="p-3 bg-vscode-sidebar border-t border-vscode-border flex items-center justify-between">
              <button
                onClick={handleReset}
                className="text-sm text-vscode-text-dim hover:text-vscode-text"
              >
                ↻ Reset
              </button>

              <button
                onClick={handleSubmit}
                disabled={isSubmitting}
                className={`px-4 py-2 rounded font-medium ${
                  isSubmitting
                    ? 'bg-vscode-border text-vscode-text-dim cursor-not-allowed'
                    : 'bg-vscode-success hover:bg-green-600 text-white'
                }`}
              >
                {isSubmitting ? 'Checking...' : 'Submit Solution'}
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
