@echo off
echo ============================================
echo CyberSentryAI v2.0 - Quick Setup Script
echo ============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.8 or higher.
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [OK] Python found
python --version
echo.

REM Navigate to backend directory
cd backend
if errorlevel 1 (
    echo [ERROR] backend directory not found
    pause
    exit /b 1
)

echo ============================================
echo Step 1: Creating virtual environment...
echo ============================================
echo.

if exist venv (
    echo [SKIP] Virtual environment already exists
) else (
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created
)
echo.

echo ============================================
echo Step 2: Activating virtual environment...
echo ============================================
echo.

call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment
    pause
    exit /b 1
)
echo [OK] Virtual environment activated
echo.

echo ============================================
echo Step 3: Installing dependencies...
echo ============================================
echo.

pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)
echo [OK] Dependencies installed
echo.

echo ============================================
echo Step 4: Checking configuration...
echo ============================================
echo.

if exist .env (
    echo [OK] .env file exists
    findstr /C:"HF_API_TOKEN" .env >nul
    if errorlevel 1 (
        echo [WARNING] HF_API_TOKEN not found in .env
        echo Please add your Hugging Face token to .env
    ) else (
        echo [OK] HF_API_TOKEN found in .env
    )
) else (
    echo [INFO] Creating .env from template...
    copy .env.example .env
    echo [ACTION REQUIRED] Please edit .env and add your HF_API_TOKEN
    echo Get token from: https://huggingface.co/settings/tokens
)
echo.

echo ============================================
echo Step 5: Creating directories...
echo ============================================
echo.

if not exist logs mkdir logs
if not exist exports mkdir exports
if not exist feedback_data mkdir feedback_data
if not exist feedback_data\image_samples mkdir feedback_data\image_samples

echo [OK] Directories created
echo.

echo ============================================
echo Step 6: Checking models...
echo ============================================
echo.

if exist models\text_scam_model.pkl (
    echo [OK] Text model found
) else (
    echo [WARNING] Text model not found
    echo Run: python train_text_model.py
)

if exist models\url_phishing_model.pkl (
    echo [OK] URL model found
) else (
    echo [WARNING] URL model not found
    echo Run: python train_url_model.py
)
echo.

echo ============================================
echo Setup Complete!
echo ============================================
echo.
echo Next steps:
echo 1. Edit .env and add your HF_API_TOKEN
echo 2. Train models if needed (optional):
echo    python train_text_model.py
echo    python train_url_model.py
echo 3. Start the server:
echo    python start.py
echo.
echo Server will be available at:
echo - API:    http://localhost:8000
echo - Docs:   http://localhost:8000/docs
echo - Health: http://localhost:8000/health
echo.
echo Press any key to start the server now...
pause

python start.py
