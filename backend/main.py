"""
CyberSentryAI Unified API
FastAPI backend with Red-Team AI and Cyber DNA Fingerprinting
Uses only Hugging Face Inference APIs
"""
from fastapi import FastAPI, HTTPException, Request, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import base64
import asyncio
import json
import os
import pickle
import urllib.error
import urllib.request
from pathlib import Path
from datetime import datetime

# Import our engines
from redteam_engine import RedTeamEngine
from cyber_dna_engine import CyberDNAEngine
from scan_logger import ScanLogger

app = FastAPI(
    title="CyberSentryAI API",
    description="Unified threat detection with Red-Team AI and Cyber DNA Fingerprinting",
    version="2.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize engines
redteam_engine = RedTeamEngine()
dna_engine = CyberDNAEngine()
scan_logger = ScanLogger()

# Load models
with open("models/text_scam_model.pkl", "rb") as f:
    text_model, text_vectorizer = pickle.load(f)

with open("models/url_phishing_model.pkl", "rb") as f:
    url_model = pickle.load(f)

# HF Configuration
HF_API_TOKEN = os.getenv("HF_API_TOKEN")
HF_TIMEOUT = float(os.getenv("HF_TIMEOUT", "15"))

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
            is_scam = any(key in label for key in ("spam", "scam", "phishing"))
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
            is_phishing = any(key in label for key in ("spam", "scam", "phishing"))
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
    hf_result = hf_classify_text(request.text)
    
    if hf_result:
        scan_result = hf_result
    else:
        # Fallback to local model
        X = text_vectorizer.transform([request.text])
        pred = text_model.predict(X)[0]
        prob = text_model.predict_proba(X)[0][1]
        scan_result = {
            "label": "scam" if pred == 1 else "safe",
            "score": float(prob),
            "is_scam": bool(pred == 1)
        }
    
    # Red-Team analysis
    redteam_result = None
    if request.enable_redteam:
        redteam_result = redteam_engine.analyze_text(request.text, scan_result)
    
    # Cyber DNA
    cyber_dna = None
    if request.enable_dna:
        cyber_dna = dna_engine.generate_dna(
            request.text,
            "text",
            scan_result,
            redteam_result
        )
    
    # Similar threats
    similar_threats = []
    if cyber_dna:
        dna_db = scan_logger.get_dna_database(threat_only=True, min_confidence=60)
        similar_threats = dna_engine.find_similar_threats(cyber_dna, dna_db, threshold=0.7)
    
    # Log everything
    scan_id = scan_logger.log_scan(
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
            "is_threat": scan_result.get("is_scam", False),
            "confidence": round(scan_result.get("score", 0) * 100, 2),
            "label": scan_result.get("label", "unknown"),
            "source": "huggingface" if hf_result else "local"
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
    hf_result = hf_classify_url(request.url)
    
    if hf_result:
        scan_result = hf_result
    else:
        # Fallback to local model (would need URL features extraction)
        # For now, use simple heuristics
        is_phishing = False
        reasons = []
        
        if not request.url.startswith("https"):
            is_phishing = True
            reasons.append("No HTTPS")
        if "@" in request.url:
            is_phishing = True
            reasons.append("@ symbol")
        if request.url.count("-") > 3:
            is_phishing = True
            reasons.append("Many hyphens")
        
        scan_result = {
            "label": "phishing" if is_phishing else "safe",
            "score": 0.85 if is_phishing else 0.1,
            "is_phishing": is_phishing,
            "reasons": reasons
        }
    
    # Red-Team analysis
    redteam_result = None
    if request.enable_redteam:
        redteam_result = redteam_engine.analyze_url(request.url, scan_result)
    
    # Cyber DNA
    cyber_dna = None
    if request.enable_dna:
        cyber_dna = dna_engine.generate_dna(
            request.url,
            "url",
            scan_result,
            redteam_result
        )
    
    # Similar threats
    similar_threats = []
    if cyber_dna:
        dna_db = scan_logger.get_dna_database(threat_only=True, min_confidence=60)
        similar_threats = dna_engine.find_similar_threats(cyber_dna, dna_db, threshold=0.7)
    
    # Log
    scan_id = scan_logger.log_scan(
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
            "is_threat": scan_result.get("is_phishing", False),
            "confidence": round(scan_result.get("score", 0) * 100, 2),
            "label": scan_result.get("label", "unknown"),
            "source": "huggingface" if hf_result else "local"
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
            with urllib.request.urlopen(request.image_url, timeout=HF_TIMEOUT) as resp:
                image_bytes = resp.read()
        except Exception:
            raise HTTPException(400, "Failed to fetch image from URL")
    else:
        raise HTTPException(400, "Provide image_base64 or image_url")
    
    # Primary detection
    hf_result = hf_classify_image(image_bytes)
    
    if not hf_result:
        raise HTTPException(503, "Image classification service unavailable")
    
    scan_result = hf_result
    
    # Red-Team analysis
    redteam_result = None
    if request.enable_redteam:
        redteam_result = redteam_engine.analyze_image(scan_result)
    
    # Cyber DNA
    cyber_dna = None
    if request.enable_dna:
        cyber_dna = dna_engine.generate_dna(
            scan_result.get("label", ""),
            "image",
            scan_result,
            redteam_result
        )
    
    # Similar threats
    similar_threats = []
    if cyber_dna:
        dna_db = scan_logger.get_dna_database(threat_only=True, min_confidence=60)
        similar_threats = dna_engine.find_similar_threats(cyber_dna, dna_db, threshold=0.7)
    
    # Log
    scan_id = scan_logger.log_scan(
        scan_type="image",
        raw_input={"image_id": scan_id, "size": len(image_bytes)},
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
            "is_threat": scan_result.get("is_fake", False),
            "confidence": round(scan_result.get("score", 0) * 100, 2),
            "label": scan_result.get("label", "unknown"),
            "source": "huggingface"
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
    hf_result = hf_classify_text(email_content)
    
    if hf_result:
        scan_result = hf_result
    else:
        X = text_vectorizer.transform([email_content])
        pred = text_model.predict(X)[0]
        prob = text_model.predict_proba(X)[0][1]
        scan_result = {
            "label": "scam" if pred == 1 else "safe",
            "score": float(prob),
            "is_scam": bool(pred == 1)
        }
    
    # Red-Team analysis
    redteam_result = None
    if request.enable_redteam:
        redteam_result = redteam_engine.analyze_text(email_content, scan_result)
    
    # Cyber DNA
    cyber_dna = None
    if request.enable_dna:
        cyber_dna = dna_engine.generate_dna(
            email_content,
            "email",
            scan_result,
            redteam_result
        )
    
    # Similar threats
    similar_threats = []
    if cyber_dna:
        dna_db = scan_logger.get_dna_database(threat_only=True, min_confidence=60)
        similar_threats = dna_engine.find_similar_threats(cyber_dna, dna_db, threshold=0.7)
    
    # Log
    scan_id = scan_logger.log_scan(
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
            "is_threat": scan_result.get("is_scam", False),
            "confidence": round(scan_result.get("score", 0) * 100, 2),
            "label": scan_result.get("label", "unknown"),
            "source": "huggingface" if hf_result else "local"
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
