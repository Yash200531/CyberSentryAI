import { User, ScanResult, ThreatLevel } from '../types';

// Keys
const SCANS_KEY = 'cybersentry_scans';
const AVATAR_KEY = 'cybersentry_avatars';

// Mock Data Initialization
const initStorage = () => {
  if (!localStorage.getItem(SCANS_KEY)) {
    localStorage.setItem(SCANS_KEY, JSON.stringify([]));
  }
  if (!localStorage.getItem(AVATAR_KEY)) {
    localStorage.setItem(AVATAR_KEY, JSON.stringify({}));
  }
};

initStorage();

// Profile Image Update (local cache)
export const updateUserAvatar = async (
  userId: string,
  base64Image: string
): Promise<Partial<User> | null> => {
  await new Promise(resolve => setTimeout(resolve, 500));

  const avatarMap = JSON.parse(localStorage.getItem(AVATAR_KEY) || '{}');
  avatarMap[userId] = base64Image;
  localStorage.setItem(AVATAR_KEY, JSON.stringify(avatarMap));

  return { id: userId, avatarUrl: base64Image };
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