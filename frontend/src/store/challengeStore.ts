import { create } from 'zustand';
import { challengeApi } from '../api/client';

export interface ChallengeListItem {
  id: string;
  title: string;
  difficulty: string;
  xp_reward: number;
  completed?: boolean;
}

export interface Category {
  name: string;
  display_name: string;
  challenges: ChallengeListItem[];
}

export interface ChallengeDetail {
  id: string;
  title: string;
  description: string;
  difficulty: string;
  xp_reward: number;
  category: string;
  estimated_time_minutes: number;
  hints_count: number;
  prerequisites: string[];
}

export interface SubmissionResult {
  success: boolean;
  passed: boolean;
  feedback: string;
  xp_earned: number;
  execution_time_ms: number;
  actual_output?: Record<string, unknown>[];
}

interface ChallengeState {
  categories: Category[];
  currentChallenge: ChallengeDetail | null;
  isLoading: boolean;
  error: string | null;

  // Current attempt state
  hintsUsed: number;
  revealedHints: string[];
  lastSubmission: SubmissionResult | null;
  isSubmitting: boolean;

  // User progress
  completedChallenges: Set<string>;
  totalXp: number;

  // Actions
  loadChallenges: () => Promise<void>;
  loadChallenge: (id: string) => Promise<void>;
  setupChallenge: (sessionId: string) => Promise<boolean>;
  submitSolution: (sessionId: string, sql: string) => Promise<SubmissionResult | null>;
  revealHint: () => Promise<string | null>;
  resetAttempt: () => void;
}

export const useChallengeStore = create<ChallengeState>((set, get) => ({
  categories: [],
  currentChallenge: null,
  isLoading: false,
  error: null,
  hintsUsed: 0,
  revealedHints: [],
  lastSubmission: null,
  isSubmitting: false,
  completedChallenges: new Set(),
  totalXp: 0,

  loadChallenges: async () => {
    set({ isLoading: true, error: null });
    try {
      const response = await challengeApi.list();
      set({
        categories: response.data.categories,
        isLoading: false,
      });
    } catch (err) {
      set({
        error: err instanceof Error ? err.message : 'Failed to load challenges',
        isLoading: false,
      });
    }
  },

  loadChallenge: async (id: string) => {
    set({ isLoading: true, error: null, currentChallenge: null });
    try {
      const response = await challengeApi.get(id);
      set({
        currentChallenge: response.data,
        isLoading: false,
        hintsUsed: 0,
        revealedHints: [],
        lastSubmission: null,
      });
    } catch (err) {
      set({
        error: err instanceof Error ? err.message : 'Failed to load challenge',
        isLoading: false,
      });
    }
  },

  setupChallenge: async (sessionId: string) => {
    const { currentChallenge } = get();
    if (!currentChallenge) return false;

    try {
      await challengeApi.setup(currentChallenge.id, sessionId);
      return true;
    } catch (err) {
      set({ error: err instanceof Error ? err.message : 'Failed to setup challenge' });
      return false;
    }
  },

  submitSolution: async (sessionId: string, sql: string) => {
    const { currentChallenge, hintsUsed } = get();
    if (!currentChallenge) return null;

    set({ isSubmitting: true, error: null });
    try {
      const response = await challengeApi.submit(
        currentChallenge.id,
        sessionId,
        sql,
        hintsUsed
      );

      const result: SubmissionResult = response.data;
      set({ lastSubmission: result, isSubmitting: false });

      // Update completed challenges and XP
      if (result.passed) {
        set(state => ({
          completedChallenges: new Set([...state.completedChallenges, currentChallenge.id]),
          totalXp: state.totalXp + result.xp_earned,
        }));
      }

      return result;
    } catch (err) {
      set({
        error: err instanceof Error ? err.message : 'Submission failed',
        isSubmitting: false,
      });
      return null;
    }
  },

  revealHint: async () => {
    const { currentChallenge, hintsUsed } = get();
    if (!currentChallenge || hintsUsed >= currentChallenge.hints_count) {
      return null;
    }

    try {
      const response = await challengeApi.getHint(currentChallenge.id, hintsUsed);
      const hint = response.data.hint;

      set(state => ({
        hintsUsed: state.hintsUsed + 1,
        revealedHints: [...state.revealedHints, hint],
      }));

      return hint;
    } catch (err) {
      set({ error: err instanceof Error ? err.message : 'Failed to get hint' });
      return null;
    }
  },

  resetAttempt: () => {
    set({
      hintsUsed: 0,
      revealedHints: [],
      lastSubmission: null,
    });
  },
}));
