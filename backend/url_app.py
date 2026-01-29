from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
import pickle
import urllib.error
import urllib.request
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

with open("models/url_phishing_model.pkl", "rb") as f:
    model = pickle.load(f)

@app.route("/")
def home():
    return "CyberSentryAI URL Agent Running"

@app.route("/detect-url", methods=["POST"])
def detect_url():
    """
    Hybrid AI URL detection endpoint
    Priority: HF Primary → Local Fallback → CyberDNA → RedTeam
    """
    url = request.json.get("url","").lower()
    user_ip = request.remote_addr

    # === STEP 1: Try Hugging Face First (Primary Intelligence) ===
    hf_result = hf_client.classify_url(url)

    # === STEP 2: Local Heuristics (Always run as verification/fallback) ===
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

    local_pred = len(reasons) >= 2
    local_prob = 0.92 if local_pred else 0.05

    # === STEP 3: Determine Primary Result ===
    if hf_result:
        # HF success - use as primary
        is_phishing = bool(hf_result["is_phishing"])
        prob = float(hf_result["confidence"])
        source = "huggingface"
        primary_label = hf_result.get("label", "unknown")
    else:
        # HF failed - fallback to local
        is_phishing = bool(local_pred)
        prob = float(local_prob)
        source = "local_fallback"
        primary_label = "phishing" if is_phishing else "safe"

    # === STEP 4: Build Base Scan Result ===
    scan_result = {
        "is_phishing": is_phishing,
        "score": prob,
        "url": url
    }

    # === STEP 5: CyberDNA Analysis (Always Run) ===
    try:
        cyber_dna_result = cyber_dna.generate_dna(
            content=url,
            content_type="url",
            scan_result=scan_result,
            redteam_result=None
        )
    except Exception as e:
        cyber_dna_result = None
        print(f"CyberDNA error: {e}")

    # === STEP 6: RedTeam Analysis (Always Run) ===
    try:
        redteam_result = redteam.analyze_url(url, scan_result)
    except Exception as e:
        redteam_result = None
        print(f"RedTeam error: {e}")

    # === STEP 7: Add model agreement to explanations ===
    if hf_result and local_pred is not None:
        if hf_result["is_phishing"] == bool(local_pred):
            reasons.append("✓ Local heuristics agree with HF primary")
        else:
            reasons.append("⚠ Local heuristics disagree with HF primary")

    # === STEP 8: Store in Feedback Database ===
    feedback_db.add_url_prediction(url, is_phishing, prob, user_ip, source=source)

    # === STEP 9: Build Hybrid Response ===
    response = {
        "url": url,
        "is_phishing": is_phishing,
        "confidence": round(prob, 3),
        "risk_level": "High Risk" if prob > 0.45 else "Medium Risk" if prob > 0.25 else "Low Risk",
        "explanation": reasons,
        "source": source,
        "architecture": "hybrid_ai",

        # Hugging Face Primary Results
        "hf_primary": {
            "available": hf_result is not None,
            "is_phishing": hf_result["is_phishing"] if hf_result else None,
            "confidence": round(hf_result["confidence"], 3) if hf_result else None,
            "label": hf_result.get("label") if hf_result else None,
            "model": hf_client.url_model if hf_result else None
        } if hf_result else {
            "available": False,
            "reason": "API unavailable or timeout"
        },

        # Local Heuristic Verification
        "local_verification": {
            "is_phishing": bool(local_pred),
            "confidence": round(float(local_prob), 3),
            "method": "Heuristic rules + PhiUSIIL patterns"
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
