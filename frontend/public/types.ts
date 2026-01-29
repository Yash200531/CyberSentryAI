// Runtime-safe compatibility exports for any absolute /types.ts imports.
// Note: This file is served as-is from /types.ts in production builds.

export const UserRole = Object.freeze({
  ADMIN: "admin",
  ANALYST: "analyst",
  USER: "user",
});

export const ScanType = Object.freeze({
  TEXT: "TEXT",
  URL: "URL",
  IMAGE: "IMAGE",
  EMAIL: "EMAIL",
});

export const ThreatLevel = Object.freeze({
  SAFE: "SAFE",
  SUSPICIOUS: "SUSPICIOUS",
  MALICIOUS: "MALICIOUS",
  CRITICAL: "CRITICAL",
});
