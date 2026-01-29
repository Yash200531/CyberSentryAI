import { User, ScanResult, UserRole, ScanType, ThreatLevel } from '../types';

// Keys
const USERS_KEY = 'cybersentry_users';
const SCANS_KEY = 'cybersentry_scans';
const SESSION_KEY = 'cybersentry_session';

// Mock Data Initialization
const initStorage = () => {
  if (!localStorage.getItem(USERS_KEY)) {
    const admin: User = {
      id: 'admin-1',
      username: 'ShadowAdmin',
      email: 'admin@cybersentry.ai',
      role: UserRole.ADMIN,
      avatarUrl: 'https://picsum.photos/id/2/200/200'
    };
    const user: User = {
      id: 'user-1',
      username: 'SecAnalyst',
      email: 'analyst@ji.ai',
      role: UserRole.USER,
      avatarUrl: 'https://picsum.photos/id/3/200/200'
    };
    localStorage.setItem(USERS_KEY, JSON.stringify([admin, user]));
  }
  if (!localStorage.getItem(SCANS_KEY)) {
    localStorage.setItem(SCANS_KEY, JSON.stringify([]));
  }
};

initStorage();

// User Services
export const getUsers = (): User[] => {
  return JSON.parse(localStorage.getItem(USERS_KEY) || '[]');
};

export const loginUser = async (email: string): Promise<User | null> => {
  // Simulating network delay
  await new Promise(resolve => setTimeout(resolve, 800));
  const users = getUsers();
  const user = users.find(u => u.email === email);
  if (user) {
    localStorage.setItem(SESSION_KEY, JSON.stringify(user));
    return user;
  }
  return null;
};

export const logoutUser = () => {
  localStorage.removeItem(SESSION_KEY);
};

export const getCurrentUser = (): User | null => {
  const session = localStorage.getItem(SESSION_KEY);
  return session ? JSON.parse(session) : null;
};

// Simulate Backend API for Profile Image Update
export const updateUserAvatar = async (userId: string, base64Image: string): Promise<User | null> => {
  // Simulate network latency
  await new Promise(resolve => setTimeout(resolve, 500));

  const users = getUsers();
  const userIndex = users.findIndex(u => u.id === userId);

  if (userIndex === -1) return null;

  // Update in DB
  users[userIndex].avatarUrl = base64Image;
  localStorage.setItem(USERS_KEY, JSON.stringify(users));

  // Update in Session if it's the current user
  const currentUser = getCurrentUser();
  if (currentUser && currentUser.id === userId) {
    currentUser.avatarUrl = base64Image;
    localStorage.setItem(SESSION_KEY, JSON.stringify(currentUser));
    return currentUser;
  }

  return users[userIndex];
};

// Scan Services
export const saveScan = async (scan: ScanResult): Promise<void> => {
  const scans = getScans();
  scans.unshift(scan); // Add to top
  localStorage.setItem(SCANS_KEY, JSON.stringify(scans));
};

export const getScans = (): ScanResult[] => {
  return JSON.parse(localStorage.getItem(SCANS_KEY) || '[]');
};

export const getUserScans = (userId: string): ScanResult[] => {
  return getScans().filter(s => s.userId === userId);
};

export const getStats = () => {
  const scans = getScans();
  return {
    total: scans.length,
    malicious: scans.filter(s => s.threatLevel === ThreatLevel.MALICIOUS || s.threatLevel === ThreatLevel.CRITICAL).length,
    safe: scans.filter(s => s.threatLevel === ThreatLevel.SAFE).length,
  };
};