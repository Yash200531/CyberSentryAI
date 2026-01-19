from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle
from feedback_db import FeedbackDB

app = Flask(__name__)
CORS(app)

# Initialize feedback database
feedback_db = FeedbackDB()

# Load model
with open("models/text_scam_model.pkl", "rb") as f:
    model, vectorizer = pickle.load(f)

@app.route("/detect-text", methods=["POST"])
def detect_text():
    data = request.json
    text = data.get("text", "").lower()
    user_ip = request.remote_addr

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

    # Store prediction in feedback database for adaptive learning
    feedback_db.add_text_prediction(text, pred, float(prob), user_ip)

    return jsonify({
        "text": text,
        "is_scam": bool(pred),
        "confidence": round(prob, 3),
        "risk_level": risk,
        "explanation": explanations,
        "note": "Analyzed using Naive Bayes ML model trained on spam dataset"
    })

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
    app.run(debug=True, port=5000)
