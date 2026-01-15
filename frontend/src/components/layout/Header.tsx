import { Link, useLocation } from 'react-router-dom';
import { useChallengeStore } from '../../store/challengeStore';

export default function Header() {
  const location = useLocation();
  const { totalXp, completedChallenges } = useChallengeStore();

  const navItems = [
    { path: '/sandbox', label: 'Sandbox', icon: '>' },
    { path: '/challenges', label: 'Challenges', icon: '!' },
  ];

  const level = Math.floor(totalXp / 100) + 1;

  return (
    <header className="h-12 bg-vscode-sidebar border-b border-vscode-border flex items-center justify-between px-4">
      {/* Logo and Nav */}
      <div className="flex items-center gap-6">
        <Link to="/" className="flex items-center gap-2 text-vscode-text hover:text-white">
          <span className="text-vscode-accent font-bold">{'<>'}</span>
          <span className="font-semibold">LearnDB</span>
        </Link>

        <nav className="flex items-center gap-1">
          {navItems.map(item => (
            <Link
              key={item.path}
              to={item.path}
              className={`px-3 py-1.5 rounded text-sm transition-colors ${
                location.pathname.startsWith(item.path)
                  ? 'bg-vscode-selection text-white'
                  : 'text-vscode-text-dim hover:text-vscode-text hover:bg-vscode-border'
              }`}
            >
              <span className="text-vscode-accent mr-1">{item.icon}</span>
              {item.label}
            </Link>
          ))}
        </nav>
      </div>

      {/* User Stats */}
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2 text-sm">
          <span className="text-vscode-warning">★</span>
          <span className="text-vscode-text">{totalXp} XP</span>
        </div>
        <div className="flex items-center gap-2 text-sm">
          <span className="text-vscode-accent">Lvl {level}</span>
        </div>
        <div className="flex items-center gap-2 text-sm text-vscode-text-dim">
          <span className="text-vscode-success">✓</span>
          <span>{completedChallenges.size} completed</span>
        </div>
      </div>
    </header>
  );
}
