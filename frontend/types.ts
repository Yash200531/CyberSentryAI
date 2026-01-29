export enum UserRole {
  ADMIN = 'admin',
  ANALYST = 'analyst',
  USER = 'user',
}

export interface User {
  id: number | string;
  email: string;
  roles?: string[]; // JWT roles
  scopes?: string[]; // JWT scopes
  role?: UserRole; // legacy single-role consumers
  username?: string;
  avatarUrl?: string;
}

export enum ScanType {
  TEXT = 'TEXT',
  URL = 'URL',
  IMAGE = 'IMAGE',
  EMAIL = 'EMAIL',
}

export enum ThreatLevel {
  SAFE = 'SAFE',
  SUSPICIOUS = 'SUSPICIOUS',
  MALICIOUS = 'MALICIOUS',
  CRITICAL = 'CRITICAL',
}

export interface RedTeamReport {
  attackGoal: string;
  victimProfile: string;
  psychologyExploited: string;
  exploitationChain: string[];
  nextMoves: string;
  confidenceScore: number;
}

export interface CyberDNA {
  linguistics: number; // 0-100: Manipulation via language
  urgency: number; // 0-100: Time pressure/fear
  impersonation: number; // 0-100: Brand/Authority mimicry
  obfuscation: number; // 0-100: Hidden scripts, encoding, weird URLs
  visual: number; // 0-100: Visual deception (for images) or structural tricks
  intent: number; // 0-100: Malicious severity (credential theft vs spam)
  fingerprintHash: string; // Hex string identifying this pattern
  similarCampaigns: string[];
}

export interface ScanResult {
  id: string;
  userId: string;
  timestamp: string;
  type: ScanType;
  contentSnippet: string;
  riskScore: number; // 0-100
  threatLevel: ThreatLevel;
  redTeamReport: RedTeamReport;
  cyberDNA: CyberDNA;
  status: 'pending' | 'completed' | 'failed';
}

export interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}
