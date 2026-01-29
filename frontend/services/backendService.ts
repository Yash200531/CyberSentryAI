import { ScanType, ScanResult, ThreatLevel, RedTeamReport, CyberDNA } from '../types';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const clamp = (value: number, min = 0, max = 100) => Math.min(Math.max(value, min), max);

const toRiskScore = (riskScore: number | undefined) => {
  if (riskScore === undefined || isNaN(riskScore)) return 0;
  return clamp(Math.round(riskScore));
};

const generateId = () =>
  typeof crypto !== 'undefined' && crypto.randomUUID
    ? crypto.randomUUID()
    : `scan-${Date.now()}-${Math.random().toString(16).slice(2, 8)}`;

const createFingerprint = (input: string) => {
  let hash = 0;
  for (let i = 0; i < input.length; i++) {
    hash = (hash << 5) - hash + input.charCodeAt(i);
    hash |= 0;
  }
  return Math.abs(hash).toString(16).padStart(12, '0');
};

const normalizeThreatLevel = (
  _riskLabel: string | undefined,
  riskScore: number,
  content: string
): ThreatLevel => {
  const text = content.toLowerCase();
  const hasLink = /https?:\/\//.test(text) || /\bwww\./.test(text);
  const hasVerification = /verify|verification|code|otp|password|pin/.test(text);
  const hasAccountSecure = /account|secure|security/.test(text);
  const hasBankUrgent = /(bank|upi|card|payment).*(urgent|immediately|now)/.test(text);
  const impersonation = /(bank|upi|google|amazon|govt|government|irs|police)/.test(text);
  const financialAction = /(payment|pay|refund|transfer|invoice)/.test(text) && /click|tap|visit|login|verify|update/.test(text);

  const heuristicThreat =
    (hasVerification && hasLink) ||
    (hasAccountSecure && /secure/.test(text)) ||
    hasBankUrgent ||
    (impersonation && hasLink) ||
    hasVerification ||
    financialAction;

  if (riskScore >= 70) return ThreatLevel.MALICIOUS;
  if (riskScore >= 30) return ThreatLevel.SUSPICIOUS;
  if (heuristicThreat) return ThreatLevel.SUSPICIOUS;
  return ThreatLevel.SAFE;
};

const ensureExplanations = (raw: unknown): string[] => {
  if (Array.isArray(raw)) return raw.map(String);
  if (typeof raw === 'string') return [raw];
  return ['No explanation provided'];
};

const normalizeStringList = (value: unknown): string[] => {
  if (Array.isArray(value)) return value.map(String).filter(Boolean);
  if (typeof value === 'string' && value.trim()) return [value.trim()];
  return [];
};

const normalizeExploitationChain = (value: unknown): string[] => {
  if (Array.isArray(value)) return value.map(String).filter(Boolean);
  if (typeof value === 'string') {
    return value
      .split(/→|->|\n|,/)
      .map((step) => step.trim())
      .filter(Boolean);
  }
  return [];
};

const buildRedTeamExplanations = (data: any): string[] => {
  const tactics = normalizeStringList(data?.redteam_analysis?.psychological_tactics);
  const chain = normalizeExploitationChain(data?.redteam_analysis?.exploitation_chain);
  const detectionNotes = normalizeStringList(data?.detection?.explanations);
  const combined = [...tactics, ...chain];
  return combined.length ? combined : detectionNotes.length ? detectionNotes : ensureExplanations(data?.explanation);
};

const buildRedTeamReport = ({
  type,
  content,
  explanations,
  riskScore,
}: {
  type: ScanType;
  content: string;
  explanations: string[];
  riskScore: number;
}): RedTeamReport => {
  const text = content.toLowerCase();
  const hasBanking = /bank|upi|account|card|credit|debit|kyc|otp|transaction|payment|refund|wallet|netbank|ifsc/.test(text);
  const hasJobs = /job|hiring|recruit|interview|resume|offer|salary|hr|work from home|freelance/.test(text);
  const hasLogin = /login|signin|sign in|password|verify|2fa|otp|code|auth|credential|reset/.test(text);
  const hasCrypto = /crypto|bitcoin|btc|eth|wallet|airdrop|token|staking|nft/.test(text);
  const hasGov = /government|tax|irs|police|court|passport|visa|uid|aadhaar/.test(text);
  const hasDelivery = /delivery|parcel|shipment|courier|tracking|customs/.test(text);
  const hasRomance = /love|dating|relationship|urgent help|emergency|hospital/.test(text);
  const hasSupport = /support|helpdesk|account locked|suspended|security alert/.test(text);
  const hasReward = /winner|prize|free|reward|gift/.test(text);
  const hasScarcity = /limited|only today|last chance|exclusive/.test(text);
  const hasUrgency = /urgent|immediately|now|expire/.test(text);
  const hasAuthority = /government|bank|police|irs|support|security/.test(text);
  const hasFear = /suspended|locked|unauthorized|fraud/.test(text);
  const hasTrustAbuse = /verify|secure|confirm/.test(text);

  const psychology: string[] = [];
  if (hasUrgency) psychology.push('urgency');
  if (hasFear) psychology.push('fear');
  if (hasAuthority) psychology.push('authority');
  if (hasReward) psychology.push('reward');
  if (hasScarcity) psychology.push('scarcity');
  if (hasTrustAbuse) psychology.push('trust abuse');

  const victimProfile = (() => {
    if (type === ScanType.IMAGE) return 'Social media audience / public figures';
    if (hasBanking) return 'Bank users and cardholders';
    if (hasJobs) return 'Job seekers';
    if (hasCrypto) return 'Crypto users and traders';
    if (hasGov) return 'Citizens targeted by government impersonation';
    if (hasDelivery) return 'E-commerce shoppers';
    if (hasRomance) return 'Individuals targeted for emotional manipulation';
    if (hasSupport) return 'Account holders seeking support';
    if (hasLogin) return 'Online account holders';
    if (type === ScanType.EMAIL) return 'Corporate employees';
    if (type === ScanType.URL) return 'Web users';
    return 'General public';
  })();

  const attackGoal = (() => {
    if (hasLogin || hasTrustAbuse) return 'Credential theft';
    if (hasBanking || /payment|refund|transfer/.test(text)) return 'Financial fraud';
    if (type === ScanType.IMAGE) return 'Impersonation or misinformation';
    if (/download|attachment|invoice/.test(text)) return 'Malware delivery';
    return 'Impersonation / social engineering';
  })();

  const killChain = [
    'Initial lure',
    'Trust building',
    hasUrgency ? 'Urgency trigger' : 'Motivation trigger',
    hasLogin || /http/.test(text) ? 'Redirection or payload' : 'Engagement step',
    attackGoal === 'Credential theft' ? 'Credential capture' : 'Data theft or fraud',
  ];

  const psychologyExploited = psychology[0] || explanations[0] || 'trust abuse';
  const exploitationChain = explanations.length ? explanations : killChain;

  return {
    attackGoal,
    victimProfile,
    psychologyExploited,
    exploitationChain,
    nextMoves:
      riskScore > 45
        ? 'Isolate, block sender, notify SOC'
        : riskScore > 25
        ? 'Warn user and monitor'
        : 'Log and continue',
    confidenceScore: clamp(riskScore),
  };
};

const buildCyberDNA = ({
  content,
  explanations,
  riskScore,
  type,
}: {
  content: string;
  explanations: string[];
  riskScore: number;
  type: ScanType;
}): CyberDNA => {
  const text = content.toLowerCase();
  const tokens = text.match(/[\w@.-]+/g) || [];
  const wordCount = Math.max(1, tokens.length);
  const charCount = Math.max(1, text.length);

  const scamKeywordHits = (text.match(/verify|secure|bank|account|password|login|otp|code|payment|refund|urgent|prize|winner|click/gi) || []).length;
  const linguistics = clamp((scamKeywordHits / wordCount) * 200);

  const urgencyHits = (text.match(/urgent|immediately|expire|now/gi) || []).length;
  const urgency = clamp((urgencyHits / wordCount) * 300);

  const impersonationHits = (text.match(/bank|google|amazon|govt|government|upi/gi) || []).length;
  const impersonation = clamp((impersonationHits / wordCount) * 300);

  const shortenerHits = (text.match(/bit\.ly|tinyurl|t\.co|goo\.gl/gi) || []).length;
  const dotHits = (text.match(/\./g) || []).length;
  const suspiciousTldHits = (text.match(/\.(ru|cn|tk|ml|ga|cf|gq|top|xyz)(\b|\/)/gi) || []).length;
  const obfuscationSignals = shortenerHits * 3 + suspiciousTldHits * 2 + dotHits / Math.max(10, charCount);
  const obfuscation = clamp((obfuscationSignals / Math.max(3, wordCount)) * 100);

  const intent = clamp(riskScore);
  const visual = type === ScanType.IMAGE ? clamp(riskScore) : 0;

  return {
    linguistics,
    urgency,
    impersonation,
    obfuscation,
    visual,
    intent,
    fingerprintHash: createFingerprint(content + explanations.join('|')),
    similarCampaigns: [],
  };
};

const buildScanResult = ({
  type,
  userId,
  contentSnippet,
  riskScore,
  threatLevel,
  redTeamReport,
  cyberDNA,
}: any): ScanResult => ({
  id: generateId(),
  userId,
  timestamp: new Date().toISOString(),
  type,
  contentSnippet,
  riskScore,
  threatLevel,
  redTeamReport,
  cyberDNA,
  status: 'completed',
});

const analyzeText = async (content: string, userId: string): Promise<ScanResult> => {
  const response = await fetch(`${API_BASE}/scan/text`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text: content }),
  });

  const data = await response.json();
  const detection = data?.detection ?? data;
  const riskScore = toRiskScore(detection?.risk_score ?? data?.risk_score);
  const explanations = buildRedTeamExplanations(data);
  const threatLevel = normalizeThreatLevel(detection?.label ?? data?.label, riskScore, content);

  return buildScanResult({
    type: ScanType.TEXT,
    userId,
    contentSnippet: content,
    riskScore,
    threatLevel,
    redTeamReport: buildRedTeamReport({
      type: ScanType.TEXT,
      content,
      explanations,
      riskScore,
    }),
    cyberDNA: buildCyberDNA({
      content,
      explanations,
      riskScore,
      type: ScanType.TEXT,
    }),
  });
};

const analyzeUrl = async (url: string, userId: string): Promise<ScanResult> => {
  const response = await fetch(`${API_BASE}/scan/url`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url }),
  });

  const data = await response.json();
  const detection = data?.detection ?? data;
  const riskScore = toRiskScore(detection?.risk_score ?? data?.risk_score);
  const explanations = buildRedTeamExplanations(data);
  const threatLevel = normalizeThreatLevel(detection?.label ?? data?.label, riskScore, url);

  return buildScanResult({
    type: ScanType.URL,
    userId,
    contentSnippet: url,
    riskScore,
    threatLevel,
    redTeamReport: buildRedTeamReport({
      type: ScanType.URL,
      content: url,
      explanations,
      riskScore,
    }),
    cyberDNA: buildCyberDNA({
      content: url,
      explanations,
      riskScore,
      type: ScanType.URL,
    }),
  });
};

const stripDataUrl = (dataUrl: string): string => {
  const match = dataUrl.match(/^data:.*?;base64,(.*)$/i);
  return match ? match[1] : dataUrl;
};

const analyzeImage = async (imageDataUrl: string, userId: string): Promise<ScanResult> => {
  const image_base64 = stripDataUrl(imageDataUrl);

  const response = await fetch(`${API_BASE}/scan/image`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ image_base64 }),
  });

  const data = await response.json();
  const detection = data?.detection ?? data;
  const riskScore = toRiskScore(detection?.risk_score ?? data?.risk_score);
  const explanations = buildRedTeamExplanations(data);
  const threatLevel = normalizeThreatLevel(detection?.label ?? data?.label, riskScore, 'image');

  return buildScanResult({
    type: ScanType.IMAGE,
    userId,
    contentSnippet: 'Image scan',
    riskScore,
    threatLevel,
    redTeamReport: buildRedTeamReport({
      type: ScanType.IMAGE,
      content: 'image',
      explanations,
      riskScore,
    }),
    cyberDNA: buildCyberDNA({
      content: 'image',
      explanations,
      riskScore,
      type: ScanType.IMAGE,
    }),
  });
};

export const analyzeContent = async (
  type: ScanType,
  content: string,
  userId: string
): Promise<ScanResult> => {
  if (type === ScanType.TEXT) return analyzeText(content, userId);
  if (type === ScanType.URL) return analyzeUrl(content, userId);
  if (type === ScanType.IMAGE) return analyzeImage(content, userId);
  throw new Error('Unsupported type');
};
