from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
import pickle
import re
import sys
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path
from feedback_db import FeedbackDB
from hf_client import get_hf_client
from cyber_dna_engine import CyberDNAEngine
from redteam_engine import RedTeamEngine

app = Flask(__name__)
CORS(app)

# Initialize intelligent engines
feedback_db = FeedbackDB()
hf_client = get_hf_client()
cyber_dna = CyberDNAEngine()
redteam = RedTeamEngine()

# Load model
with open("models/text_scam_model.pkl", "rb") as f:
    model, vectorizer = pickle.load(f)

METRICS_PATH = Path("models/text_model_metrics.json")
if METRICS_PATH.exists():
    with open(METRICS_PATH, "r", encoding="utf-8") as f:
        metrics = json.load(f)
    best_threshold = float(metrics.get("best_threshold", 0.5))
else:
    best_threshold = 0.5

RETRAIN_ENABLED = os.getenv("RETRAIN_ENABLED", "true").lower() == "true"
RETRAIN_INTERVAL_MIN = int(os.getenv("RETRAIN_INTERVAL_MIN", "1440"))
BASE_DIR = Path(__file__).resolve().parent


def normalize_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"https?://\S+|www\.\S+", " <URL> ", text)
    text = re.sub(r"\b[\w\.-]+@[\w\.-]+\.\w+\b", " <EMAIL> ", text)
    text = re.sub(r"\b\+?\d[\d\s\-().]{7,}\b", " <PHONE> ", text)
    text = re.sub(r"\b\d+(?:[.,]\d+)?\b", " <NUM> ", text)
    text = re.sub(r"[$₹€£]", " <CUR> ", text)
    text = re.sub(r"[^\w\s<>]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def start_retrain_scheduler():
    if not RETRAIN_ENABLED:
        return

    def _loop():
        while True:
            time.sleep(max(RETRAIN_INTERVAL_MIN, 10) * 60)
            try:
                subprocess_args = [sys.executable, "retrain_adaptive.py"]
                with open(os.devnull, "w") as devnull:
                    import subprocess
                    subprocess.Popen(subprocess_args, cwd=str(BASE_DIR), stdout=devnull, stderr=devnull)
            except Exception:
                pass

    thread = threading.Thread(target=_loop, daemon=True)
    thread.start()

@app.route("/detect-text", methods=["POST"])
def detect_text():
    """
    Hybrid AI text detection endpoint
    Priority: HF Primary → Local Fallback → CyberDNA → RedTeam
    """
    data = request.json
    raw_text = data.get("text", "")
    text = normalize_text(raw_text)
    user_ip = request.remote_addr

    # === STEP 1: Try Hugging Face First (Primary Intelligence) ===
    hf_result = hf_client.classify_text(raw_text)
    
    # === STEP 2: Local Model (Always run as verification/fallback) ===
    classes = list(getattr(model, "classes_", []))
    pos_label = "spam" if "spam" in classes else (classes[-1] if classes else "spam")
    pos_index = classes.index(pos_label) if pos_label in classes else 1
    
    vec = vectorizer.transform([text])
    local_prob = model.predict_proba(vec)[0][pos_index]
    local_pred = local_prob >= best_threshold
    
    # === STEP 3: Determine Primary Result ===
    if hf_result:
        # HF success - use as primary
        pred = bool(hf_result["is_scam"])
        prob = float(hf_result["confidence"])
        source = "huggingface"
        primary_label = hf_result.get("label", "unknown")
    else:
        # HF failed - fallback to local
        pred = bool(local_pred)
        prob = float(local_prob)
        source = "local_fallback"
        primary_label = "scam" if pred else "safe"
    
    # === STEP 4: Build Base Scan Result ===
    scan_result = {
        "is_scam": pred,
        "score": prob,
        "text": raw_text
    }
    
    # === STEP 5: CyberDNA Analysis (Always Run) ===
    try:
        cyber_dna_result = cyber_dna.generate_dna(
            content=raw_text,
            content_type="text",
            scan_result=scan_result,
            redteam_result=None  # Will add after redteam runs
        )
    except Exception as e:
        cyber_dna_result = None
        print(f"CyberDNA error: {e}")
    
    # === STEP 6: RedTeam Analysis (Always Run) ===
    try:
        redteam_result = redteam.analyze_text(raw_text, scan_result)
    except Exception as e:
        redteam_result = None
        print(f"RedTeam error: {e}")
    
    # === STEP 7: Generate Explanations ===
    risk = "High Risk" if prob > 0.45 else "Medium Risk" if prob > 0.25 else "Low Risk"
    explanations = []
    
    if pred:  # If it's a scam
        # Check for urgency
        urgency_words = ["urgent", "immediately", "now", "today", "expire", "act fast", "limited time", "hurry"]
        if any(word in text for word in urgency_words):
            explanations.append("Contains urgency indicators to pressure immediate action")
        
        # Check for financial threats
        financial_words = ["bank", "account", "payment", "money", "cash", "prize", "won", "claim", "refund", "tax", "suspended"]
        if any(word in text for word in financial_words):
            explanations.append("References financial terms commonly used in scams")
        
        # Check for links
        if "http" in text or "bit.ly" in text or "click here" in text or "link" in text:
            explanations.append("Contains suspicious links or prompts to click")
        
        # Check for personal info requests
        personal_words = ["verify", "confirm", "update", "details", "password", "pin", "otp", "card"]
        if any(word in text for word in personal_words):
            explanations.append("Requests personal or sensitive information")
        
        # Check for rewards/prizes
        prize_words = ["congratulations", "winner", "won", "prize", "lottery", "selected", "lucky"]
        if any(word in text for word in prize_words):
            explanations.append("Offers unrealistic prizes or rewards")
        
        # Check for impersonation
        org_words = ["sbi", "hdfc", "icici", "paytm", "google", "amazon", "government", "tax department", "police"]
        if any(word in text for word in org_words):
            explanations.append("Impersonates legitimate organizations")
        
        # If no specific patterns found, add generic message
        if not explanations:
            explanations.append("Multiple suspicious patterns detected by ML model")
    else:  # Safe message
        explanations.append("No suspicious scam patterns detected")
        explanations.append("Message appears to be legitimate communication")
    
    # Add model agreement/disagreement
    if hf_result and local_pred is not None:
        if hf_result["is_scam"] == bool(local_pred):
            explanations.append("✓ Local model agrees with HF primary")
        else:
            explanations.append("⚠ Local model disagrees with HF primary")
    
    # === STEP 8: Store in Feedback Database ===
    feedback_db.add_text_prediction(text, pred, float(prob), user_ip, source=source)
    
    # === STEP 9: Build Hybrid Response ===
    response = {
        "text": raw_text,
        "is_scam": bool(pred),
        "confidence": round(prob, 3),
        "risk_level": risk,
        "explanation": explanations,
        "source": source,
        "architecture": "hybrid_ai",
        
        # Hugging Face Primary Results
        "hf_primary": {
            "available": hf_result is not None,
            "is_scam": hf_result["is_scam"] if hf_result else None,
            "confidence": round(hf_result["confidence"], 3) if hf_result else None,
            "label": hf_result.get("label") if hf_result else None,
            "model": hf_client.text_model if hf_result else None
        } if hf_result else {
            "available": False,
            "reason": "API unavailable or timeout"
        },
        
        # Local Model Verification
        "local_verification": {
            "is_scam": bool(local_pred),
            "confidence": round(float(local_prob), 3),
            "threshold": round(float(best_threshold), 3),
            "model": "SVM with TF-IDF"
        },
        
        # CyberDNA Fingerprint
        "cyber_dna": cyber_dna_result if cyber_dna_result else {
            "available": False,
            "reason": "Analysis failed"
        },
        
        # RedTeam Intelligence
        "redteam": redteam_result if redteam_result else {
            "available": False,
            "reason": "Analysis failed"
        },
        
        "note": f"Hybrid AI: {'HF primary + local verification + CyberDNA + RedTeam' if hf_result else 'Local fallback + CyberDNA + RedTeam'}"
    }

    return jsonify(response)

@app.route("/report-text", methods=["POST"])
def report_text():
    """Endpoint for users to report/flag text as safe or scam"""
    data = request.json
    text = data.get("text", "").lower()
    user_label = data.get("label", "").lower()  # 'safe' or 'scam'
    comment = data.get("comment", "")
    user_ip = request.remote_addr
    
    # Validate input
    if not text:
        return jsonify({"error": "Text is required"}), 400
    
    if user_label not in ['safe', 'scam']:
        return jsonify({"error": "Label must be 'safe' or 'scam'"}), 400
    
    # Add report to database
    feedback_db.add_text_report(text, user_label, user_ip, comment)
    
    return jsonify({
        "success": True,
        "message": "Thank you for your feedback! Your report helps improve our model.",
        "text": text,
        "reported_as": user_label
    })

@app.route("/feedback-stats", methods=["GET"])
def feedback_stats():
    """Get statistics about feedback data"""
    stats = feedback_db.get_stats()
    return jsonify(stats)

if __name__ == "__main__":
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true" or not app.debug:
        start_retrain_scheduler()
    app.run(debug=True, port=5000)
