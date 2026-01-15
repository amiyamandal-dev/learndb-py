import { useEffect } from 'react';
import { Routes, Route } from 'react-router-dom';
import { useSessionStore } from './store/sessionStore';
import Layout from './components/layout/Layout';
import SandboxPage from './pages/SandboxPage';
import ChallengeListPage from './pages/ChallengeListPage';
import ChallengePage from './pages/ChallengePage';

function App() {
  const { createSession, sessionId, isLoading, error } = useSessionStore();

  useEffect(() => {
    if (!sessionId && !isLoading) {
      createSession();
    }
  }, [sessionId, isLoading, createSession]);

  if (isLoading && !sessionId) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-vscode-bg">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-vscode-accent mx-auto mb-4"></div>
          <p className="text-vscode-text">Initializing LearnDB...</p>
        </div>
      </div>
    );
  }

  if (error && !sessionId) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-vscode-bg">
        <div className="text-center p-8 bg-vscode-sidebar rounded-lg border border-vscode-error">
          <h2 className="text-xl text-vscode-error mb-2">Connection Error</h2>
          <p className="text-vscode-text-dim mb-4">{error}</p>
          <button
            onClick={() => createSession()}
            className="btn-primary"
          >
            Retry Connection
          </button>
        </div>
      </div>
    );
  }

  return (
    <Layout>
      <Routes>
        <Route path="/" element={<SandboxPage />} />
        <Route path="/sandbox" element={<SandboxPage />} />
        <Route path="/challenges" element={<ChallengeListPage />} />
        <Route path="/challenges/:id" element={<ChallengePage />} />
      </Routes>
    </Layout>
  );
}

export default App;
