"""Test script for OTP email verification flow."""
import sys
import os
from datetime import datetime, timedelta

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from auth_models import SessionLocal, User, Role, init_db
from sqlalchemy import func


def test_otp_generation():
    """Test OTP generation and database storage."""
    print("=" * 60)
    print("Test 1: OTP Generation and Storage")
    print("=" * 60)
    
    init_db()
    
    with SessionLocal() as session:
        # Get the admin user
        admin_email = "admin@cyber.in"
        user = session.query(User).filter(func.lower(User.email) == admin_email).first()
        
        if not user:
            print(f"❌ User {admin_email} not found")
            return False
        
        print(f"✓ Found user: {user.email}")
        print(f"  - Email verified: {user.is_email_verified}")
        print(f"  - OTP code: {user.otp_code}")
        print(f"  - OTP expiry: {user.otp_expiry}")
        
        # Set OTP
        test_otp = "123456"
        user.otp_code = test_otp
        user.otp_expiry = datetime.utcnow() + timedelta(minutes=10)
        user.is_email_verified = False
        session.commit()
        
        print(f"\n✓ OTP set successfully")
        print(f"  - OTP code: {user.otp_code}")
        print(f"  - Expiry: {user.otp_expiry}")
        
        return True


def test_otp_verification():
    """Test OTP verification logic."""
    print("\n" + "=" * 60)
    print("Test 2: OTP Verification")
    print("=" * 60)
    
    with SessionLocal() as session:
        admin_email = "admin@cyber.in"
        user = session.query(User).filter(func.lower(User.email) == admin_email).first()
        
        if not user:
            print(f"❌ User {admin_email} not found")
            return False
        
        print(f"✓ Testing verification for: {user.email}")
        
        # Test valid OTP
        test_otp = "123456"
        if user.otp_code == test_otp:
            print(f"✓ OTP matches: {test_otp}")
        else:
            print(f"❌ OTP mismatch: expected {test_otp}, got {user.otp_code}")
            return False
        
        # Test expiry
        if datetime.utcnow() < user.otp_expiry:
            print(f"✓ OTP not expired (expires at {user.otp_expiry})")
        else:
            print(f"❌ OTP expired")
            return False
        
        # Verify email
        user.is_email_verified = True
        user.otp_code = None
        user.otp_expiry = None
        session.commit()
        
        print(f"✓ Email verified successfully")
        print(f"  - Email verified: {user.is_email_verified}")
        print(f"  - OTP cleared: {user.otp_code is None}")
        
        return True


def test_otp_expiry():
    """Test OTP expiry logic."""
    print("\n" + "=" * 60)
    print("Test 3: OTP Expiry")
    print("=" * 60)
    
    with SessionLocal() as session:
        analyst_email = "analyst@co.in"
        user = session.query(User).filter(func.lower(User.email) == analyst_email).first()
        
        if not user:
            print(f"❌ User {analyst_email} not found")
            return False
        
        # Set expired OTP
        user.otp_code = "654321"
        user.otp_expiry = datetime.utcnow() - timedelta(minutes=1)  # Expired 1 minute ago
        user.is_email_verified = False
        session.commit()
        
        print(f"✓ Set expired OTP for: {user.email}")
        print(f"  - OTP code: {user.otp_code}")
        print(f"  - Expiry: {user.otp_expiry}")
        
        # Check expiry
        if datetime.utcnow() > user.otp_expiry:
            print(f"✓ OTP correctly detected as expired")
        else:
            print(f"❌ OTP should be expired")
            return False
        
        return True


def test_email_service():
    """Test email service initialization."""
    print("\n" + "=" * 60)
    print("Test 4: Email Service")
    print("=" * 60)
    
    try:
        from email_service import email_service
        
        print(f"✓ Email service initialized")
        print(f"  - SMTP Host: {email_service.smtp_host}")
        print(f"  - SMTP Port: {email_service.smtp_port}")
        print(f"  - Enabled: {email_service.enabled}")
        
        if not email_service.enabled:
            print(f"  ⚠ Email service disabled (SMTP credentials not configured)")
            print(f"    This is expected in development mode")
        
        return True
    except Exception as e:
        print(f"❌ Email service error: {e}")
        return False


def main():
    """Run all tests."""
    print("\n🧪 Starting OTP Verification Tests\n")
    
    tests = [
        test_otp_generation,
        test_otp_verification,
        test_otp_expiry,
        test_email_service,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"\n❌ Test failed with exception: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("\n✅ All tests passed!")
        return 0
    else:
        print(f"\n❌ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
