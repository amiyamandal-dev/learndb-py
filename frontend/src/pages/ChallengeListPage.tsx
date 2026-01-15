import { useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useChallengeStore } from '../store/challengeStore';

export default function ChallengeListPage() {
  const { categories, loadChallenges, isLoading, completedChallenges, totalXp } = useChallengeStore();

  useEffect(() => {
    loadChallenges();
  }, [loadChallenges]);

  if (isLoading) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="animate-spin text-2xl">⏳</div>
      </div>
    );
  }

  const totalChallenges = categories.reduce((sum, cat) => sum + cat.challenges.length, 0);

  return (
    <div className="h-full overflow-y-auto p-6">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-vscode-text mb-2">SQL Challenges</h1>
        <p className="text-vscode-text-dim">
          Test your SQL skills with interactive challenges. Earn XP and unlock achievements!
        </p>

        {/* Progress */}
        <div className="mt-4 p-4 bg-vscode-sidebar rounded-lg border border-vscode-border">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-vscode-text-dim">Progress</span>
            <span className="text-sm text-vscode-accent">
              {completedChallenges.size} / {totalChallenges} completed
            </span>
          </div>
          <div className="h-2 bg-vscode-border rounded-full overflow-hidden">
            <div
              className="h-full bg-vscode-accent transition-all duration-500"
              style={{ width: `${(completedChallenges.size / totalChallenges) * 100}%` }}
            />
          </div>
          <div className="mt-2 text-sm text-vscode-warning">
            ★ {totalXp} XP earned
          </div>
        </div>
      </div>

      {/* Categories */}
      <div className="space-y-8">
        {categories.map(category => (
          <div key={category.name}>
            <h2 className="text-lg font-semibold text-vscode-text mb-4 flex items-center gap-2">
              <span className="text-vscode-accent">#</span>
              {category.display_name}
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {category.challenges.map(challenge => {
                const isCompleted = completedChallenges.has(challenge.id);

                return (
                  <Link
                    key={challenge.id}
                    to={`/challenges/${challenge.id}`}
                    className={`block p-4 rounded-lg border transition-all hover:border-vscode-accent ${
                      isCompleted
                        ? 'bg-green-900/20 border-green-700'
                        : 'bg-vscode-sidebar border-vscode-border'
                    }`}
                  >
                    <div className="flex items-start justify-between mb-2">
                      <h3 className="font-medium text-vscode-text">
                        {isCompleted && <span className="text-vscode-success mr-2">✓</span>}
                        {challenge.title}
                      </h3>
                      <span className={`badge badge-${challenge.difficulty}`}>
                        {challenge.difficulty}
                      </span>
                    </div>

                    <div className="flex items-center gap-4 text-sm text-vscode-text-dim">
                      <span className="text-vscode-warning">★ {challenge.xp_reward} XP</span>
                    </div>
                  </Link>
                );
              })}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
