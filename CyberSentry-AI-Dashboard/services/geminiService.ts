import { AnalysisType, Verdict, AnalysisResult } from '../types';

// MOCK SERVICE - No Real AI Integration
// This service simulates the behavior of the AI for the dashboard template.

export const analyzeContent = async (
  content: string,
  type: AnalysisType
): Promise<Omit<AnalysisResult, 'id' | 'timestamp'>> => {
  
  // 1. Simulate Network/Processing Delay to allow animations to play
  await new Promise(resolve => setTimeout(resolve, 2500));

  // 2. Simple Mock Logic for Demonstration
  // In a real app, this would be the API call. 
  // Here we just look for keywords to make the template interactive.
  
  let verdict = Verdict.SAFE;
  let score = 98;
  let reasoning = "Analysis complete. No malicious patterns, obfuscated code, or known threat signatures were detected in this content. It appears to be legitimate.";

  const lowerContent = typeof content === 'string' ? content.toLowerCase() : '';

  // Simulate SPAM detection
  if (lowerContent.includes('virus') || lowerContent.includes('free money') || lowerContent.includes('winner') || lowerContent.includes('act now')) {
    verdict = Verdict.SPAM;
    score = 12;
    reasoning = "High-risk indicators detected. The content contains keywords and patterns highly correlated with phishing campaigns and financial scams.";
  } 
  // Simulate SUSPICIOUS detection
  else if (lowerContent.includes('urgent') || lowerContent.includes('verify') || lowerContent.includes('password') || lowerContent.includes('bank')) {
    verdict = Verdict.SUSPICIOUS;
    score = 45;
    reasoning = "Potential social engineering detected. The content uses urgency and requests sensitive information, which are common traits of targeted attacks.";
  }

  // Simulate Image Analysis Randomness (since we can't actually read the image content in a mock)
  if (type === AnalysisType.IMAGE) {
    // Randomly flag images for demo purposes if "fake" or "ai" is in the filename/logic (or just random)
    const random = Math.random();
    if (random > 0.7) {
        verdict = Verdict.SUSPICIOUS;
        score = 35;
        reasoning = "Visual forensics detected anomalies in lighting and texture consistency consistent with AI-generated imagery (Deepfake).";
    } else {
        verdict = Verdict.SAFE;
        score = 92;
        reasoning = "Digital signature analysis confirms the image metadata is consistent. No visual artifacts of manipulation detected.";
    }
  }

  return {
    type,
    content: type === AnalysisType.IMAGE ? "Image File" : content,
    verdict,
    score,
    reasoning
  };
};