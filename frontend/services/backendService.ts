import { ScanType, ScanResult, ThreatLevel, RedTeamReport, CyberDNA } from '../types';

const TEXT_API_URL = import.meta.env.VITE_TEXT_API_URL || 'http://localhost:5000';
const URL_API_URL = import.meta.env.VITE_URL_API_URL || 'http://localhost:5001';
const IMAGE_API_URL = import.meta.env.VITE_IMAGE_API_URL || 'http://localhost:5003';

type ScanBuilderInput = {
  type: ScanType;
  userId: string;
  contentSnippet: string;
  riskScore: number;
  threatLevel: ThreatLevel;
  redTeamReport: RedTeamReport;
  cyberDNA: CyberDNA;
};

const clamp = (value: number, min = 0, max = 100) => Math.min(Math.max(value, min), max);

const toRiskScore = (confidence: number | undefined) => {
  if (confidence === undefined || Number.isNaN(confidence)) return 0;
  return clamp(confidence > 1 ? confidence : confidence * 100);
};

const generateId = () =>
  typeof crypto !== 'undefined' && crypto.randomUUID
    ? crypto.randomUUID()
    : `scan-${Date.now()}-${Math.random().toString(16).slice(2, 8)}`;

const createFingerprint = (input: string) => {
  let hash = 0;
  for (let i = 0; i < input.length; i += 1) {
    hash = (hash << 5) - hash + input.charCodeAt(i);
    hash |= 0;
  }
  return Math.abs(hash).toString(16).padStart(12, '0');
};

const normalizeThreatLevel = (
  riskLabel: string | undefined,
  isThreat: boolean,
  riskScore: number
): ThreatLevel => {
  const label = (riskLabel || '').toLowerCase();
  if (!isThreat && riskScore < 35) return ThreatLevel.SAFE;
  if (label.includes('critical')) return ThreatLevel.CRITICAL;
  if (label.includes('high')) return ThreatLevel.MALICIOUS;
  if (label.includes('medium')) return ThreatLevel.SUSPICIOUS;
  if (label.includes('low')) return isThreat ? ThreatLevel.SUSPICIOUS : ThreatLevel.SAFE;
  if (!isThreat) return ThreatLevel.SAFE;
  if (riskScore >= 85) return ThreatLevel.CRITICAL;
  if (riskScore >= 60) return ThreatLevel.MALICIOUS;
  return ThreatLevel.SUSPICIOUS;
};

const ensureExplanations = (raw: unknown): string[] => {
  if (Array.isArray(raw)) {
    const cleaned = raw.filter(Boolean).map(value => String(value));
    return cleaned.length ? cleaned : ['No explanation provided'];
  }
  if (typeof raw === 'string' && raw.trim()) return [raw.trim()];
  return ['No explanation provided'];
};

const buildRedTeamReport = ({
  type,
  explanations,
  isThreat,
  riskScore,
}: {
  type: ScanType;
  explanations: string[];
  isThreat: boolean;
  riskScore: number;
}): RedTeamReport => {
  const attackGoalMap: Record<ScanType, string> = {
    [ScanType.TEXT]: 'Social engineering / credential theft',
    [ScanType.EMAIL]: 'Business email compromise',
    [ScanType.URL]: 'Malicious landing page redirection',
    [ScanType.IMAGE]: 'Visual spoofing / forged artifacts',
  };

  const victimProfileMap: Record<ScanType, string> = {
    [ScanType.TEXT]: 'Messaging or chat recipient',
    [ScanType.EMAIL]: 'Corporate email user',
    [ScanType.URL]: 'End user browsing a suspicious domain',
    [ScanType.IMAGE]: 'User verifying visual evidence',
  };

  const primaryInsight = explanations[0] || 'No specific tactic detected';

  return {
    attackGoal: isThreat ? attackGoalMap[type] : 'Benign communication',
    victimProfile: victimProfileMap[type],
    psychologyExploited: isThreat ? primaryInsight : 'No social engineering patterns detected',
    exploitationChain: explanations,
    nextMoves: isThreat
      ? 'Isolate channel, alert SOC, and educate the impacted user'
      : 'Log scan and continue monitoring',
    confidenceScore: clamp(isThreat ? Math.max(riskScore, 60) : Math.min(riskScore, 40)),
  };
};

const buildCyberDNA = ({
  content = '',
  type,
  explanations,
  isThreat,
  riskScore,
  fingerprintSource,
}: {
  content?: string;
  type: ScanType;
  explanations: string[];
  isThreat: boolean;
  riskScore: number;
  fingerprintSource?: string;
}): CyberDNA => {
  const urgencyPattern = /(urgent|immediately|act now|expire|today|limited)/i;
  const impersonationPattern = /(account|bank|upi|paytm|sbi|icici|government|amazon|google|verify|security)/i;
  const obfuscationPattern = /(https?:\/|bit\.ly|tinyurl|@|login|secure|verify)/i;
  const riskyTldPattern = /\.(zip|xyz|ru|cn|top|tk|gq|ml|info|click)(?:\/|$)/i;

  const base = isThreat ? 70 : 25;
  const toScore = (condition: boolean, emphasis = 20) => clamp(base + (condition ? emphasis : -10), 5, 95);

  let urgency = type === ScanType.IMAGE ? 35 : toScore(urgencyPattern.test(content));
  let impersonation = toScore(impersonationPattern.test(content));
  let obfuscation = toScore(obfuscationPattern.test(content));
  let visual = type === ScanType.IMAGE ? clamp(riskScore, 30, 95) : clamp(base - 5, 15, 80);

  if (type === ScanType.URL) {
    const httpsMissing = !content.startsWith('https://');
    const manyDots = (content.match(/\./g) || []).length > 3;
    urgency = toScore(false, 10);
    impersonation = toScore(/login|secure|account|bank|verify/i.test(content));
    obfuscation = clamp(base + (httpsMissing ? 25 : 0) + (manyDots ? 15 : 0) + (riskyTldPattern.test(content) ? 20 : 0), 5, 95);
    visual = clamp(base, 10, 55);
  }

  if (type === ScanType.IMAGE) {
    impersonation = clamp(base + 15, 10, 95);
    obfuscation = clamp(base, 5, 70);
  }

  const fingerprint = createFingerprint(
    fingerprintSource || content || explanations.join('|') || new Date().toISOString()
  );

  return {
    linguistics: clamp(base + explanations.length * 3, 10, 95),
    urgency,
    impersonation,
    obfuscation,
    visual,
    intent: clamp(isThreat ? Math.max(riskScore, base + 10) : Math.min(riskScore / 2, 40)),
    fingerprintHash: fingerprint,
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
}: ScanBuilderInput): ScanResult => ({
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

const formatSnippet = (text: string, fallback: string) => {
  const cleaned = text?.trim();
  if (!cleaned) return fallback;
  return cleaned.length > 140 ? `${cleaned.slice(0, 140)}...` : cleaned;
};

const analyzeTextOrEmail = async (
  type: ScanType.TEXT | ScanType.EMAIL,
  content: string,
  userId: string
): Promise<ScanResult> => {
  const response = await fetch(`${TEXT_API_URL}/detect-text`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text: content }),
  });

  if (!response.ok) {
    throw new Error(`Text analyzer error: ${response.status}`);
  }

  const data = await response.json();
  const riskScore = toRiskScore(data.confidence);
  const explanations = ensureExplanations(data.explanation);
  const threatLevel = normalizeThreatLevel(data.risk_level, Boolean(data.is_scam), riskScore);

  return buildScanResult({
    type,
    userId,
    contentSnippet: formatSnippet(content, type === ScanType.EMAIL ? 'Email submission' : 'Text submission'),
    riskScore,
    threatLevel,
    redTeamReport: buildRedTeamReport({ type, explanations, isThreat: Boolean(data.is_scam), riskScore }),
    cyberDNA: buildCyberDNA({
      content,
      type,
      explanations,
      isThreat: Boolean(data.is_scam),
      riskScore,
    }),
  });
};

const analyzeUrl = async (url: string, userId: string): Promise<ScanResult> => {
  const response = await fetch(`${URL_API_URL}/detect-url`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url }),
  });

  if (!response.ok) {
    throw new Error(`URL analyzer error: ${response.status}`);
  }

  const data = await response.json();
  const riskScore = toRiskScore(data.confidence);
  const explanations = ensureExplanations(data.explanation);
  const threatLevel = normalizeThreatLevel(data.risk_level, Boolean(data.is_phishing), riskScore);

  return buildScanResult({
    type: ScanType.URL,
    userId,
    contentSnippet: url,
    riskScore,
    threatLevel,
    redTeamReport: buildRedTeamReport({
      type: ScanType.URL,
      explanations,
      isThreat: Boolean(data.is_phishing),
      riskScore,
    }),
    cyberDNA: buildCyberDNA({
      content: url,
      type: ScanType.URL,
      explanations,
      isThreat: Boolean(data.is_phishing),
      riskScore,
    }),
  });
};

const analyzeImage = async (imageData: string | undefined, userId: string): Promise<ScanResult> => {
  if (!imageData) {
    throw new Error('Image data missing for analysis');
  }

  const base64Payload = imageData.includes(',') ? imageData.split(',')[1] : imageData;
  if (!base64Payload) {
    throw new Error('Unable to read uploaded image');
  }

  const response = await fetch(`${IMAGE_API_URL}/detect-image`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ image_base64: base64Payload }),
  });

  if (!response.ok) {
    throw new Error(`Image analyzer error: ${response.status}`);
  }

  const data = await response.json();
  const riskScore = toRiskScore(data.confidence);
  const isThreat = Boolean(data.is_fake);

  const explanations = ensureExplanations(
    data.hf_primary?.label
      ? `Model detected pattern: ${data.hf_primary.label}`
      : data.risk_level || (isThreat ? 'Possible forgery detected' : 'No visual anomalies detected')
  );

  const threatLevel = normalizeThreatLevel(data.risk_level, isThreat, riskScore);

  return buildScanResult({
    type: ScanType.IMAGE,
    userId,
    contentSnippet: 'Uploaded forensic artifact',
    riskScore,
    threatLevel,
    redTeamReport: buildRedTeamReport({
      type: ScanType.IMAGE,
      explanations,
      isThreat,
      riskScore,
    }),
    cyberDNA: buildCyberDNA({
      content: '',
      type: ScanType.IMAGE,
      explanations,
      isThreat,
      riskScore,
      fingerprintSource: data.image_id || data.reference || JSON.stringify(data),
    }),
  });
};

export const analyzeContent = async (
  type: ScanType,
  content: string,
  userId: string,
  imageData?: string
): Promise<ScanResult> => {
  switch (type) {
    case ScanType.TEXT:
      return analyzeTextOrEmail(ScanType.TEXT, content, userId);
    case ScanType.EMAIL:
      return analyzeTextOrEmail(ScanType.EMAIL, content, userId);
    case ScanType.URL:
      return analyzeUrl(content, userId);
    case ScanType.IMAGE:
      return analyzeImage(imageData, userId);
    default:
      throw new Error(`Unsupported scan type: ${type}`);
  }
};
