# 🚀 How to Run CyberSentryAI

Complete step-by-step guide to start the CyberSentryAI Threat Detection Platform.

---

## 📋 Prerequisites

Make sure you have installed:
- **Python 3.8+** 
- **Node.js 16+**
- **Git**

---

## ⚙️ Setup (One-Time)

### 1️⃣ Activate Virtual Environment

Open terminal in the project root folder:

```bash
# Windows PowerShell
.\venv\Scripts\Activate

# macOS/Linux
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt.

### 2️⃣ Install Python Dependencies (if not already installed)

```bash
pip install flask flask-cors scikit-learn pandas numpy
```

### 3️⃣ Install Frontend Dependencies (if not already installed)

```bash
cd frontend
npm install
cd ..
```

---

## 🎬 Starting the Application

You need to run **4 servers** simultaneously (Text, URL, Image, and Frontend). Follow these steps:

### 🔴 Terminal 1: Text Detection API

```bash
# Step 1: Activate virtual environment
.\venv\Scripts\Activate

# Step 2: Navigate to backend folder
cd backend

# Step 3: Start text detection server
python text_app.py
```

**✅ Success Message:**
```
* Running on http://127.0.0.1:5000
```

**Keep this terminal running!**

---

### 🟠 Terminal 2: URL Detection API

Open a **NEW** terminal window:

```bash
# Step 1: Activate virtual environment
.\venv\Scripts\Activate

# Step 2: Navigate to backend folder
cd backend

# Step 3: Start URL detection server
python url_app.py
```

**✅ Success Message:**
```
* Running on http://127.0.0.1:5001
```

**Keep this terminal running!**

---

### 🟡 Terminal 3: Image Detection API (Hugging Face)

> ℹ️ **Requires Hugging Face API Token**
>
> 1. Create a token at https://huggingface.co/settings/tokens
> 2. Set it before launching the server:
> ```powershell
> setx HF_API_TOKEN "hf_your_token_here"
> ```
> (Close & reopen terminal so the variable loads.)

```bash
# Step 1: Activate virtual environment
.\venv\Scripts\Activate

# Step 2: Navigate to backend folder
cd backend

# Step 3: Start image detection server (Port 5003)
python image_app.py
```

**✅ Success Message:**
```
* Running on http://127.0.0.1:5003
```

#### 🧠 (Optional) Train/Refresh the Local Image Model

If you prefer to run completely offline, you can train the fallback model using the
feedback data you have labeled:

```bash
cd backend
python train_image_model.py --min-reports 2 --min-samples 6
```

- Uses `feedback_data/image_feedback.json` and the saved image samples.
- Writes the model to `models/image_deepfake_model.pkl` plus a metrics report.
- Restart `python image_app.py` afterward so the service picks up the new file (no Hugging Face token required).

### 🟢 Terminal 4: Frontend Server

Open a **FOURTH NEW** terminal window:

```bash
# Step 1: Navigate to frontend folder
cd frontend

# Step 2: Start React development server
npm run dev
```

**✅ Success Message:**
```
➜  Local:   http://localhost:3000/
```

**Keep this terminal running!**

---

## 🌐 Open the Application

Once all 3 servers are running, open your browser and go to:

```
http://localhost:3000
```

---

## 🎮 Using the Dashboard

### Text Analysis
1. Click **Text Analysis** in the sidebar
2. Try quick samples or paste your own text
3. Click **Analyze Message**
4. View results with risk level and explanations

### URL Scanner
1. Click **URL Scanner** in the sidebar
2. Try quick samples or enter your own URL
3. Click **Scan URL**
4. View phishing risk analysis

---

## 🛑 Stopping the Servers

Press `Ctrl + C` in each terminal window to stop the servers.

---

## ⚡ Quick Start (All-in-One)

If you want to start all servers quickly, you can use these commands in 4 separate terminals:

**Terminal 1:**
```bash
.\venv\Scripts\Activate; cd backend; python text_app.py
```

**Terminal 2:**
```bash
.\venv\Scripts\Activate; cd backend; python url_app.py
```

**Terminal 3 (requires HF token):**
```bash
.\venv\Scripts\Activate; cd backend; python image_app.py
```

**Terminal 4:**
```bash
cd frontend; npm run dev
```

---

## 🔧 Troubleshooting

### ❌ Port Already in Use

**Problem:** Error message says port 5000 or 5001 is already in use

**Solution (Windows):**
```bash
# Find process using the port
netstat -ano | findstr :5000

# Kill the process (replace <PID> with actual number)
taskkill /PID <PID> /F
```

---

### ❌ Module Not Found

**Problem:** `ModuleNotFoundError: No module named 'flask'`

**Solution:**
```bash
# Make sure venv is activated (you should see (venv) in prompt)
.\venv\Scripts\Activate

# Reinstall dependencies
pip install flask flask-cors scikit-learn pandas numpy
```

---

### ❌ Frontend Not Loading

**Problem:** Blank page or connection errors

**Solution:**
1. Check if all 3 servers are running (check terminal outputs)
2. Verify URLs:
   - Text API: http://127.0.0.1:5000
   - URL API: http://127.0.0.1:5001
   - Frontend: http://localhost:3000
3. Open browser console (F12) and check for errors
4. Try clearing browser cache (Ctrl + Shift + Delete)

---

### ❌ Model File Not Found

**Problem:** Error about missing `.pkl` files

**Solution:**
```bash
cd backend
python train_text_model.py
python train_url_model.py
```

---

## 📊 Server Status Check

### Check if servers are running:

**Text API (Port 5000):**
```bash
curl http://127.0.0.1:5000
# Should return 404 (normal - endpoint needs /detect-text)
```

**URL API (Port 5001):**
```bash
curl http://127.0.0.1:5001
# Should return 404 (normal - endpoint needs /detect-url)
```

**Image API (Port 5003):**
```bash
curl http://127.0.0.1:5003
# Should return 404 (normal - endpoint needs /detect-image)
```

**Frontend (Port 3000):**
Open http://localhost:3000 in browser

---

## 📁 Project Structure

```
CyberSentryAI/
├── backend/
│   ├── text_app.py       ← Text Detection API (Port 5000)
│   ├── url_app.py        ← URL Detection API (Port 5001)
│   ├── image_app.py      ← Image Detection API (Port 5003)
│   └── models/           ← ML model files (.pkl)
│
├── frontend/             ← React Application
│   ├── index.html
│   ├── package.json
│   └── ...
│
├── venv/                 ← Python virtual environment
└── STARTUP_GUIDE.md      ← This file
```

---

## 🎯 API Endpoints

### Text Detection
**Endpoint:** `POST http://127.0.0.1:5000/detect-text`

**Request:**
```json
{
  "text": "Congratulations! You won $5000. Click here to claim."
}
```

### URL Detection
**Endpoint:** `POST http://127.0.0.1:5001/detect-url`

**Request:**
```json
{
  "url": "https://suspicious-site.com"
}
```

### Image Detection (Hugging Face)
**Endpoint:** `POST http://127.0.0.1:5003/detect-image`

**Request (Base64):**
```json
{
  "image_base64": "<base64-encoded-image>"
}
```

**Request (URL):**
```json
{
  "image_url": "https://example.com/screenshot.png"
}
```

---

## 💡 Tips

- Keep all 3 terminal windows visible to monitor server logs
- Use the Quick Test Samples for instant demos
- Check the browser console (F12) if something doesn't work
- All data is stored locally in your browser (localStorage)

---

## ✅ Summary Checklist

Before starting:
- [ ] Virtual environment activated in terminal
- [ ] Flask and dependencies installed (`pip list` to check)
- [ ] Node modules installed in frontend folder

To run:
- [ ] Terminal 1: Text API running on port 5000
- [ ] Terminal 2: URL API running on port 5001  
- [ ] Terminal 3: Image API running on port 5003 (HF token set)
- [ ] Terminal 4: Frontend running on port 3000
- [ ] Browser open at http://localhost:3000

---

**Need help?** Check the troubleshooting section or open the browser console (F12) for error messages.
