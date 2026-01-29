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

app = Flask(__name__)
CORS(app)

# Initialize feedback database
feedback_db = FeedbackDB()

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

HF_MODEL = os.getenv("HF_TEXT_MODEL", "mrm8488/bert-tiny-finetuned-sms-spam-detection")
HF_API_URL = f"https://api-inference.huggingface.co/models/{HF_MODEL}"
HF_API_TOKEN = os.getenv("HF_API_TOKEN")
HF_MIN_PROB = float(os.getenv("HF_MIN_PROB", "0.35"))
HF_MAX_PROB = float(os.getenv("HF_MAX_PROB", "0.65"))
HF_TIMEOUT = float(os.getenv("HF_TIMEOUT", "10"))

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


def hf_classify(text: str):
    if not HF_API_TOKEN:
        return None
    payload = json.dumps({"inputs": text}).encode("utf-8")
    req = urllib.request.Request(
        HF_API_URL,
        data=payload,
        headers={
            "Authorization": f"Bearer {HF_API_TOKEN}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=HF_TIMEOUT) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, ValueError):
        return None

    if isinstance(data, dict) and data.get("error"):
        return None

    if isinstance(data, list) and data and isinstance(data[0], list):
        data = data[0]

    if isinstance(data, list) and data:
        best = max(data, key=lambda item: item.get("score", 0))
        label = str(best.get("label", "")).lower()
        score = float(best.get("score", 0))
        is_spam = any(key in label for key in ("spam", "scam", "phishing"))
        return {"label": label, "score": score, "is_scam": is_spam}

    return None


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
    data = request.json
    raw_text = data.get("text", "")
    text = normalize_text(raw_text)
    user_ip = request.remote_addr

    classes = list(getattr(model, "classes_", []))
    pos_label = "spam" if "spam" in classes else (classes[-1] if classes else "spam")
    pos_index = classes.index(pos_label) if pos_label in classes else 1

    vec = vectorizer.transform([text])
    local_prob = model.predict_proba(vec)[0][pos_index]
    local_pred = local_prob >= best_threshold

    hf_result = hf_classify(raw_text) if HF_API_TOKEN else None
    if hf_result:
        pred = bool(hf_result["is_scam"])
        prob = float(hf_result["score"])
        source = "huggingface"
    else:
        pred = bool(local_pred)
        prob = float(local_prob)
        source = "local"

    risk = "High Risk" if prob > 0.7 else "Medium Risk" if prob > 0.4 else "Low Risk"

    # Generate detailed explanations based on content
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

    if hf_result and local_pred is not None:
        if hf_result["is_scam"] == bool(local_pred):
            explanations.append("Local model agrees with HF primary")
        else:
            explanations.append("Local model disagrees with HF primary")

    # Store prediction in feedback database for adaptive learning
    feedback_db.add_text_prediction(text, pred, float(prob), user_ip, source=source)

    response = {
        "text": raw_text,
        "is_scam": bool(pred),
        "confidence": round(prob, 3),
        "risk_level": risk,
        "explanation": explanations,
        "note": "Analyzed using HF primary with local SVM verification" if source == "huggingface" else "Analyzed using calibrated SVM model trained on spam dataset",
        "source": source,
    }

    if hf_result:
        response["hf_primary"] = {
            "is_scam": hf_result["is_scam"],
            "confidence": round(hf_result["score"], 3),
            "label": hf_result["label"],
            "model": HF_MODEL,
        }

    response["local_verification"] = {
        "is_scam": bool(local_pred),
        "confidence": round(float(local_prob), 3),
        "threshold": round(float(best_threshold), 3),
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
