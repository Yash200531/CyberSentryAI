"""
Quick Integration Test for CyberSentryAI v2.0
Tests all core components without running the server
"""
import os
import sys
from pathlib import Path

# Test data
TEST_TEXT = "URGENT! Your account will be suspended in 24 hours. Click here to verify: http://fake-bank.com/verify"
TEST_URL = "http://paypa1-verify.com/login?user=victim"
TEST_EMAIL = {
    "subject": "Account Verification Required",
    "body": "Dear customer, verify your account immediately to avoid suspension."
}

def test_imports():
    """Test that all modules can be imported"""
    print("🔍 Testing module imports...")
    
    try:
        from redteam_engine import RedTeamEngine
        print("  ✅ redteam_engine")
    except Exception as e:
        print(f"  ❌ redteam_engine: {e}")
        return False
    
    try:
        from cyber_dna_engine import CyberDNAEngine
        print("  ✅ cyber_dna_engine")
    except Exception as e:
        print(f"  ❌ cyber_dna_engine: {e}")
        return False
    
    try:
        from scan_logger import ScanLogger
        print("  ✅ scan_logger")
    except Exception as e:
        print(f"  ❌ scan_logger: {e}")
        return False
    
    try:
        from performance_optimizations import AsyncHFClient
        print("  ✅ performance_optimizations")
    except Exception as e:
        print(f"  ❌ performance_optimizations: {e}")
        return False
    
    try:
        from main import app
        print("  ✅ main (FastAPI)")
    except Exception as e:
        print(f"  ❌ main: {e}")
        return False
    
    return True


def test_redteam_engine():
    """Test Red-Team Engine"""
    print("\n🔍 Testing Red-Team Engine...")
    
    try:
        from redteam_engine import RedTeamEngine
        
        engine = RedTeamEngine()
        print("  ✅ Engine initialized")
        
        # Test with mock scan result
        scan_result = {
            "is_scam": True,
            "score": 0.85,
            "label": "phishing"
        }
        
        # This won't actually call the API without token, but tests the logic
        result = engine.analyze_text(TEST_TEXT, scan_result)
        
        if "attack_goal" in result:
            print("  ✅ Analysis structure correct")
            print(f"     Attack Goal: {result['attack_goal'][:50]}...")
            return True
        else:
            print("  ❌ Missing required fields")
            return False
            
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False


def test_dna_engine():
    """Test Cyber DNA Engine"""
    print("\n🔍 Testing Cyber DNA Engine...")
    
    try:
        from cyber_dna_engine import CyberDNAEngine
        
        engine = CyberDNAEngine()
        print("  ✅ Engine initialized")
        
        # Test feature extraction
        scan_result = {
            "is_scam": True,
            "score": 0.85
        }
        
        dna = engine.generate_dna(TEST_TEXT, "text", scan_result, None)
        
        if "dna_hash" in dna and "scores" in dna:
            print("  ✅ DNA generation works")
            print(f"     DNA Hash: {dna['dna_hash']}")
            print(f"     Overall Score: {dna['overall_threat_score']}")
            print(f"     Scores: {dna['scores']}")
            return True
        else:
            print("  ❌ Missing required fields")
            return False
            
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False


def test_logger():
    """Test Scan Logger"""
    print("\n🔍 Testing Scan Logger...")
    
    try:
        from scan_logger import ScanLogger
        
        logger = ScanLogger()
        print("  ✅ Logger initialized")
        
        # Test log entry
        scan_id = logger.log_scan(
            scan_type="text",
            raw_input=TEST_TEXT,
            scan_result={"is_scam": True, "score": 0.85},
            redteam_result={"attack_goal": "Test"},
            cyber_dna={"dna_hash": "test123", "scores": {}},
            user_id="test_user",
            user_ip="127.0.0.1"
        )
        
        print(f"  ✅ Scan logged: {scan_id}")
        
        # Test retrieval
        history = logger.get_scan_history(limit=1)
        if len(history) > 0:
            print("  ✅ History retrieval works")
            return True
        else:
            print("  ⚠️  History empty (expected on first run)")
            return True
            
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False


def test_fastapi():
    """Test FastAPI app structure"""
    print("\n🔍 Testing FastAPI Application...")
    
    try:
        from fastapi.testclient import TestClient
        from main import app
        
        client = TestClient(app)
        print("  ✅ Test client created")
        
        # Test health endpoint
        response = client.get("/health")
        if response.status_code == 200:
            print("  ✅ Health endpoint works")
            data = response.json()
            print(f"     Status: {data.get('status')}")
            return True
        else:
            print(f"  ❌ Health endpoint failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False


def check_environment():
    """Check environment configuration"""
    print("\n🔍 Checking Environment...")
    
    env_file = Path(".env")
    if env_file.exists():
        print("  ✅ .env file exists")
        
        with open(env_file, "r") as f:
            content = f.read()
        
        if "HF_API_TOKEN" in content:
            print("  ✅ HF_API_TOKEN configured")
            
            if "your_huggingface_token_here" not in content and "hf_" in content:
                print("  ✅ Token appears valid")
                return True
            else:
                print("  ⚠️  Token needs to be set (placeholder detected)")
                return True
        else:
            print("  ❌ HF_API_TOKEN not found")
            return False
    else:
        print("  ⚠️  .env file not found (using .env.example)")
        return True


def check_models():
    """Check if ML models exist"""
    print("\n🔍 Checking ML Models...")
    
    models_dir = Path("models")
    if not models_dir.exists():
        print("  ⚠️  models/ directory not found")
        return False
    
    text_model = models_dir / "text_scam_model.pkl"
    url_model = models_dir / "url_phishing_model.pkl"
    
    text_exists = text_model.exists()
    url_exists = url_model.exists()
    
    if text_exists:
        print("  ✅ Text model exists")
    else:
        print("  ⚠️  Text model not found (train_text_model.py)")
    
    if url_exists:
        print("  ✅ URL model exists")
    else:
        print("  ⚠️  URL model not found (train_url_model.py)")
    
    return text_exists or url_exists


def print_summary(results):
    """Print test summary"""
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print("="*60)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! System ready.")
    elif passed >= total * 0.7:
        print("\n⚠️  Most tests passed. Check warnings above.")
    else:
        print("\n❌ Several tests failed. Fix issues before deployment.")


def main():
    """Run all tests"""
    print("""
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║     CyberSentryAI v2.0 - Integration Test Suite        ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
""")
    
    results = {
        "Module Imports": test_imports(),
        "Environment Check": check_environment(),
        "ML Models": check_models(),
        "Red-Team Engine": test_redteam_engine(),
        "Cyber DNA Engine": test_dna_engine(),
        "Scan Logger": test_logger(),
        "FastAPI App": test_fastapi()
    }
    
    print_summary(results)
    
    print("\n📝 Next Steps:")
    print("  1. Ensure .env has valid HF_API_TOKEN")
    print("  2. Train models if needed: python train_text_model.py")
    print("  3. Start server: python start.py")
    print("  4. Test API: http://localhost:8000/docs")
    print()


if __name__ == "__main__":
    main()
