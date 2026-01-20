export enum AnalysisType {
  TEXT = 'TEXT',
  LINK = 'LINK',
  IMAGE = 'IMAGE'
}

export enum Verdict {
  SAFE = 'SAFE',
  SPAM = 'SPAM',
  SUSPICIOUS = 'SUSPICIOUS',
  UNKNOWN = 'UNKNOWN'
}

export interface User {
  id: string;
  username: string;
  email: string;
  avatarUrl?: string;
  joinedDate: string;
}

export interface AnalysisResult {
  id: string;
  timestamp: number;
  type: AnalysisType;
  content: string;
  verdict: Verdict;
  score: number; // 0 to 100 safety score
  reasoning: string;
}

export interface AppState {
  user: User | null;
  history: AnalysisResult[];
  theme: 'light' | 'dark';
}