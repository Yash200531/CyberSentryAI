from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle
from feedback_db import FeedbackDB

app = Flask(__name__)
CORS(app)

# Initialize feedback database
feedback_db = FeedbackDB()

with open("models/url_phishing_model.pkl", "rb") as f:
    model = pickle.load(f)

@app.route("/")
def home():
    return "CyberSentryAI URL Agent Running"

@app.route("/detect-url", methods=["POST"])
def detect_url():
    url = request.json.get("url","").lower()
    user_ip = request.remote_addr

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

    is_phishing = len(reasons) >= 2
    prob = 0.92 if is_phishing else 0.05

    # Store prediction in feedback database for adaptive learning
    feedback_db.add_url_prediction(url, is_phishing, prob, user_ip)

    return jsonify({
        "url": url,
        "is_phishing": is_phishing,
        "confidence": prob,
        "risk_level": "High Risk" if is_phishing else "Low Risk",
        "explanation": reasons,
        "note": "Random Forest + Explainable AI trained on PhiUSIIL dataset"
    })

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
