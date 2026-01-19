"""
Quick Setup Script for Adaptive Learning System
Run this after implementing the adaptive learning features
"""
import os
import json

print("\n" + "="*60)
print(" "*10 + "CyberSentryAI - Adaptive Learning Setup")
print("="*60 + "\n")

# Create feedback_data directory
feedback_dir = "backend/feedback_data"
if not os.path.exists(feedback_dir):
    os.makedirs(feedback_dir)
    print("✓ Created feedback_data directory")
else:
    print("✓ feedback_data directory already exists")

# Create models/backups directory
backups_dir = "backend/models/backups"
if not os.path.exists(backups_dir):
    os.makedirs(backups_dir)
    print("✓ Created models/backups directory")
else:
    print("✓ models/backups directory already exists")

# Initialize feedback JSON files
text_feedback_file = os.path.join(feedback_dir, "text_feedback.json")
url_feedback_file = os.path.join(feedback_dir, "url_feedback.json")

if not os.path.exists(text_feedback_file):
    with open(text_feedback_file, 'w') as f:
        json.dump([], f)
    print("✓ Initialized text_feedback.json")
else:
    print("✓ text_feedback.json already exists")

if not os.path.exists(url_feedback_file):
    with open(url_feedback_file, 'w') as f:
        json.dump([], f)
    print("✓ Initialized url_feedback.json")
else:
    print("✓ url_feedback.json already exists")

print("\n" + "="*60)
print("SETUP COMPLETE! 🎉")
print("="*60)

print("\nNext Steps:")
print("\n1. Start the Flask servers:")
print("   Terminal 1: cd backend && python text_app.py")
print("   Terminal 2: cd backend && python url_app.py")
print("   Terminal 3: cd backend && python admin_app.py")

print("\n2. Open the frontend:")
print("   Open: frontend/index.html in your browser")

print("\n3. Test the feedback system:")
print("   - Analyze some text/URLs")
print("   - Click feedback buttons")
print("   - Submit reports")

print("\n4. Monitor feedback collection:")
print("   - Check: backend/feedback_data/*.json")
print("   - Or visit: http://127.0.0.1:5000/feedback-stats")

print("\n5. Retrain models when ready:")
print("   cd backend && python retrain_adaptive.py")

print("\n" + "="*60)
print("Read ADAPTIVE_LEARNING_GUIDE.md for detailed documentation")
print("="*60 + "\n")
