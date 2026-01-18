from flask import Flask, request, jsonify
import pickle

app = Flask(__name__)

# Load model
with open("models/text_scam_model.pkl", "rb") as f:
    model, vectorizer = pickle.load(f)

@app.route("/detect-text", methods=["POST"])
def detect_text():
    data = request.json
    text = data.get("text", "")

    vec = vectorizer.transform([text])
    prob = model.predict_proba(vec)[0][1]
    pred = prob > 0.5

    risk = "High Risk" if prob > 0.7 else "Medium Risk" if prob > 0.4 else "Low Risk"


    return jsonify({
        "text": text,
        "is_scam": bool(pred),
        "confidence": round(prob, 3),
        "risk_level": risk,
        "explanation": "Message shows scam patterns like urgency, financial threat or impersonation"
    })

if __name__ == "__main__":
    app.run(debug=True)
