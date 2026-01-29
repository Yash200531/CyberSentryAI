import { GoogleGenAI, Type } from "@google/genai";
import { ScanType, ScanResult, ThreatLevel, RedTeamReport, CyberDNA } from '../types';

const API_KEY = process.env.API_KEY || ''; 

const ai = new GoogleGenAI({ apiKey: API_KEY });

const SYSTEM_INSTRUCTION = `
You are CyberSentry, an advanced offensive security AI (Red Team) and cyber forensics engine.
Your job is to analyze content (text, emails, URLs, images) and determine if it is malicious.
You must think like an attacker to explain the "why" and "how".

CRITICAL: You must generate a "Cyber DNA" fingerprint based on 6 distinct axes (0-100):
1. Linguistics: Persuasive, coercive, or manipulative language patterns.
2. Urgency: Artificial time constraints or fear inducement.
3. Impersonation: Mimicry of brands, authority figures, or trusted entities.
4. Obfuscation: Technical hiding, encoding, weird domains, hidden scripts.
5. Visual: Deceptive layout, fake buttons, visual artifacts (relevant for images/emails).
6. Intent: Severity of the goal (e.g. 100 for Ransomware/Cred harvesting, 20 for Spam).

Output MUST be strictly valid JSON matching the schema provided.
`;

export const analyzeContent = async (
  type: ScanType,
  content: string,
  userId: string,
  imageData?: string // Base64 for images
): Promise<ScanResult> => {

  const model = 'gemini-3-pro-preview'; 

  let prompt = `Analyze this ${type}:\n\n`;
  
  if (type === ScanType.TEXT || type === ScanType.EMAIL || type === ScanType.URL) {
    prompt += content;
  } else if (type === ScanType.IMAGE) {
    prompt += "Analyze the visual content of this image for signs of phishing, scams, or malicious intent.";
  }

  const parts: any[] = [{ text: prompt }];
  if (imageData) {
    parts.push({
      inlineData: {
        mimeType: 'image/png',
        data: imageData.split(',')[1]
      }
    });
  }

  try {
    const response = await ai.models.generateContent({
      model: model,
      contents: { parts: parts },
      config: {
        systemInstruction: SYSTEM_INSTRUCTION,
        responseMimeType: "application/json",
        responseSchema: {
          type: Type.OBJECT,
          properties: {
            riskScore: { type: Type.NUMBER, description: "0 to 100 risk score" },
            threatLevel: { type: Type.STRING, enum: ["SAFE", "SUSPICIOUS", "MALICIOUS", "CRITICAL"] },
            redTeamReport: {
              type: Type.OBJECT,
              properties: {
                attackGoal: { type: Type.STRING },
                victimProfile: { type: Type.STRING },
                psychologyExploited: { type: Type.STRING },
                exploitationChain: { type: Type.ARRAY, items: { type: Type.STRING } },
                nextMoves: { type: Type.STRING },
                confidenceScore: { type: Type.NUMBER },
              }
            },
            cyberDNA: {
              type: Type.OBJECT,
              properties: {
                linguistics: { type: Type.NUMBER, description: "0-100" },
                urgency: { type: Type.NUMBER, description: "0-100" },
                impersonation: { type: Type.NUMBER, description: "0-100" },
                obfuscation: { type: Type.NUMBER, description: "0-100" },
                visual: { type: Type.NUMBER, description: "0-100" },
                intent: { type: Type.NUMBER, description: "0-100" },
                fingerprintHash: { type: Type.STRING },
                similarCampaigns: { type: Type.ARRAY, items: { type: Type.STRING } }
              }
            }
          }
        }
      }
    });

    const resultText = response.text || "{}";
    const analysis = JSON.parse(resultText);

    // Ensure DNA values are numbers (fallback logic)
    const dna = analysis.cyberDNA || {};
    const safeDNA: CyberDNA = {
      linguistics: dna.linguistics || 0,
      urgency: dna.urgency || 0,
      impersonation: dna.impersonation || 0,
      obfuscation: dna.obfuscation || 0,
      visual: dna.visual || 0,
      intent: dna.intent || 0,
      fingerprintHash: dna.fingerprintHash || "UNKNOWN",
      similarCampaigns: dna.similarCampaigns || []
    };

    const scanResult: ScanResult = {
      id: crypto.randomUUID(),
      userId,
      timestamp: new Date().toISOString(),
      type,
      contentSnippet: type === ScanType.IMAGE ? "Image Upload" : content.substring(0, 100) + "...",
      riskScore: analysis.riskScore || 0,
      threatLevel: analysis.threatLevel as ThreatLevel,
      redTeamReport: analysis.redTeamReport,
      cyberDNA: safeDNA,
      status: 'completed'
    };

    return scanResult;

  } catch (error) {
    console.error("Gemini Analysis Error:", error);
    return {
      id: crypto.randomUUID(),
      userId,
      timestamp: new Date().toISOString(),
      type,
      contentSnippet: "Analysis Failed",
      riskScore: 0,
      threatLevel: ThreatLevel.SAFE,
      redTeamReport: {
        attackGoal: "Unknown",
        victimProfile: "Unknown",
        psychologyExploited: "Unknown",
        exploitationChain: ["Analysis failed due to API error"],
        nextMoves: "None",
        confidenceScore: 0
      },
      cyberDNA: {
        linguistics: 0,
        urgency: 0,
        impersonation: 0,
        obfuscation: 0,
        visual: 0,
        intent: 0,
        fingerprintHash: "000000",
        similarCampaigns: []
      },
      status: 'failed'
    };
  }
};
