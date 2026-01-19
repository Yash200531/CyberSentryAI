"""
Admin Dashboard API for Review and Management
Provides endpoints for admins to review pending feedback and manage the system
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from feedback_db import FeedbackDB
import os

app = Flask(__name__)
CORS(app)

# Initialize feedback database
feedback_db = FeedbackDB()

# Simple admin authentication (for production, use proper auth)
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "cybersentryai2026")

def verify_admin(password):
    """Simple password verification"""
    return password == ADMIN_PASSWORD

@app.route("/")
def home():
    return "CyberSentryAI Admin Dashboard API"

@app.route("/admin/stats", methods=["POST"])
def get_stats():
    """Get comprehensive feedback statistics"""
    data = request.json
    password = data.get("password", "")
    
    if not verify_admin(password):
        return jsonify({"error": "Unauthorized"}), 401
    
    stats = feedback_db.get_stats()
    return jsonify(stats)

@app.route("/admin/pending-reviews", methods=["POST"])
def get_pending_reviews():
    """Get all pending reviews for admin validation"""
    data = request.json
    password = data.get("password", "")
    data_type = data.get("type", "text")  # 'text' or 'url'
    
    if not verify_admin(password):
        return jsonify({"error": "Unauthorized"}), 401
    
    pending = feedback_db.get_pending_reviews(data_type)
    
    # Sort by prediction count (most queried first)
    pending_sorted = sorted(pending, key=lambda x: x['prediction_count'], reverse=True)
    
    return jsonify({
        "type": data_type,
        "count": len(pending_sorted),
        "items": pending_sorted
    })

@app.route("/admin/validate-item", methods=["POST"])
def validate_item():
    """Admin manually validates or rejects an item"""
    data = request.json
    password = data.get("password", "")
    data_type = data.get("type", "text")  # 'text' or 'url'
    identifier = data.get("identifier", "")  # The text or URL
    status = data.get("status", "validated")  # 'validated' or 'rejected'
    
    if not verify_admin(password):
        return jsonify({"error": "Unauthorized"}), 401
    
    if not identifier:
        return jsonify({"error": "Identifier is required"}), 400
    
    if status not in ['validated', 'rejected']:
        return jsonify({"error": "Status must be 'validated' or 'rejected'"}), 400
    
    feedback_db.admin_validate(data_type, identifier, status)
    
    return jsonify({
        "success": True,
        "message": f"Item {status} successfully",
        "type": data_type,
        "identifier": identifier,
        "status": status
    })

@app.route("/admin/trigger-retrain", methods=["POST"])
def trigger_retrain():
    """Trigger model retraining (in production, this would be async)"""
    data = request.json
    password = data.get("password", "")
    
    if not verify_admin(password):
        return jsonify({"error": "Unauthorized"}), 401
    
    return jsonify({
        "success": True,
        "message": "To retrain models, run: python backend/retrain_adaptive.py",
        "note": "In production, this would trigger an async retraining job"
    })

@app.route("/admin/export-feedback", methods=["POST"])
def export_feedback():
    """Export feedback data for analysis"""
    data = request.json
    password = data.get("password", "")
    data_type = data.get("type", "text")
    
    if not verify_admin(password):
        return jsonify({"error": "Unauthorized"}), 401
    
    if data_type == "text":
        feedback_data = feedback_db._load_json(feedback_db.text_feedback_file)
    else:
        feedback_data = feedback_db._load_json(feedback_db.url_feedback_file)
    
    return jsonify({
        "type": data_type,
        "count": len(feedback_data),
        "data": feedback_data
    })

if __name__ == "__main__":
    print("\n" + "="*60)
    print(" "*15 + "CYBERSENTRYAI ADMIN DASHBOARD")
    print("="*60)
    print(f"\nAdmin Password: {ADMIN_PASSWORD}")
    print("⚠️  Change ADMIN_PASSWORD environment variable for production!")
    print("\nEndpoints:")
    print("  POST /admin/stats - Get feedback statistics")
    print("  POST /admin/pending-reviews - Get pending items")
    print("  POST /admin/validate-item - Validate/reject items")
    print("  POST /admin/trigger-retrain - Trigger model retraining")
    print("  POST /admin/export-feedback - Export feedback data")
    print("\n" + "="*60 + "\n")
    
    app.run(debug=True, port=5002)
