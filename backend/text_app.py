from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle

app = Flask(__name__)
CORS(app)

# Load model
with open("models/text_scam_model.pkl", "rb") as f:
    model, vectorizer = pickle.load(f)

@app.route("/detect-text", methods=["POST"])
def detect_text():
    data = request.json
    text = data.get("text", "").lower()

    vec = vectorizer.transform([text])
    prob = model.predict_proba(vec)[0][1]
    pred = prob > 0.5

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

    return jsonify({
        "text": text,
        "is_scam": bool(pred),
        "confidence": round(prob, 3),
        "risk_level": risk,
        "explanation": explanations,
        "note": "Analyzed using Naive Bayes ML model trained on spam dataset"
    })

if __name__ == "__main__":
    app.run(debug=True, port=5000)
