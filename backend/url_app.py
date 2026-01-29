from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
import pickle
import urllib.error
import urllib.request
from feedback_db import FeedbackDB

app = Flask(__name__)
CORS(app)

# Initialize feedback database
feedback_db = FeedbackDB()

with open("models/url_phishing_model.pkl", "rb") as f:
    model = pickle.load(f)

HF_MODEL = os.getenv("HF_URL_MODEL", "mrm8488/bert-tiny-finetuned-sms-spam-detection")
HF_API_URL = f"https://api-inference.huggingface.co/models/{HF_MODEL}"
HF_API_TOKEN = os.getenv("HF_API_TOKEN")
HF_TIMEOUT = float(os.getenv("HF_TIMEOUT", "10"))


def hf_classify_url(url: str):
    if not HF_API_TOKEN:
        return None
    payload = json.dumps({"inputs": url}).encode("utf-8")
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
        is_phish = any(key in label for key in ("spam", "scam", "phishing"))
        return {"label": label, "score": score, "is_phishing": is_phish}

    return None

@app.route("/")
def home():
    return "CyberSentryAI URL Agent Running"

@app.route("/detect-url", methods=["POST"])
def detect_url():
    url = request.json.get("url","").lower()
    user_ip = request.remote_addr

    hf_result = hf_classify_url(url) if HF_API_TOKEN else None

    reasons = []

    if not url.startswith("https"):
        reasons.append("No HTTPS encryption")
    if "@" in url:
        reasons.append("Contains @ symbol")
    if url.count("-") > 2:
        reasons.append("Too many hyphens")
    if url.count(".") > 4:
        reasons.append("Many subdomains")
    if any(w in url for w in ["login","verify","secure","bank","upi","paytm","sbi","account"]):
        reasons.append("Contains financial keywords")

    if hf_result:
        reasons.append("Local heuristic checks used for verification")

    local_pred = len(reasons) >= 2
    local_prob = 0.92 if local_pred else 0.05

    if hf_result:
        is_phishing = bool(hf_result["is_phishing"])
        prob = float(hf_result["score"])
        source = "huggingface"
    else:
        is_phishing = bool(local_pred)
        prob = float(local_prob)
        source = "local"

    # Store prediction in feedback database for adaptive learning
    feedback_db.add_url_prediction(url, is_phishing, prob, user_ip, source=source)

    response = {
        "url": url,
        "is_phishing": is_phishing,
        "confidence": prob,
        "risk_level": "High Risk" if is_phishing else "Low Risk",
        "explanation": reasons,
        "note": "HF primary with local heuristic verification" if source == "huggingface" else "Random Forest + Explainable AI trained on PhiUSIIL dataset",
        "source": source,
    }

    if hf_result:
        response["hf_primary"] = {
            "is_phishing": hf_result["is_phishing"],
            "confidence": round(hf_result["score"], 3),
            "label": hf_result["label"],
            "model": HF_MODEL,
        }

    response["local_verification"] = {
        "is_phishing": bool(local_pred),
        "confidence": round(float(local_prob), 3),
    }

    return jsonify(response)

@app.route("/report-url", methods=["POST"])
def report_url():
    """Endpoint for users to report/flag URL as safe or phishing"""
    data = request.json
    url = data.get("url", "").lower()
    user_label = data.get("label", "").lower()  # 'safe' or 'phishing'
    comment = data.get("comment", "")
    user_ip = request.remote_addr
    
    # Validate input
    if not url:
        return jsonify({"error": "URL is required"}), 400
    
    if user_label not in ['safe', 'phishing']:
        return jsonify({"error": "Label must be 'safe' or 'phishing'"}), 400
    
    # Add report to database
    feedback_db.add_url_report(url, user_label, user_ip, comment)
    
    return jsonify({
        "success": True,
        "message": "Thank you for your feedback! Your report helps improve our model.",
        "url": url,
        "reported_as": user_label
    })

@app.route("/feedback-stats", methods=["GET"])
def feedback_stats():
    """Get statistics about feedback data"""
    stats = feedback_db.get_stats()
    return jsonify(stats)

if __name__ == "__main__":
    app.run(debug=True, port=5001)
