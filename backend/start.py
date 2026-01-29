"""
CyberSentryAI Startup Script
Checks dependencies, configuration, and launches the server
"""
import os
import sys
from pathlib import Path


def check_python_version():
    """Check Python version"""
    print("🔍 Checking Python version...")
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required. Current:", sys.version)
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    return True


def check_dependencies():
    """Check if dependencies are installed"""
    print("\n🔍 Checking dependencies...")
    required = [
        "fastapi",
        "uvicorn",
        "pydantic",
        "numpy",
        "sklearn",
        "flask",
        "aiohttp"
    ]
    
    missing = []
    for package in required:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - MISSING")
            missing.append(package)
    
    if missing:
        print(f"\n⚠️  Missing packages: {', '.join(missing)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    return True


def check_env_file():
    """Check if .env file exists and has required values"""
    print("\n🔍 Checking environment configuration...")
    
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found")
        print("📝 Copy .env.example to .env and add your HF_API_TOKEN")
        return False
    
    print("✅ .env file exists")
    
    # Check for required token
    with open(env_file, "r") as f:
        content = f.read()
    
    if "HF_API_TOKEN" not in content:
        print("⚠️  HF_API_TOKEN not found in .env")
        return False
    
    if "your_huggingface_token_here" in content or "hf_" not in content:
        print("⚠️  HF_API_TOKEN not configured (still has placeholder)")
        print("📝 Get your token from: https://huggingface.co/settings/tokens")
        return False
    
    print("✅ HF_API_TOKEN configured")
    return True


def check_models():
    """Check if ML models exist"""
    print("\n🔍 Checking ML models...")
    
    models_dir = Path("models")
    required_models = [
        "text_scam_model.pkl",
        "url_phishing_model.pkl"
    ]
    
    if not models_dir.exists():
        print("⚠️  models/ directory not found")
        print("📝 Train models first: python train_text_model.py && python train_url_model.py")
        return False
    
    missing = []
    for model in required_models:
        model_path = models_dir / model
        if model_path.exists():
            print(f"✅ {model}")
        else:
            print(f"❌ {model} - MISSING")
            missing.append(model)
    
    if missing:
        print(f"\n⚠️  Missing models: {', '.join(missing)}")
        print("📝 Train models first using train_*_model.py scripts")
        return False
    
    return True


def create_directories():
    """Create necessary directories"""
    print("\n🔍 Creating directories...")
    
    dirs = [
        "logs",
        "exports",
        "feedback_data",
        "feedback_data/image_samples"
    ]
    
    for dir_name in dirs:
        dir_path = Path(dir_name)
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"✅ Created {dir_name}/")
        else:
            print(f"✅ {dir_name}/ exists")
    
    return True


def print_banner():
    """Print startup banner"""
    banner = """
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║        CyberSentryAI v2.0 - Unified Threat Scanner      ║
║                                                          ║
║  🤖 Red-Team AI        | Attacker Psychology Analysis   ║
║  🧬 Cyber DNA          | Threat Fingerprinting          ║
║  🚀 FastAPI            | High-Performance Backend       ║
║  🤗 Hugging Face       | Production ML Models           ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
"""
    print(banner)


def start_server():
    """Start the FastAPI server"""
    print("\n🚀 Starting CyberSentryAI server...\n")
    print("📡 API:     http://localhost:8000")
    print("📚 Docs:    http://localhost:8000/docs")
    print("❤️  Health: http://localhost:8000/health")
    print("\n⏸️  Press CTRL+C to stop\n")
    print("=" * 60)
    
    import uvicorn
    from main import app
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )


def main():
    """Main startup sequence"""
    print_banner()
    
    # Run checks
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Environment", check_env_file),
        ("ML Models", check_models),
        ("Directories", create_directories)
    ]
    
    all_passed = True
    for name, check_func in checks:
        if not check_func():
            all_passed = False
    
    if not all_passed:
        print("\n❌ Startup checks failed. Fix issues above and try again.")
        sys.exit(1)
    
    print("\n✅ All checks passed! Starting server...")
    
    # Start server
    try:
        start_server()
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
        print("👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
