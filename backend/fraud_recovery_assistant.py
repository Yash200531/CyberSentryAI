"""
Agentic AI Fraud-Recovery Assistant
Provides personalized recovery guidance and action plans for fraud/phishing victims
Uses Hugging Face Inference API for intelligent recommendations
"""
import json
import os
import urllib.error
import urllib.request
from typing import Dict, Any, List, Optional
from datetime import datetime
import hashlib


class FraudRecoveryAssistant:
    """
    AI-powered fraud recovery assistant that provides:
    - Step-by-step recovery plans
    - Personalized recommendations based on threat type
    - Progress tracking
    - Report generation for authorities
    """
    
    def __init__(self):
        self.api_token = os.getenv("HF_API_TOKEN")
        # Use instruction-tuned model for generating recovery advice
        self.model = os.getenv("HF_REDTEAM_MODEL", "HuggingFaceH4/zephyr-7b-beta")
        self.api_url = f"https://api-inference.huggingface.co/models/{self.model}"
        self.timeout = float(os.getenv("HF_TIMEOUT", "30"))
        self.max_tokens = 800
        
        # Recovery action templates by threat type
        self.recovery_templates = {
            "phishing": [
                "Change passwords immediately for affected accounts",
                "Enable two-factor authentication (2FA) on all accounts",
                "Contact your bank/financial institution to report the incident",
                "Monitor your accounts for suspicious activity",
                "Report the phishing attempt to relevant authorities",
                "Review recent transactions and statements",
                "Update security questions and recovery email/phone",
                "Scan devices for malware",
                "Check credit report for unauthorized activity",
                "Document all evidence for potential legal action"
            ],
            "scam": [
                "Stop all communication with the scammer immediately",
                "Document all interactions and evidence",
                "Report to local law enforcement and FBI IC3 (if applicable)",
                "Contact your bank to dispute fraudulent charges",
                "Place fraud alerts with credit bureaus",
                "Change passwords for any compromised accounts",
                "Report to FTC and appropriate consumer protection agencies",
                "Notify friends/family if scam involved impersonation",
                "Review financial statements for unauthorized transactions",
                "Consider identity theft protection services"
            ],
            "malware": [
                "Disconnect device from internet immediately",
                "Run comprehensive antivirus/anti-malware scan",
                "Change all passwords from a secure device",
                "Check for unauthorized access to accounts",
                "Review installed programs and remove suspicious ones",
                "Update operating system and all software",
                "Enable firewall and security features",
                "Back up important data (after ensuring it's clean)",
                "Consider professional malware removal if needed",
                "Monitor accounts for signs of data theft"
            ],
            "identity_theft": [
                "Place fraud alert with all three credit bureaus",
                "File report with local police department",
                "Report to Federal Trade Commission (FTC)",
                "Contact affected financial institutions immediately",
                "Close compromised accounts and open new ones",
                "Review credit reports from all bureaus",
                "Consider credit freeze to prevent new account openings",
                "Update security settings on all online accounts",
                "Monitor Social Security Administration records",
                "Keep detailed records of all recovery steps"
            ],
            "financial_fraud": [
                "Contact bank/credit card company immediately",
                "Dispute all fraudulent transactions",
                "File police report for documentation",
                "Place fraud alerts with credit bureaus",
                "Close compromised financial accounts",
                "Update online banking credentials",
                "Enable transaction alerts and monitoring",
                "Review recent statements for unauthorized activity",
                "Report to appropriate financial regulatory authorities",
                "Document all losses for insurance/legal purposes"
            ]
        }
        
        # Important contacts and resources
        self.resources = {
            "emergency_contacts": [
                {"name": "FBI Internet Crime Complaint Center (IC3)", "url": "https://www.ic3.gov/"},
                {"name": "Federal Trade Commission (FTC)", "url": "https://reportfraud.ftc.gov/"},
                {"name": "Anti-Phishing Working Group", "url": "https://apwg.org/"},
                {"name": "Local Law Enforcement", "info": "Call local police non-emergency number"}
            ],
            "credit_bureaus": [
                {"name": "Equifax", "phone": "1-800-525-6285"},
                {"name": "Experian", "phone": "1-888-397-3742"},
                {"name": "TransUnion", "phone": "1-800-680-7289"}
            ],
            "financial_institutions": [
                {"action": "Contact your bank immediately", "info": "Call number on back of card"},
                {"action": "Notify credit card companies", "info": "Report fraudulent charges"}
            ]
        }
    
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
            print(f"HF API Error in recovery assistant: {e}")
            return None
            
        return None
    
    def generate_recovery_plan(self, threat_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate comprehensive recovery plan based on detected threat
        
        Args:
            threat_data: Detection results including threat type, confidence, etc.
            
        Returns:
            Recovery plan with steps, recommendations, and resources
        """
        threat_type = threat_data.get("detection", {}).get("label", "phishing")
        confidence = threat_data.get("detection", {}).get("confidence", 0)
        scan_type = threat_data.get("scan_type", "text")
        
        # Map detection labels to recovery categories
        category_mapping = {
            "phishing": "phishing",
            "scam": "scam",
            "spam": "scam",
            "malicious": "malware",
            "fraud": "financial_fraud"
        }
        
        recovery_category = category_mapping.get(threat_type, "phishing")
        
        # Get base recovery steps
        recovery_steps = self._get_recovery_steps(recovery_category)
        
        # Generate AI-powered personalized advice
        personalized_advice = self._generate_personalized_advice(threat_data)
        
        # Calculate urgency level
        urgency = self._calculate_urgency(threat_data)
        
        # Create recovery session
        session_id = self._generate_session_id(threat_data)
        
        recovery_plan = {
            "session_id": session_id,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "threat_summary": {
                "type": threat_type,
                "category": recovery_category,
                "confidence": confidence,
                "scan_type": scan_type,
                "urgency_level": urgency
            },
            "immediate_actions": recovery_steps[:3],  # First 3 are most urgent
            "recovery_steps": recovery_steps,
            "personalized_advice": personalized_advice,
            "resources": self._get_relevant_resources(recovery_category),
            "progress_tracker": {
                "total_steps": len(recovery_steps),
                "completed_steps": [],
                "current_step": 0
            }
        }
        
        return recovery_plan
    
    def _get_recovery_steps(self, category: str) -> List[Dict[str, Any]]:
        """Get recovery steps for specific threat category"""
        template_steps = self.recovery_templates.get(category, self.recovery_templates["phishing"])
        
        steps = []
        for idx, step_description in enumerate(template_steps):
            steps.append({
                "step_number": idx + 1,
                "description": step_description,
                "status": "pending",
                "priority": "high" if idx < 3 else "medium" if idx < 7 else "normal",
                "completed_at": None
            })
        
        return steps
    
    def _generate_personalized_advice(self, threat_data: Dict[str, Any]) -> str:
        """Generate AI-powered personalized recovery advice"""
        
        # Extract key information
        threat_type = threat_data.get("detection", {}).get("label", "unknown")
        confidence = threat_data.get("detection", {}).get("confidence", 0)
        
        # Get attack analysis if available
        attack_goal = threat_data.get("redteam_analysis", {}).get("attack_goal", "Unknown attack goal")
        victim_profile = threat_data.get("redteam_analysis", {}).get("victim_profile", "General users")
        tactics = threat_data.get("redteam_analysis", {}).get("psychological_tactics", [])
        
        # Create prompt for AI advice
        prompt = f"""<|system|>
You are a fraud recovery specialist helping a victim of a cyber attack. Provide clear, actionable, and compassionate advice.
</s>
<|user|>
A user has been targeted by a {threat_type} attack. 

Attack details:
- Attack goal: {attack_goal}
- Target profile: {victim_profile}
- Tactics used: {', '.join(tactics) if tactics else 'Social engineering'}
- Confidence: {confidence}%

Based on this specific attack, provide personalized advice for the victim. Focus on:
1. Immediate actions they should take
2. What specific information might be compromised
3. How to protect themselves from similar attacks in the future

Keep the advice practical, empathetic, and under 200 words.
</s>
<|assistant|>
"""
        
        ai_advice = self._call_hf_inference(prompt)
        
        # Fallback to rule-based advice if AI fails
        if not ai_advice:
            ai_advice = self._generate_fallback_advice(threat_type, attack_goal)
        
        return ai_advice
    
    def _generate_fallback_advice(self, threat_type: str, attack_goal: str) -> str:
        """Generate rule-based advice when AI is unavailable"""
        advice_templates = {
            "phishing": f"You've been targeted by a phishing attack. The attacker's goal appears to be: {attack_goal}. Immediately change your passwords, enable 2FA, and contact your bank if you shared financial information. Be cautious of similar messages in the future and verify sender authenticity before clicking links.",
            "scam": f"You've encountered a scam attempt. The scammer's goal: {attack_goal}. Stop all communication immediately, report to authorities, and monitor your accounts. Never share personal or financial information with unverified contacts.",
            "malware": f"Your device may be infected with malware. The malicious software aims to: {attack_goal}. Disconnect from the internet, run a full antivirus scan, and change all passwords from a secure device. Consider professional help if the infection persists.",
        }
        
        return advice_templates.get(threat_type, 
            f"You've been targeted by a cyber threat. Take immediate action to secure your accounts and personal information. Contact relevant authorities and institutions to report the incident.")
    
    def _calculate_urgency(self, threat_data: Dict[str, Any]) -> str:
        """Calculate urgency level based on threat characteristics"""
        confidence = threat_data.get("detection", {}).get("confidence", 0)
        severity = threat_data.get("redteam_analysis", {}).get("severity", 5)
        
        # High urgency: high confidence and high severity
        if confidence >= 80 and severity >= 7:
            return "critical"
        elif confidence >= 60 and severity >= 5:
            return "high"
        elif confidence >= 40:
            return "medium"
        else:
            return "low"
    
    def _get_relevant_resources(self, category: str) -> Dict[str, List[Dict[str, str]]]:
        """Get relevant resources for specific threat category"""
        resources = {
            "emergency_contacts": self.resources["emergency_contacts"]
        }
        
        if category in ["phishing", "financial_fraud", "scam"]:
            resources["credit_bureaus"] = self.resources["credit_bureaus"]
            resources["financial_institutions"] = self.resources["financial_institutions"]
        
        return resources
    
    def _generate_session_id(self, threat_data: Dict[str, Any]) -> str:
        """Generate unique session ID for recovery tracking"""
        scan_id = threat_data.get("scan_id", "")
        timestamp = datetime.utcnow().isoformat()
        raw = f"{scan_id}{timestamp}"
        return hashlib.md5(raw.encode()).hexdigest()[:16]
    
    def update_progress(self, session_id: str, step_number: int, status: str = "completed") -> Dict[str, Any]:
        """
        Update recovery progress for a specific step
        
        Args:
            session_id: Recovery session ID
            step_number: Step number to update
            status: Status of the step (completed, in_progress, skipped)
            
        Returns:
            Updated progress information
        """
        return {
            "session_id": session_id,
            "step_number": step_number,
            "status": status,
            "updated_at": datetime.utcnow().isoformat() + "Z",
            "message": f"Step {step_number} marked as {status}"
        }
    
    def generate_report(self, recovery_plan: Dict[str, Any], completed_steps: List[int]) -> Dict[str, Any]:
        """
        Generate formal report for authorities/institutions
        
        Args:
            recovery_plan: Original recovery plan
            completed_steps: List of completed step numbers
            
        Returns:
            Formal incident and recovery report
        """
        report = {
            "report_id": f"FR-{recovery_plan['session_id']}",
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "incident_details": {
                "incident_type": recovery_plan["threat_summary"]["type"],
                "detection_date": recovery_plan["timestamp"],
                "confidence_level": recovery_plan["threat_summary"]["confidence"],
                "urgency_level": recovery_plan["threat_summary"]["urgency_level"]
            },
            "actions_taken": [
                {
                    "step": step["step_number"],
                    "description": step["description"],
                    "status": "completed" if step["step_number"] in completed_steps else "pending"
                }
                for step in recovery_plan["recovery_steps"]
            ],
            "completion_rate": f"{len(completed_steps)}/{recovery_plan['progress_tracker']['total_steps']}",
            "resources_contacted": recovery_plan["resources"],
            "recommendations": recovery_plan["personalized_advice"],
            "report_purpose": "This report can be used for filing complaints with law enforcement, financial institutions, or regulatory agencies."
        }
        
        return report
    
    def get_guidance_for_threat(self, threat_type: str) -> Dict[str, Any]:
        """
        Get general guidance for a specific threat type
        
        Args:
            threat_type: Type of threat (phishing, scam, malware, etc.)
            
        Returns:
            General guidance and prevention tips
        """
        # Map to recovery category
        category_mapping = {
            "phishing": "phishing",
            "scam": "scam",
            "spam": "scam",
            "malicious": "malware",
            "fraud": "financial_fraud",
            "identity": "identity_theft"
        }
        
        category = category_mapping.get(threat_type.lower(), "phishing")
        
        prevention_tips = {
            "phishing": [
                "Always verify sender email addresses carefully",
                "Hover over links before clicking to check URLs",
                "Never share passwords or sensitive info via email",
                "Enable email filters and spam protection",
                "Look for spelling and grammar errors in messages",
                "Be suspicious of urgent requests for information"
            ],
            "scam": [
                "Be skeptical of unsolicited offers or requests",
                "Never send money to unknown individuals",
                "Verify identities through official channels",
                "Don't trust caller ID - scammers can spoof numbers",
                "Research companies before making purchases",
                "Trust your instincts - if it seems too good to be true, it is"
            ],
            "malware": [
                "Keep antivirus software updated",
                "Don't download files from untrusted sources",
                "Keep operating system and software updated",
                "Use strong passwords and 2FA",
                "Be cautious with email attachments",
                "Back up important data regularly"
            ],
            "identity_theft": [
                "Monitor credit reports regularly",
                "Use strong, unique passwords for each account",
                "Enable 2FA on all important accounts",
                "Shred sensitive documents before disposal",
                "Be cautious about sharing personal information",
                "Review financial statements regularly"
            ],
            "financial_fraud": [
                "Monitor bank accounts and credit cards regularly",
                "Enable transaction alerts",
                "Use secure payment methods",
                "Verify website security (HTTPS) before entering card info",
                "Never share PINs or CVV codes",
                "Report suspicious charges immediately"
            ]
        }
        
        return {
            "threat_type": threat_type,
            "category": category,
            "overview": f"Guidance for {category.replace('_', ' ').title()} threats",
            "recovery_steps": self.recovery_templates.get(category, self.recovery_templates["phishing"]),
            "prevention_tips": prevention_tips.get(category, prevention_tips["phishing"]),
            "resources": self._get_relevant_resources(category)
        }
