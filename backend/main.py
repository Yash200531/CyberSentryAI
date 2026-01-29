"""
CyberSentryAI Unified API
FastAPI backend with Red-Team AI and Cyber DNA Fingerprinting
Uses only Hugging Face Inference APIs
"""


from fastapi import FastAPI, HTTPException, Request, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import base64
import asyncio
import json
import os
import pickle
import hashlib
import sys
import re
import urllib.error
import urllib.request
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Import our engines
from redteam_engine import RedTeamEngine
from cyber_dna_engine import CyberDNAEngine
from scan_logger import ScanLogger

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# Load environment variables (.env) from backend or project root
load_dotenv(BASE_DIR / ".env")
load_dotenv(PROJECT_ROOT / ".env")

app = FastAPI(
    title="CyberSentryAI API",
    description="Unified threat detection with Red-Team AI and Cyber DNA Fingerprinting",
    version="2.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize engines
redteam_engine = RedTeamEngine()
dna_engine = CyberDNAEngine()
scan_logger = ScanLogger()

# Load models (absolute paths)
TEXT_MODEL_PATH = BASE_DIR / "models" / "text_scam_model.pkl"
URL_MODEL_PATH = BASE_DIR / "models" / "url_phishing_model.pkl"

with open(TEXT_MODEL_PATH, "rb") as f:
    text_model, text_vectorizer = pickle.load(f)

with open(URL_MODEL_PATH, "rb") as f:
    url_model = pickle.load(f)


# HF Configuration
HF_API_TOKEN = os.getenv("HF_API_TOKEN")
HF_TIMEOUT = float(os.getenv("HF_TIMEOUT", "15"))
HF_MIN_PROB = float(os.getenv("HF_MIN_PROB", "0.25"))
HF_MAX_PROB = float(os.getenv("HF_MAX_PROB", "0.45"))

# Text model
HF_TEXT_MODEL = os.getenv("HF_TEXT_MODEL", "mrm8488/bert-tiny-finetuned-sms-spam-detection")
HF_TEXT_URL = f"https://api-inference.huggingface.co/models/{HF_TEXT_MODEL}"

# URL model
HF_URL_MODEL = os.getenv("HF_URL_MODEL", "mrm8488/bert-tiny-finetuned-sms-spam-detection")
HF_URL_URL = f"https://api-inference.huggingface.co/models/{HF_URL_MODEL}"

# Image model
HF_IMAGE_MODEL = os.getenv("HF_IMAGE_MODEL", "prithivMLmods/DeepFake-Detection")
HF_IMAGE_URL = f"https://api-inference.huggingface.co/models/{HF_IMAGE_MODEL}"


# Pydantic models
class TextScanRequest(BaseModel):
    text: str = Field(..., description="Text content to analyze")
    user_id: Optional[str] = None
    enable_redteam: bool = Field(True, description="Enable Red-Team analysis")
    enable_dna: bool = Field(True, description="Enable Cyber DNA fingerprinting")


class URLScanRequest(BaseModel):
    url: str = Field(..., description="URL to analyze")
    user_id: Optional[str] = None
    enable_redteam: bool = Field(True, description="Enable Red-Team analysis")
    enable_dna: bool = Field(True, description="Enable Cyber DNA fingerprinting")


class ImageScanRequest(BaseModel):
    image_base64: Optional[str] = None
    image_url: Optional[str] = None
    user_id: Optional[str] = None
    enable_redteam: bool = Field(True, description="Enable Red-Team analysis")
    enable_dna: bool = Field(True, description="Enable Cyber DNA fingerprinting")


class EmailScanRequest(BaseModel):
    subject: str
    body: str
    sender: Optional[str] = None
    user_id: Optional[str] = None
    enable_redteam: bool = Field(True, description="Enable Red-Team analysis")
    enable_dna: bool = Field(True, description="Enable Cyber DNA fingerprinting")


# Helper functions
def hf_classify_text(text: str) -> Optional[Dict]:
    """Call HuggingFace text classification API"""
    if not HF_API_TOKEN:
        return None
    
    payload = json.dumps({"inputs": text}).encode("utf-8")
    req = urllib.request.Request(
        HF_TEXT_URL,
        data=payload,
        headers={
            "Authorization": f"Bearer {HF_API_TOKEN}",
            "Content-Type": "application/json",
        },
    )
    
    try:
        with urllib.request.urlopen(req, timeout=HF_TIMEOUT) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        
        if isinstance(data, dict) and data.get("error"):
            return None
        
        if isinstance(data, list) and data and isinstance(data[0], list):
            data = data[0]
        
        if isinstance(data, list) and data:
            best = max(data, key=lambda item: item.get("score", 0))
            label = str(best.get("label", "")).lower()
            score = float(best.get("score", 0))
            is_scam = _is_suspicious_label(label, score)
            return {"label": label, "score": score, "is_scam": is_scam}
    
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, ValueError):
        pass
    
    return None


def hf_classify_url(url: str) -> Optional[Dict]:
    """Call HuggingFace URL classification API"""
    if not HF_API_TOKEN:
        return None
    
    payload = json.dumps({"inputs": url}).encode("utf-8")
    req = urllib.request.Request(
        HF_URL_URL,
        data=payload,
        headers={
            "Authorization": f"Bearer {HF_API_TOKEN}",
            "Content-Type": "application/json",
        },
    )
    
    try:
        with urllib.request.urlopen(req, timeout=HF_TIMEOUT) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        
        if isinstance(data, dict) and data.get("error"):
            return None
        
        if isinstance(data, list) and data and isinstance(data[0], list):
            data = data[0]
        
        if isinstance(data, list) and data:
            best = max(data, key=lambda item: item.get("score", 0))
            label = str(best.get("label", "")).lower()
            score = float(best.get("score", 0))
            is_phishing = _is_suspicious_label(label, score)
            return {"label": label, "score": score, "is_phishing": is_phishing}
    
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, ValueError):
        pass
    
    return None


def hf_classify_image(image_bytes: bytes) -> Optional[Dict]:
    """Call HuggingFace image classification API"""
    if not HF_API_TOKEN:
        return None
    
    req = urllib.request.Request(
        HF_IMAGE_URL,
        data=image_bytes,
        headers={
            "Authorization": f"Bearer {HF_API_TOKEN}",
            "Content-Type": "application/octet-stream",
        },
    )
    
    try:
        with urllib.request.urlopen(req, timeout=HF_TIMEOUT) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        
        if isinstance(data, dict) and data.get("error"):
            return None
        
        if isinstance(data, list) and data:
            best = max(data, key=lambda item: item.get("score", 0))
            label = str(best.get("label", "")).lower()
            score = float(best.get("score", 0))
            is_fake = any(key in label for key in ("fake", "deepfake", "ai", "synthetic"))
            if any(key in label for key in ("real", "authentic")):
                is_fake = False
            return {"label": label, "score": score, "is_fake": is_fake}
    
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, ValueError):
        pass
    
    return None


def _is_suspicious_label(label: str, score: float) -> bool:
    suspicious_threshold = HF_MIN_PROB
    malicious_threshold = HF_MAX_PROB

    risky_tokens = (
        "spam",
        "scam",
        "phishing",
        "malicious",
        "fraud",
        "social engineering",
        "unsafe",
        "threat",
        "negative",
    )
    safe_tokens = (
        "ham",
        "safe",
        "benign",
        "legit",
        "legitimate",
        "positive",
    )

    label_is_risky = any(token in label for token in risky_tokens)
    label_is_safe = any(token in label for token in safe_tokens)

    if label_is_safe and not label_is_risky:
        return False

    if label_is_risky:
        return score >= suspicious_threshold

    return score >= suspicious_threshold


async def _run_blocking(func, *args, **kwargs):
    return await asyncio.to_thread(func, *args, **kwargs)


def _local_text_infer(text: str) -> Dict[str, Any]:
    X = text_vectorizer.transform([text])
    pred = text_model.predict(X)[0]
    prob = text_model.predict_proba(X)[0][1]
    return {
        "label": "scam" if pred == 1 else "safe",
        "score": float(prob),
        "is_scam": bool(pred == 1)
    }


def _local_email_infer(email_content: str) -> Dict[str, Any]:
    X = text_vectorizer.transform([email_content])
    pred = text_model.predict(X)[0]
    prob = text_model.predict_proba(X)[0][1]
    return {
        "label": "scam" if pred == 1 else "safe",
        "score": float(prob),
        "is_scam": bool(pred == 1)
    }


def _local_url_infer(url: str) -> Dict[str, Any]:
    is_phishing = False
    reasons = []

    if not url.startswith("https"):
        is_phishing = True
        reasons.append("No HTTPS")
    if "@" in url:
        is_phishing = True
        reasons.append("@ symbol")
    if url.count("-") > 3:
        is_phishing = True
        reasons.append("Many hyphens")

    return {
        "label": "phishing" if is_phishing else "safe",
        "score": 0.85 if is_phishing else 0.1,
        "is_phishing": is_phishing,
        "reasons": reasons
    }


def _fetch_image_from_url(url: str) -> bytes:
    with urllib.request.urlopen(url, timeout=HF_TIMEOUT) as resp:
        return resp.read()


def _clamp_score(value: float, min_value: float = 0, max_value: float = 100) -> float:
    return max(min_value, min(max_value, value))


def _compute_text_signals(text: str) -> Dict[str, Any]:
    content = text.lower()
    has_link = bool(re.search(r"https?://|\bwww\.", content))
    keyword_hits = [
        kw for kw in (
            "verify",
            "secure",
            "bank",
            "account",
            "password",
            "login",
            "otp",
            "code",
            "payment",
            "refund",
            "kyc",
            "update",
            "confirm",
        )
        if kw in content
    ]
    impersonation_hits = [
        kw for kw in (
            "bank",
            "upi",
            "google",
            "amazon",
            "govt",
            "government",
            "irs",
            "police",
        )
        if kw in content
    ]
    suspicious_tld = bool(re.search(r"\.(ru|cn|tk|ml|ga|cf|gq|top|xyz)(\b|/)", content))
    many_dots = content.count(".") >= 4

    action_request = bool(re.search(r"\b(click|tap|visit|login|verify|update|respond|reply|call)\b", content))
    credential_request = bool(re.search(r"\b(password|otp|code|pin|ssn|cvv|account number)\b", content))
    urgency = bool(re.search(r"\b(urgent|immediately|expire|now|limited time|suspended)\b", content))
    financial_action = bool(re.search(r"\b(payment|pay|refund|transfer|upi|bank|card|invoice)\b", content)) and action_request

    rule_hits = sum([
        has_link,
        bool(keyword_hits),
        bool(impersonation_hits),
        suspicious_tld or many_dots,
    ])
    context_hits = sum([action_request, credential_request, urgency])

    forced_threat = (has_link and bool(impersonation_hits)) or credential_request or financial_action

    explanations = []
    if has_link:
        explanations.append("Contains link or URL")
    if keyword_hits:
        explanations.append("Contains verification/security keywords")
    if impersonation_hits:
        explanations.append("Possible impersonation of known brands or institutions")
    if suspicious_tld or many_dots:
        explanations.append("Suspicious or obfuscated domain")
    if action_request:
        explanations.append("Requests immediate action")
    if credential_request:
        explanations.append("Requests credentials or codes")
    if urgency:
        explanations.append("Creates urgency or time pressure")
    if financial_action:
        explanations.append("Requests financial action")

    return {
        "has_link": has_link,
        "keyword_hits": keyword_hits,
        "impersonation_hits": impersonation_hits,
        "suspicious_domain": suspicious_tld or many_dots,
        "action_request": action_request,
        "credential_request": credential_request,
        "urgency": urgency,
        "financial_action": financial_action,
        "rule_hits": rule_hits,
        "context_hits": context_hits,
        "forced_threat": forced_threat,
        "explanations": explanations,
    }




# API Endpoints
@app.get("/")
async def root():
    return {
        "service": "CyberSentryAI Unified API",
        "version": "2.0.0",
        "features": ["Red-Team AI", "Cyber DNA Fingerprinting", "Multi-Model Detection"],
        "status": "operational"
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "engines": {
            "redteam": "operational",
            "cyber_dna": "operational",
            "logging": "operational"
        }
    }


@app.post("/scan/text")
async def scan_text(request: TextScanRequest, req: Request):
    """Scan text/SMS content with full analysis"""
    
    # Primary detection
    hf_result = await _run_blocking(hf_classify_text, request.text)
    
    if hf_result:
        scan_result = hf_result
    else:
        # Fallback to local model
        scan_result = await _run_blocking(_local_text_infer, request.text)

    signals = _compute_text_signals(request.text)
    base_score = float(scan_result.get("score", 0)) * 100
    model_signal = base_score >= 30
    rule_signal = signals["rule_hits"] > 0
    context_signal = signals["context_hits"] > 0
    is_threat = (sum([model_signal, rule_signal, context_signal]) >= 2) or signals["forced_threat"]
    rule_adjust = (signals["rule_hits"] + signals["context_hits"]) * 10
    final_score = _clamp_score(base_score + rule_adjust)
    if signals["forced_threat"] and final_score < 30:
        final_score = 30
    
    # Red-Team analysis
    redteam_result = None
    if request.enable_redteam:
        redteam_result = await _run_blocking(redteam_engine.analyze_text, request.text, scan_result)
    
    # Cyber DNA
    cyber_dna = None
    if request.enable_dna:
        cyber_dna = await _run_blocking(
            dna_engine.generate_dna,
            request.text,
            "text",
            scan_result,
            redteam_result
        )
    
    # Similar threats
    similar_threats = []
    if cyber_dna:
        dna_db = await _run_blocking(scan_logger.get_dna_database, threat_only=True, min_confidence=60)
        similar_threats = await _run_blocking(dna_engine.find_similar_threats, cyber_dna, dna_db, threshold=0.7)
    
    # Log everything
    scan_id = await _run_blocking(
        scan_logger.log_scan,
        scan_type="text",
        raw_input=request.text,
        scan_result=scan_result,
        redteam_result=redteam_result,
        cyber_dna=cyber_dna,
        user_id=request.user_id,
        user_ip=req.client.host
    )
    
    return {
        "scan_id": scan_id,
        "timestamp": datetime.utcnow().isoformat(),
        "scan_type": "text",
        "detection": {
            "is_threat": bool(is_threat),
            "confidence": round(scan_result.get("score", 0), 4),
            "risk_score": round(final_score, 2),
            "label": scan_result.get("label", "unknown"),
            "source": "huggingface" if hf_result else "local",
            "explanations": signals["explanations"],
            "signals": {
                "model_signal": model_signal,
                "rule_signal": rule_signal,
                "context_signal": context_signal,
                "forced_threat": signals["forced_threat"],
            },
        },
        "redteam_analysis": redteam_result,
        "cyber_dna": {
            "dna_hash": cyber_dna.get("dna_hash") if cyber_dna else None,
            "scores": cyber_dna.get("scores") if cyber_dna else None,
            "overall_threat_score": cyber_dna.get("overall_threat_score") if cyber_dna else None
        },
        "similar_threats": similar_threats[:5],  # Top 5
        "recommendation": _generate_recommendation(scan_result, redteam_result)
    }


@app.post("/scan/url")
async def scan_url(request: URLScanRequest, req: Request):
    """Scan URL with full analysis"""
    
    # Primary detection
    hf_result = await _run_blocking(hf_classify_url, request.url)
    
    if hf_result:
        scan_result = hf_result
    else:
        # Fallback to local model (would need URL features extraction)
        # For now, use simple heuristics
        scan_result = await _run_blocking(_local_url_infer, request.url)

    signals = _compute_text_signals(request.url)
    base_score = float(scan_result.get("score", 0)) * 100
    model_signal = base_score >= 30
    rule_signal = signals["rule_hits"] > 0
    context_signal = signals["context_hits"] > 0
    is_threat = (sum([model_signal, rule_signal, context_signal]) >= 2) or signals["forced_threat"]
    rule_adjust = (signals["rule_hits"] + signals["context_hits"]) * 10
    final_score = _clamp_score(base_score + rule_adjust)
    if signals["forced_threat"] and final_score < 30:
        final_score = 30
    
    # Red-Team analysis
    redteam_result = None
    if request.enable_redteam:
        redteam_result = await _run_blocking(redteam_engine.analyze_url, request.url, scan_result)
    
    # Cyber DNA
    cyber_dna = None
    if request.enable_dna:
        cyber_dna = await _run_blocking(
            dna_engine.generate_dna,
            request.url,
            "url",
            scan_result,
            redteam_result
        )
    
    # Similar threats
    similar_threats = []
    if cyber_dna:
        dna_db = await _run_blocking(scan_logger.get_dna_database, threat_only=True, min_confidence=60)
        similar_threats = await _run_blocking(dna_engine.find_similar_threats, cyber_dna, dna_db, threshold=0.7)
    
    # Log
    scan_id = await _run_blocking(
        scan_logger.log_scan,
        scan_type="url",
        raw_input=request.url,
        scan_result=scan_result,
        redteam_result=redteam_result,
        cyber_dna=cyber_dna,
        user_id=request.user_id,
        user_ip=req.client.host
    )
    
    return {
        "scan_id": scan_id,
        "timestamp": datetime.utcnow().isoformat(),
        "scan_type": "url",
        "detection": {
            "is_threat": bool(is_threat),
            "confidence": round(scan_result.get("score", 0), 4),
            "risk_score": round(final_score, 2),
            "label": scan_result.get("label", "unknown"),
            "source": "huggingface" if hf_result else "local",
            "explanations": signals["explanations"],
            "signals": {
                "model_signal": model_signal,
                "rule_signal": rule_signal,
                "context_signal": context_signal,
                "forced_threat": signals["forced_threat"],
            },
        },
        "redteam_analysis": redteam_result,
        "cyber_dna": {
            "dna_hash": cyber_dna.get("dna_hash") if cyber_dna else None,
            "scores": cyber_dna.get("scores") if cyber_dna else None,
            "overall_threat_score": cyber_dna.get("overall_threat_score") if cyber_dna else None
        },
        "similar_threats": similar_threats[:5],
        "recommendation": _generate_recommendation(scan_result, redteam_result)
    }


@app.post("/scan/image")
async def scan_image(request: ImageScanRequest, req: Request):
    """Scan image with full analysis"""
    
    # Load image bytes
    if request.image_base64:
        try:
            image_bytes = base64.b64decode(request.image_base64)
        except Exception:
            raise HTTPException(400, "Invalid base64 image")
    elif request.image_url:
        try:
            image_bytes = await _run_blocking(_fetch_image_from_url, request.image_url)
        except Exception:
            raise HTTPException(400, "Failed to fetch image from URL")
    else:
        raise HTTPException(400, "Provide image_base64 or image_url")
    
    # Primary detection
    hf_result = await _run_blocking(hf_classify_image, image_bytes)
    if not hf_result:
        return JSONResponse(status_code=503, content={"error": "Image scanning requires Hugging Face service"})
    scan_result = hf_result
    detection_source = "huggingface"

    base_score = float(scan_result.get("score", 0)) * 100
    is_threat = base_score >= 30 or bool(scan_result.get("is_fake", False))
    final_score = _clamp_score(base_score)
    
    # Red-Team analysis
    redteam_result = None
    if request.enable_redteam:
        redteam_result = await _run_blocking(redteam_engine.analyze_image, scan_result)
    
    # Cyber DNA
    cyber_dna = None
    if request.enable_dna:
        cyber_dna = await _run_blocking(
            dna_engine.generate_dna,
            scan_result.get("label", ""),
            "image",
            scan_result,
            redteam_result
        )
    
    # Similar threats
    similar_threats = []
    if cyber_dna:
        dna_db = await _run_blocking(scan_logger.get_dna_database, threat_only=True, min_confidence=60)
        similar_threats = await _run_blocking(dna_engine.find_similar_threats, cyber_dna, dna_db, threshold=0.7)
    
    # Log
    image_id = hashlib.sha256(image_bytes).hexdigest()
    scan_id = await _run_blocking(
        scan_logger.log_scan,
        scan_type="image",
        raw_input={"image_id": image_id, "size": len(image_bytes)},
        scan_result=scan_result,
        redteam_result=redteam_result,
        cyber_dna=cyber_dna,
        user_id=request.user_id,
        user_ip=req.client.host
    )
    
    return {
        "scan_id": scan_id,
        "timestamp": datetime.utcnow().isoformat(),
        "scan_type": "image",
        "detection": {
            "is_threat": bool(is_threat),
            "confidence": round(scan_result.get("score", 0), 4),
            "risk_score": round(final_score, 2),
            "label": scan_result.get("label", "unknown"),
            "source": detection_source
        },
        "redteam_analysis": redteam_result,
        "cyber_dna": {
            "dna_hash": cyber_dna.get("dna_hash") if cyber_dna else None,
            "scores": cyber_dna.get("scores") if cyber_dna else None,
            "overall_threat_score": cyber_dna.get("overall_threat_score") if cyber_dna else None
        },
        "similar_threats": similar_threats[:5],
        "recommendation": _generate_recommendation(scan_result, redteam_result)
    }


@app.post("/scan/email")
async def scan_email(request: EmailScanRequest, req: Request):
    """Scan email with full analysis"""
    
    # Combine subject and body
    email_content = f"Subject: {request.subject}\n\n{request.body}"
    
    # Use text scanning
    hf_result = await _run_blocking(hf_classify_text, email_content)
    
    if hf_result:
        scan_result = hf_result
    else:
        scan_result = await _run_blocking(_local_email_infer, email_content)

    signals = _compute_text_signals(email_content)
    base_score = float(scan_result.get("score", 0)) * 100
    model_signal = base_score >= 30
    rule_signal = signals["rule_hits"] > 0
    context_signal = signals["context_hits"] > 0
    is_threat = (sum([model_signal, rule_signal, context_signal]) >= 2) or signals["forced_threat"]
    rule_adjust = (signals["rule_hits"] + signals["context_hits"]) * 10
    final_score = _clamp_score(base_score + rule_adjust)
    if signals["forced_threat"] and final_score < 30:
        final_score = 30
    
    # Red-Team analysis
    redteam_result = None
    if request.enable_redteam:
        redteam_result = await _run_blocking(redteam_engine.analyze_text, email_content, scan_result)
    
    # Cyber DNA
    cyber_dna = None
    if request.enable_dna:
        cyber_dna = await _run_blocking(
            dna_engine.generate_dna,
            email_content,
            "email",
            scan_result,
            redteam_result
        )
    
    # Similar threats
    similar_threats = []
    if cyber_dna:
        dna_db = await _run_blocking(scan_logger.get_dna_database, threat_only=True, min_confidence=60)
        similar_threats = await _run_blocking(dna_engine.find_similar_threats, cyber_dna, dna_db, threshold=0.7)
    
    # Log
    scan_id = await _run_blocking(
        scan_logger.log_scan,
        scan_type="email",
        raw_input=email_content,
        scan_result=scan_result,
        redteam_result=redteam_result,
        cyber_dna=cyber_dna,
        user_id=request.user_id,
        user_ip=req.client.host,
        metadata={"sender": request.sender, "subject": request.subject}
    )
    
    return {
        "scan_id": scan_id,
        "timestamp": datetime.utcnow().isoformat(),
        "scan_type": "email",
        "detection": {
            "is_threat": bool(is_threat),
            "confidence": round(scan_result.get("score", 0), 4),
            "risk_score": round(final_score, 2),
            "label": scan_result.get("label", "unknown"),
            "source": "huggingface" if hf_result else "local",
            "explanations": signals["explanations"],
            "signals": {
                "model_signal": model_signal,
                "rule_signal": rule_signal,
                "context_signal": context_signal,
                "forced_threat": signals["forced_threat"],
            },
        },
        "redteam_analysis": redteam_result,
        "cyber_dna": {
            "dna_hash": cyber_dna.get("dna_hash") if cyber_dna else None,
            "scores": cyber_dna.get("scores") if cyber_dna else None,
            "overall_threat_score": cyber_dna.get("overall_threat_score") if cyber_dna else None
        },
        "similar_threats": similar_threats[:5],
        "recommendation": _generate_recommendation(scan_result, redteam_result)
    }


@app.get("/history")
async def get_history(
    scan_type: Optional[str] = None,
    limit: int = 50,
    threat_only: bool = False
):
    """Get scan history"""
    history = scan_logger.get_scan_history(scan_type, limit, threat_only)
    return {
        "total": len(history),
        "scans": history
    }


@app.get("/stats")
async def get_stats():
    """Get daily statistics"""
    stats = scan_logger.get_daily_stats()
    return stats


@app.get("/dna/similar/{dna_hash}")
async def find_similar_by_hash(dna_hash: str, threshold: float = 0.7):
    """Find similar threats by DNA hash"""
    # This would require storing DNAs with their hashes for lookup
    # Implementation depends on your storage strategy
    return {
        "message": "Feature requires DNA database indexing",
        "dna_hash": dna_hash
    }


def _generate_recommendation(scan_result: Dict, redteam_result: Optional[Dict]) -> str:
    """Generate user recommendation based on analysis"""
    is_threat = (
        scan_result.get("is_scam") or 
        scan_result.get("is_phishing") or 
        scan_result.get("is_fake", False)
    )
    
    if not is_threat:
        return "This content appears safe. Always remain vigilant."
    
    confidence = scan_result.get("score", 0) * 100
    
    if confidence > 80:
        severity = "HIGH RISK"
    elif confidence > 50:
        severity = "MEDIUM RISK"
    else:
        severity = "LOW RISK"
    
    recommendation = f"⚠️ {severity} DETECTED. "
    
    if redteam_result:
        goal = redteam_result.get("attack_goal", "malicious activity")
        recommendation += f"Likely attack goal: {goal}. "
    
    recommendation += "Do NOT click links, share information, or respond. Report and delete."
    
    return recommendation


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
