# 🚀 CyberSentryAI - Production Deployment Guide

> **First-time production release checklist for Vercel (frontend) + Render/Railway (backend)**

---

## ✅ PRE-DEPLOYMENT CHECKLIST

### 1. **Repository Status**
- [ ] `.gitignore` excludes: `venv/`, `.env`, `__pycache__/`, `*.pyc`, `node_modules/`, `dist/`
- [ ] `.env` file NOT committed (secrets safe)
- [ ] `.env.example` has placeholder values only
- [ ] All production code committed to `main` branch
- [ ] Git repository pushed to GitHub

### 2. **Dependencies**
**Backend** ([requirements.txt](backend/requirements.txt)):
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
numpy==1.26.4
scikit-learn==1.8.0
scipy==1.11.4
flask==3.0.0
flask-cors==4.0.0
flask-jwt-extended==4.6.0
sqlalchemy==2.0.25
passlib[bcrypt]==1.7.4
aiohttp==3.9.1
python-dotenv==1.0.1
```

**Frontend** ([package.json](frontend/package.json)):
```json
{
  "dependencies": {
    "@google/genai": "^1.38.0",
    "axios": "^1.13.4",
    "jspdf": "2.5.1",
    "jspdf-autotable": "3.8.2",
    "lucide-react": "^0.562.0",
    "react": "^19.2.3",
    "react-dom": "^19.2.3",
    "react-router-dom": "^7.12.0",
    "recharts": "^3.6.0"
  }
}
```

### 3. **Build Verification**
**Backend** (local test):
```powershell
cd backend
python -m uvicorn main:app --reload
```
- [ ] Server starts on `http://localhost:8000`
- [ ] `/docs` endpoint loads (FastAPI Swagger UI)

**Frontend** (local test):
```powershell
cd frontend
npm install
npm run build
```
- [ ] Build completes without errors
- [ ] `frontend/dist/` folder created

---

## 📦 STEP 1: PUSH TO GITHUB

```powershell
# Navigate to project root
cd C:\Users\yashkumar\Desktop\Projects\CyberSentryAI

# Check git status
git status

# Add all production-ready files
git add .gitignore backend/ frontend/ datasets/ *.md

# Commit with production message
git commit -m "feat: production-ready v1.0 - hybrid AI threat detection

- Implemented hybrid intelligence (HuggingFace + local ML + rule-based)
- Added CyberDNA fingerprinting + Red Team simulation
- Created React dashboard with PDF export + scan history
- Set up FastAPI backend with JWT authentication
- Configured adaptive learning system for model retraining
- Added comprehensive .gitignore for secrets protection

Dependencies:
- Backend: FastAPI 0.104.1, scikit-learn 1.8.0, aiohttp 3.9.1
- Frontend: React 19.2.3, Vite 6.2.0, Recharts 3.6.0

Deployment: Ready for Vercel (frontend) + Render/Railway (backend)"

# Push to GitHub
git push origin main
```

**⚠️ VERIFY**: Visit GitHub repository to confirm:
- [ ] `.env` file NOT present
- [ ] `venv/` directory NOT present
- [ ] All source code visible

---

## 🌐 STEP 2: DEPLOY FRONTEND TO VERCEL

### 2.1 Connect Repository
1. Visit [vercel.com](https://vercel.com)
2. Click **"Add New" → "Project"**
3. Import your GitHub repository: `YourUsername/CyberSentryAI`
4. Select **`frontend`** folder as root directory

### 2.2 Configure Build Settings
```yaml
Framework Preset: Vite
Build Command: npm run build
Output Directory: dist
Install Command: npm install
Node Version: 18.x or 20.x
```

### 2.3 Environment Variables
Click **"Environment Variables"** and add:
```
# Google Generative AI (optional - for enhanced analysis)
VITE_GEMINI_API_KEY=your_gemini_api_key_here

# Backend API URL (will be updated after backend deployment)
VITE_BACKEND_URL=https://your-backend.onrender.com
```
**Note**: Leave `VITE_BACKEND_URL` blank for now - update after Step 3.

### 2.4 Deploy
- Click **"Deploy"**
- Wait 2-3 minutes
- Copy deployment URL (e.g., `https://cybersentryai.vercel.app`)

**Troubleshooting**:
- Build fails? Check `Node version` is 18.x+
- CORS errors? Will be fixed after backend deployment

---

## 🔧 STEP 3: DEPLOY BACKEND TO RENDER/RAILWAY

### **Option A: Render** (Recommended)

#### 3.1 Create Web Service
1. Visit [render.com](https://render.com)
2. Click **"New" → "Web Service"**
3. Connect GitHub repository
4. Select repository: `YourUsername/CyberSentryAI`
5. **Root Directory**: `backend`

#### 3.2 Configure Service
```yaml
Name: cybersentryai-backend
Region: Oregon (US West) or closest to you
Branch: main
Runtime: Python 3
Build Command: pip install -r requirements.txt
Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
```

#### 3.3 Environment Variables
Add these in Render dashboard:
```bash
# HuggingFace API (REQUIRED)
HF_API_TOKEN=your_hf_token_from_https://huggingface.co/settings/tokens

# Model Configuration
HF_TEXT_MODEL=mrm8488/bert-tiny-finetuned-sms-spam-detection
HF_URL_MODEL=distilbert-base-uncased-finetuned-sst-2-english
HF_IMAGE_MODEL=dima806/deepfake_vs_real_image_detection
HF_REDTEAM_MODEL=HuggingFaceH4/zephyr-7b-beta
HF_EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Performance
HF_TIMEOUT=15.0
HF_MIN_PROB=0.25
HF_MAX_PROB=0.45

# Server Config
API_HOST=0.0.0.0
API_PORT=10000

# Adaptive Learning
RETRAIN_ENABLED=true
RETRAIN_INTERVAL_MIN=1440

# Admin (CHANGE THIS!)
ADMIN_PASSWORD=your_secure_admin_password_here
```

#### 3.4 Deploy
- Click **"Create Web Service"**
- Wait 5-10 minutes for initial build
- Copy service URL (e.g., `https://cybersentryai-backend.onrender.com`)

**Free Tier Limits**:
- ⚠️ Render free tier spins down after 15 minutes of inactivity
- First request after spin-down takes ~30 seconds
- 750 hours/month free (sufficient for development)

---

### **Option B: Railway** (Alternative)

#### 3.1 Create Project
1. Visit [railway.app](https://railway.app)
2. Click **"New Project" → "Deploy from GitHub repo"**
3. Select `YourUsername/CyberSentryAI`
4. Click **"Deploy Now"**

#### 3.2 Configure Service
Railway auto-detects Python. Set:
```yaml
Root Directory: backend
Build Command: pip install -r requirements.txt
Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
```

#### 3.3 Environment Variables
Same as Render (Step 3.3 above)

#### 3.4 Generate Domain
- Click **"Settings" → "Networking" → "Generate Domain"**
- Copy domain (e.g., `cybersentryai-backend.up.railway.app`)

**Free Tier Limits**:
- $5 credit/month (~500 hours server time)
- No cold starts (always running)

---

## 🔗 STEP 4: CONNECT FRONTEND TO BACKEND

### 4.1 Update Vercel Environment Variables
1. Go to Vercel Dashboard → Your Project → **Settings** → **Environment Variables**
2. Update `VITE_BACKEND_URL`:
   ```
   VITE_BACKEND_URL=https://cybersentryai-backend.onrender.com
   ```
   (Or Railway URL if using Railway)

### 4.2 Redeploy Frontend
- Click **"Deployments" → "Redeploy"** (forces rebuild with new env var)

---

## 🛡️ STEP 5: CONFIGURE CORS (Backend)

**If you see CORS errors**, add your Vercel domain to backend CORS whitelist:

Edit `backend/main.py`:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Local dev
        "https://cybersentryai.vercel.app",  # Your Vercel domain
        "https://*.vercel.app"  # Allow preview deployments
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Commit and push changes - Render/Railway auto-redeploys.

---

## 📋 STEP 6: VERIFY DEPLOYMENT

### 6.1 Backend Health Check
Visit: `https://cybersentryai-backend.onrender.com/docs`
- [ ] FastAPI Swagger UI loads
- [ ] `/health` endpoint returns `{"status": "ok"}`

### 6.2 Frontend Test
Visit: `https://cybersentryai.vercel.app`
- [ ] Landing page loads
- [ ] Login works (create test account)
- [ ] Scan page can submit URLs/text
- [ ] Results display correctly
- [ ] PDF export works

---

## 🔧 ENVIRONMENT VARIABLES REFERENCE

### **Backend** (Render/Railway)
| Variable | Purpose | Example |
|----------|---------|---------|
| `HF_API_TOKEN` | HuggingFace authentication | `hf_xxxxxxxxxxxxx` |
| `HF_TEXT_MODEL` | Spam/scam detection model | `mrm8488/bert-tiny-finetuned-sms-spam-detection` |
| `HF_URL_MODEL` | Phishing URL detection | `distilbert-base-uncased-finetuned-sst-2-english` |
| `HF_IMAGE_MODEL` | Deepfake/fake image detection | `dima806/deepfake_vs_real_image_detection` |
| `HF_REDTEAM_MODEL` | Red Team simulation | `HuggingFaceH4/zephyr-7b-beta` |
| `ADMIN_PASSWORD` | Admin panel access | **Change from default!** |

### **Frontend** (Vercel)
| Variable | Purpose | Example |
|----------|---------|---------|
| `VITE_BACKEND_URL` | Backend API endpoint | `https://cybersentryai-backend.onrender.com` |
| `VITE_GEMINI_API_KEY` | (Optional) Google AI enhancement | `AIzaSyC...` |

---

## 🚨 TROUBLESHOOTING

### Frontend Issues
**"Failed to fetch" errors**:
- Check `VITE_BACKEND_URL` in Vercel settings
- Verify CORS configuration in backend
- Check browser console for specific error

**Build fails**:
- Verify Node version is 18.x or 20.x
- Check all dependencies install: `npm install --legacy-peer-deps`

### Backend Issues
**"Module not found" errors**:
- Check all packages in `requirements.txt`
- Verify Python version is 3.11+ in Render/Railway settings

**HuggingFace API timeout**:
- Free tier has rate limits - wait 60 seconds and retry
- Consider upgrading to HF Pro ($9/month) for higher limits

**Cold starts (Render free tier)**:
- First request after 15 min takes ~30 seconds
- Solution: Upgrade to paid tier ($7/month) for always-on

---

## 📊 MONITORING & MAINTENANCE

### Render Dashboard
- **Logs**: Click service → "Logs" tab
- **Metrics**: View CPU/RAM usage
- **Events**: Track deploys & restarts

### Vercel Dashboard
- **Analytics**: Page views, load times
- **Logs**: Function logs (if using serverless)
- **Deployments**: Auto-deploy on `git push`

---

## 🎯 PRODUCTION CHECKLIST

Before announcing to users:
- [ ] Change `ADMIN_PASSWORD` from default
- [ ] Test all scan types (text, URL, image, email)
- [ ] Verify PDF export downloads correctly
- [ ] Check responsive design on mobile
- [ ] Monitor backend logs for errors
- [ ] Set up uptime monitoring (e.g., UptimeRobot)
- [ ] Create backup of `auth.db` (user accounts)

---

## 📞 SUPPORT

**Backend Logs**:
```powershell
# Render
render logs -f cybersentryai-backend

# Railway
railway logs
```

**Frontend Logs**:
Vercel Dashboard → Deployments → Click deployment → "Function Logs"

**Need Help?**
- Backend API docs: `https://your-backend-url.com/docs`
- HuggingFace docs: https://huggingface.co/docs
- Vercel docs: https://vercel.com/docs
- Render docs: https://render.com/docs
- Railway docs: https://docs.railway.app

---

**🎉 Congratulations!** Your CyberSentryAI platform is now live in production!

Frontend: `https://cybersentryai.vercel.app`  
Backend: `https://cybersentryai-backend.onrender.com`  
API Docs: `https://cybersentryai-backend.onrender.com/docs`
