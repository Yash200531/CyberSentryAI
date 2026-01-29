"""
Simple FastAPI server without model dependencies
For testing connectivity
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import os

app = FastAPI(
    title="CyberSentryAI API",
    description="Unified threat detection - Basic version",
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

@app.get("/")
async def root():
    return {
        "service": "CyberSentryAI API",
        "version": "2.0.0",
        "status": "operational",
        "message": "Server is running successfully!"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "server": "running"
    }

@app.get("/test")
async def test_endpoint():
    return {
        "message": "Connection successful!",
        "server": "CyberSentryAI v2.0",
        "timestamp": datetime.utcnow().isoformat()
    }

class SimpleTextRequest(BaseModel):
    text: str

class SimpleEmailRequest(BaseModel):
    email_content: str

class SimpleURLRequest(BaseModel):
    url: str

class SimpleImageRequest(BaseModel):
    image_data: str

def create_mock_response(scan_type: str, is_threat: bool, confidence: float, content: str):
    scan_id = f"scan_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    severity = int(confidence / 10)
    
    return {
        "scan_id": scan_id,
        "timestamp": datetime.utcnow().isoformat(),
        "scan_type": scan_type,
        "content": content[:200],
        "detection": {
            "is_threat": is_threat,
            "confidence": confidence,
            "label": "threat" if is_threat else "safe",
            "threat_type": "phishing" if is_threat else "legitimate"
        },
        "redteam_analysis": {
            "attack_goal": "Social engineering via urgency" if is_threat else "No attack detected",
            "victim_profile": "Users susceptible to urgency tactics" if is_threat else "N/A",
            "psychological_tactics": ["urgency", "fear"] if is_threat else [],
            "exploitation_chain": ["email delivery", "link click", "credential harvest"] if is_threat else [],
            "next_step": "User clicks malicious link" if is_threat else "No action",
            "severity": severity
        },
        "cyber_dna": {
            "dna_hash": f"dna_{scan_id}",
            "overall_threat_score": confidence,
            "scores": {
                "linguistic": confidence * 0.9 if is_threat else 10,
                "urgency": confidence * 0.95 if is_threat else 5,
                "brand_impersonation": confidence * 0.7 if is_threat else 0,
                "obfuscation": confidence * 0.6 if is_threat else 0,
                "visual_deception": confidence * 0.5 if is_threat else 0,
                "malicious_intent": confidence if is_threat else 0
            },
            "embedding_preview": [0.1, 0.2, 0.3, 0.4, 0.5]
        },
        "similar_threats": []
    }

@app.post("/scan/text")
async def scan_text_simple(request: SimpleTextRequest):
    """Simple text scan"""
    text = request.text.lower()
    threat_keywords = ["urgent", "verify", "suspended", "click here", "prize", "won", "congratulations"]
    matches = sum(1 for keyword in threat_keywords if keyword in text)
    is_threat = matches >= 2
    confidence = min(95.0, matches * 15.0)
    return create_mock_response("text", is_threat, confidence, request.text)

@app.post("/scan/email")
async def scan_email_simple(request: SimpleEmailRequest):
    """Simple email scan"""
    email = request.email_content.lower()
    threat_keywords = ["urgent", "account", "verify", "suspended", "click", "prize"]
    matches = sum(1 for keyword in threat_keywords if keyword in email)
    is_threat = matches >= 2
    confidence = min(90.0, matches * 12.0)
    return create_mock_response("email", is_threat, confidence, request.email_content)

@app.post("/scan/url")
async def scan_url_simple(request: SimpleURLRequest):
    """Simple URL scan"""
    url = request.url.lower()
    suspicious_patterns = ["bit.ly", "tinyurl", "login", "verify", "secure-"]
    matches = sum(1 for pattern in suspicious_patterns if pattern in url)
    is_threat = matches >= 1 or not ("https://" in url)
    confidence = min(85.0, matches * 25.0 + (0 if "https://" in url else 30))
    return create_mock_response("url", is_threat, confidence, request.url)

@app.post("/scan/image")
async def scan_image_simple(request: SimpleImageRequest):
    """Simple image scan"""
    is_threat = len(request.image_data) > 1000
    confidence = 50.0
    return create_mock_response("image", is_threat, confidence, "Image data")

@app.get("/history")
async def get_history(user_id: str = "anonymous", limit: int = 50):
    """Get scan history"""
    return {
        "user_id": user_id,
        "total_scans": 0,
        "scans": []
    }

@app.get("/stats")
async def get_stats(user_id: str = "anonymous"):
    """Get user statistics"""
    return {
        "user_id": user_id,
        "total_scans": 0,
        "threats_detected": 0,
        "safe_scans": 0,
        "average_threat_score": 0
    }

if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*60)
    print("🚀 Starting CyberSentryAI Simple Server")
    print("="*60)
    print(f"📡 API:     http://localhost:8000")
    print(f"📡 API:     http://127.0.0.1:8000")
    print(f"📚 Docs:    http://localhost:8000/docs")
    print(f"❤️  Health: http://localhost:8000/health")
    print(f"🧪 Test:    http://localhost:8000/test")
    print("="*60)
    print("⏸️  Press CTRL+C to stop\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
