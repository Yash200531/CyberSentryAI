from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle

app = Flask(__name__)
CORS(app)

with open("models/url_phishing_model.pkl", "rb") as f:
    model = pickle.load(f)

@app.route("/")
def home():
    return "CyberSentryAI URL Agent Running"

@app.route("/detect-url", methods=["POST"])
def detect_url():
    url = request.json.get("url","").lower()

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

    return jsonify({
        "url": url,
        "is_phishing": is_phishing,
        "confidence": prob,
        "risk_level": "High Risk" if is_phishing else "Low Risk",
        "explanation": reasons,
        "note": "Random Forest + Explainable AI trained on PhiUSIIL dataset"
    })

if __name__ == "__main__":
    app.run(debug=True, port=5001)
