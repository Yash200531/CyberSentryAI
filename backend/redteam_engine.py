"""
Red-Team AI Engine
Analyzes scam/phishing content from an attacker's perspective
Uses Hugging Face Inference API for reasoning
"""
import json
import os
import urllib.error
import urllib.request
from typing import Dict, Any, Optional
from datetime import datetime


class RedTeamEngine:
    """
    Red-Team analysis using attacker-thinking AI
    Provides psychological, intent, and exploitation chain analysis
    """
    
    def __init__(self):
        self.api_token = os.getenv("HF_API_TOKEN")
        # Use fast instruction-tuned model for reasoning
        self.model = os.getenv("HF_REDTEAM_MODEL", "HuggingFaceH4/zephyr-7b-beta")
        self.api_url = f"https://api-inference.huggingface.co/models/{self.model}"
        self.timeout = float(os.getenv("HF_TIMEOUT", "30"))
        self.max_tokens = 500
        
    def _call_hf_inference(self, prompt: str) -> Optional[str]:
        """Call Hugging Face Inference API with prompt"""
        if not self.api_token:
            return None
            
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": self.max_tokens,
                "temperature": 0.3,
                "top_p": 0.9,
                "do_sample": True,
                "return_full_text": False
            }
        }
        
        req = urllib.request.Request(
            self.api_url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json",
            },
        )
        
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                
            if isinstance(data, list) and len(data) > 0:
                return data[0].get("generated_text", "")
            elif isinstance(data, dict):
                if "error" in data:
                    return None
                return data.get("generated_text", "")
                
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, ValueError) as e:
            print(f"HF API Error: {e}")
            return None
            
        return None
    
    def analyze_text(self, text: str, scan_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze text/email content from attacker perspective
        
        Args:
            text: Original message content
            scan_result: Results from primary detection (is_scam, score, etc.)
            
        Returns:
            Red-team analysis with attack goal, victim profile, exploitation chain
        """
        confidence = scan_result.get("score", 0) * 100
        is_threat = confidence >= 30
        
        if not is_threat:
            # Not a significant threat, return minimal analysis
            return self._minimal_analysis("low_threat")
        
        prompt = self._build_text_prompt(text, confidence)
        response = self._call_hf_inference(prompt)
        
        if response:
            parsed = self._parse_redteam_response(response)
            parsed["timestamp"] = datetime.utcnow().isoformat()
            parsed["model_used"] = self.model
            return parsed
        else:
            # Fallback to rule-based analysis
            return self._fallback_text_analysis(text, confidence)
    
    def analyze_url(self, url: str, scan_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze URL from attacker perspective
        
        Args:
            url: Target URL
            scan_result: Results from URL detection
            
        Returns:
            Red-team analysis
        """
        confidence = scan_result.get("score", 0) * 100
        is_threat = confidence >= 30
        
        if not is_threat:
            return self._minimal_analysis("low_threat")
        
        prompt = self._build_url_prompt(url, confidence)
        response = self._call_hf_inference(prompt)
        
        if response:
            parsed = self._parse_redteam_response(response)
            parsed["timestamp"] = datetime.utcnow().isoformat()
            parsed["model_used"] = self.model
            return parsed
        else:
            return self._fallback_url_analysis(url, confidence)
    
    def analyze_image(self, image_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze image/deepfake from attacker perspective
        
        Args:
            image_result: Results from image detection
            
        Returns:
            Red-team analysis
        """
        confidence = image_result.get("score", 0) * 100
        is_threat = confidence >= 30
        
        if not is_threat:
            return self._minimal_analysis("low_threat")
        
        prompt = self._build_image_prompt(image_result, confidence)
        response = self._call_hf_inference(prompt)
        
        if response:
            parsed = self._parse_redteam_response(response)
            parsed["timestamp"] = datetime.utcnow().isoformat()
            parsed["model_used"] = self.model
            return parsed
        else:
            return self._fallback_image_analysis(image_result, confidence)
    
    def _build_text_prompt(self, text: str, confidence: float) -> str:
        """Build prompt for text/email analysis"""
        return f"""You are a cybersecurity analyst. Analyze this suspicious message (confidence: {confidence:.0f}%) from an attacker's perspective. Be concise and factual.

Message: "{text[:500]}"

Provide ONLY a JSON response with these exact fields:
- attack_goal: Primary objective (data theft, financial scam, credential phishing, etc.)
- victim_profile: Target demographic (elderly, business users, general public, etc.)
- psychological_tactics: List of manipulation techniques used (urgency, authority, fear, greed, etc.)
- exploitation_chain: Step-by-step attack sequence
- next_step: Likely attacker's next move
- severity: Number 1-10
- confidence_score: Number 0-100

JSON:"""
    
    def _build_url_prompt(self, url: str, confidence: float) -> str:
        """Build prompt for URL analysis"""
        return f"""You are a cybersecurity analyst. Analyze this suspicious URL (confidence: {confidence:.0f}%) from an attacker's perspective. Be concise and factual.

URL: {url}

Provide ONLY a JSON response with these exact fields:
- attack_goal: Primary objective (credential theft, malware distribution, fake login, etc.)
- victim_profile: Target demographic
- psychological_tactics: List of manipulation techniques
- exploitation_chain: Step-by-step attack sequence
- next_step: Likely attacker's next move
- severity: Number 1-10
- confidence_score: Number 0-100

JSON:"""
    
    def _build_image_prompt(self, image_result: Dict, confidence: float) -> str:
        """Build prompt for image analysis"""
        label = image_result.get("label", "unknown")
        return f"""You are a cybersecurity analyst. Analyze this suspicious image (type: {label}, confidence: {confidence:.0f}%) from an attacker's perspective. Be concise and factual.

Detection: {label}

Provide ONLY a JSON response with these exact fields:
- attack_goal: Purpose of fake/manipulated image (identity fraud, fake evidence, impersonation, etc.)
- victim_profile: Target demographic
- psychological_tactics: List of deception techniques
- exploitation_chain: How this image would be used in an attack
- next_step: Likely attacker's next move
- severity: Number 1-10
- confidence_score: Number 0-100

JSON:"""
    
    def _parse_redteam_response(self, response: str) -> Dict[str, Any]:
        """Parse and validate AI response"""
        try:
            # Extract JSON from response
            start = response.find("{")
            end = response.rfind("}") + 1
            if start >= 0 and end > start:
                json_str = response[start:end]
                parsed = json.loads(json_str)
                
                # Validate and normalize
                return {
                    "attack_goal": str(parsed.get("attack_goal", "Unknown"))[:200],
                    "victim_profile": str(parsed.get("victim_profile", "General users"))[:200],
                    "psychological_tactics": parsed.get("psychological_tactics", [])[:5],
                    "exploitation_chain": str(parsed.get("exploitation_chain", ""))[:500],
                    "next_step": str(parsed.get("next_step", "Unknown"))[:200],
                    "severity": max(1, min(10, int(parsed.get("severity", 5)))),
                    "confidence_score": max(0, min(100, float(parsed.get("confidence_score", 50))))
                }
        except (json.JSONDecodeError, ValueError, KeyError):
            pass
        
        # If parsing fails, return default
        return self._minimal_analysis("parse_failed")
    
    def _fallback_text_analysis(self, text: str, confidence: float) -> Dict[str, Any]:
        """Rule-based fallback for text analysis"""
        text_lower = text.lower()
        
        # Determine attack goal
        if any(word in text_lower for word in ["password", "login", "verify", "account"]):
            goal = "Credential theft via fake verification"
        elif any(word in text_lower for word in ["money", "prize", "won", "lottery", "$"]):
            goal = "Financial scam / advance fee fraud"
        elif any(word in text_lower for word in ["click", "link", "urgent", "suspended"]):
            goal = "Phishing link distribution"
        else:
            goal = "Social engineering / information gathering"
        
        # Detect tactics
        tactics = []
        if any(word in text_lower for word in ["urgent", "immediately", "now", "expire"]):
            tactics.append("urgency")
        if any(word in text_lower for word in ["verify", "confirm", "security"]):
            tactics.append("authority")
        if any(word in text_lower for word in ["suspended", "locked", "unauthorized"]):
            tactics.append("fear")
        if any(word in text_lower for word in ["prize", "won", "free", "congratulations"]):
            tactics.append("greed")
        
        severity = min(10, max(4, int(confidence / 10)))
        
        return {
            "attack_goal": goal,
            "victim_profile": "General public or targeted users",
            "psychological_tactics": tactics or ["deception"],
            "exploitation_chain": "Message delivery → User trust → Action (click/reply) → Data compromise",
            "next_step": "Await user response or credential submission",
            "severity": severity,
            "confidence_score": confidence,
            "timestamp": datetime.utcnow().isoformat(),
            "model_used": "rule_based_fallback"
        }
    
    def _fallback_url_analysis(self, url: str, confidence: float) -> Dict[str, Any]:
        """Rule-based fallback for URL analysis"""
        url_lower = url.lower()
        
        # Determine attack type
        if any(word in url_lower for word in ["login", "signin", "verify", "account"]):
            goal = "Credential phishing via fake login page"
        elif any(word in url_lower for word in ["download", "file", "update"]):
            goal = "Malware distribution"
        elif any(word in url_lower for word in ["bank", "payment", "paypal", "stripe"]):
            goal = "Financial credential theft"
        else:
            goal = "General phishing / data collection"
        
        tactics = ["URL spoofing", "domain mimicry"]
        if not url.startswith("https"):
            tactics.append("no encryption")
        if "@" in url or url.count("-") > 2:
            tactics.append("obfuscation")
        
        severity = min(10, max(5, int(confidence / 10)))
        
        return {
            "attack_goal": goal,
            "victim_profile": "Users seeking legitimate services",
            "psychological_tactics": tactics,
            "exploitation_chain": "Malicious URL → Fake landing page → Credential input → Data theft",
            "next_step": "Harvest credentials from fake form submissions",
            "severity": severity,
            "confidence_score": confidence,
            "timestamp": datetime.utcnow().isoformat(),
            "model_used": "rule_based_fallback"
        }
    
    def _fallback_image_analysis(self, image_result: Dict, confidence: float) -> Dict[str, Any]:
        """Rule-based fallback for image analysis"""
        label = image_result.get("label", "").lower()
        
        if "deepfake" in label or "fake" in label:
            goal = "Identity impersonation or fake evidence creation"
            chain = "Deepfake generation → Social media distribution → Trust exploitation → Financial/reputational damage"
        else:
            goal = "Visual deception for scam legitimacy"
            chain = "AI-generated content → Fake legitimacy → User trust → Scam success"
        
        severity = min(10, max(6, int(confidence / 10)))
        
        return {
            "attack_goal": goal,
            "victim_profile": "Social media users, investors, general public",
            "psychological_tactics": ["visual deception", "false authority", "authenticity illusion"],
            "exploitation_chain": chain,
            "next_step": "Distribute across platforms to build false credibility",
            "severity": severity,
            "confidence_score": confidence,
            "timestamp": datetime.utcnow().isoformat(),
            "model_used": "rule_based_fallback"
        }
    
    def _minimal_analysis(self, reason: str) -> Dict[str, Any]:
        """Return minimal analysis for low-threat content"""
        return {
            "attack_goal": "None detected",
            "victim_profile": "N/A",
            "psychological_tactics": [],
            "exploitation_chain": "No significant threat detected",
            "next_step": "N/A",
            "severity": 1,
            "confidence_score": 0,
            "timestamp": datetime.utcnow().isoformat(),
            "model_used": "minimal_analysis",
            "reason": reason
        }
