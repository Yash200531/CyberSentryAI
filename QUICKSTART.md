# 🚀 Quick Start - Adaptive Learning System

## Start All Services (3 Terminals)

### Terminal 1 - Text Analysis Service
```bash
cd c:\Users\yashkumar\Desktop\Projects\CyberSentryAI\backend
python text_app.py
```
**Runs on:** http://127.0.0.1:5000

---

### Terminal 2 - URL Analysis Service
```bash
cd c:\Users\yashkumar\Desktop\Projects\CyberSentryAI\backend
python url_app.py
```
**Runs on:** http://127.0.0.1:5001

---

### Terminal 3 - Admin Dashboard (Optional)
```bash
cd c:\Users\yashkumar\Desktop\Projects\CyberSentryAI\backend
python admin_app.py
```
**Runs on:** http://127.0.0.1:5002  
**Password:** `cybersentryai2026`

---

## Open Frontend

1. Navigate to: `c:\Users\yashkumar\Desktop\Projects\CyberSentryAI\frontend\`
2. Open `index.html` in your browser
3. Or use: `start frontend\index.html`

---

## Test the Adaptive Learning

### 1. Analyze Some Text
- Paste a message in the text box
- Click "Analyze Message"
- See results

### 2. Provide Feedback
After analysis, you'll see:
```
🤝 Help Improve Our AI
Was this prediction correct?

[✓ Correct] [✗ Incorrect] [🚩 Report/Flag]
```

**Try each button:**
- **Correct**: Quick feedback that model was right
- **Incorrect**: Quick feedback that model was wrong  
- **Report/Flag**: Detailed report with custom label + comment

### 3. Submit a Report
Click **"🚩 Report/Flag"** → Modal opens:
- Choose: Safe or Threat
- Add comment (optional)
- Click "Submit Report"
- See confirmation toast! ✅

### 4. Check Feedback Storage
```bash
# View stored feedback
cat backend\feedback_data\text_feedback.json
cat backend\feedback_data\url_feedback.json

# Or via API
curl http://127.0.0.1:5000/feedback-stats
```

### 5. Retrain Model (After Collecting Feedback)
```bash
cd backend
python retrain_adaptive.py
```

**Output will show:**
- Original dataset size
- New validated feedback samples
- Training progress
- Model accuracy metrics
- Backup location
- Success message

### 6. Restart Servers to Load New Model
After retraining, restart Terminal 1 & 2:
- Press `Ctrl+C` to stop
- Run `python text_app.py` again
- Run `python url_app.py` again

---

## Quick Test Script

```bash
# Test text analysis
curl -X POST http://127.0.0.1:5000/detect-text ^
  -H "Content-Type: application/json" ^
  -d "{\"text\": \"Urgent! Your bank account suspended. Click here now!\"}"

# Submit feedback report
curl -X POST http://127.0.0.1:5000/report-text ^
  -H "Content-Type: application/json" ^
  -d "{\"text\": \"Urgent bank alert\", \"label\": \"scam\", \"comment\": \"Phishing attempt\"}"

# Check stats
curl http://127.0.0.1:5000/feedback-stats
```

---

## Admin Dashboard Quick Test

```bash
# Get statistics
curl -X POST http://127.0.0.1:5002/admin/stats ^
  -H "Content-Type: application/json" ^
  -d "{\"password\": \"cybersentryai2026\"}"

# View pending reviews
curl -X POST http://127.0.0.1:5002/admin/pending-reviews ^
  -H "Content-Type: application/json" ^
  -d "{\"password\": \"cybersentryai2026\", \"type\": \"text\"}"
```

---

## Validation Threshold Test

To see auto-validation in action:

1. **Submit same report 3 times** (simulate 3 different users):
   ```bash
   curl -X POST http://127.0.0.1:5000/report-text ^
     -H "Content-Type: application/json" ^
     -d "{\"text\": \"test message\", \"label\": \"scam\"}"
   
   # Run this 3 times
   ```

2. **Check status** in `backend/feedback_data/text_feedback.json`:
   ```json
   {
     "text": "test message",
     "status": "validated",  // ← Changed from "pending"!
     "user_reports": [...]  // 3 reports
   }
   ```

3. **Now retrain**:
   ```bash
   python backend\retrain_adaptive.py
   ```

4. The "test message" will be **included in training data**!

---

## Troubleshooting

### Issue: Servers won't start
```bash
# Check if ports are in use
netstat -ano | findstr :5000
netstat -ano | findstr :5001
netstat -ano | findstr :5002

# Kill process if needed
taskkill /PID <process_id> /F
```

### Issue: Feedback not saving
```bash
# Check directory exists
dir backend\feedback_data\

# Check file permissions
type backend\feedback_data\text_feedback.json
```

### Issue: Retraining fails
```bash
# Make sure there's validated feedback
python -c "from backend.feedback_db import FeedbackDB; db = FeedbackDB(); print(db.get_stats())"
```

---

## File Locations

```
Configuration:
├── Admin Password: line 15 of backend/admin_app.py
├── Validation Threshold: line 118 of backend/feedback_db.py (default: 3)
└── Retraining Schedule: You set this up (manual or cron/Task Scheduler)

Data Storage:
├── Feedback Data: backend/feedback_data/*.json
├── Model Backups: backend/models/backups/
└── Current Models: backend/models/*.pkl

Documentation:
├── ADAPTIVE_LEARNING_GUIDE.md - Full documentation
├── IMPLEMENTATION_SUMMARY.md - What was built
└── This file - Quick start guide
```

---

## Next Steps

1. ✅ **Test the system** - Submit feedback, see it work
2. ✅ **Collect feedback** - Use it for a few days
3. ✅ **Retrain model** - Run retraining script
4. ✅ **Measure improvement** - Compare accuracy before/after
5. ✅ **Schedule retraining** - Set up periodic retraining
6. ✅ **Monitor metrics** - Track validation rate, accuracy

---

## Production Deployment

When ready for production:

1. **Switch to proper database** (PostgreSQL)
2. **Add authentication** (JWT tokens)
3. **Implement rate limiting**
4. **Set up monitoring** (accuracy tracking)
5. **Automate retraining** (Celery/Airflow)
6. **Add A/B testing** (gradual rollout)
7. **Change admin password** (environment variable)

---

## Need Help?

- Read: `ADAPTIVE_LEARNING_GUIDE.md` (comprehensive guide)
- Check: Code comments in each file
- Review: `IMPLEMENTATION_SUMMARY.md` (what was built)

---

**🎉 You're all set! Your AI has a brain now! 🧠🤖**

Start testing the adaptive learning system and watch your model get smarter! 🚀
