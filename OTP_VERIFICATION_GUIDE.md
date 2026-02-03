# OTP Email Verification - Implementation Guide

## Overview

CyberSentryAI now includes email-based OTP (One-Time Password) verification for all users (admin, analyst, and regular users). This adds an additional security layer by requiring email verification before granting access to the system.

## Features

- **6-digit OTP codes** sent via email
- **10-minute expiration** for security
- **Resend functionality** for convenience
- **Beautiful email templates** with HTML formatting
- **Development mode** that works without SMTP configuration
- **Seamless UI flow** with dedicated verification page

## Architecture

### Backend Components

1. **Database Schema** (`auth_models.py`)
   - `is_email_verified` - Boolean flag for verification status
   - `otp_code` - Stores the current OTP (cleared after verification)
   - `otp_expiry` - Timestamp for OTP expiration

2. **Email Service** (`email_service.py`)
   - SMTP-based email delivery
   - HTML and plain text email templates
   - Graceful degradation in development mode

3. **Authentication Endpoints** (`auth_routes.py`)
   - `/auth/login` - Modified to check verification status
   - `/auth/verify-otp` - Validates OTP and completes login
   - `/auth/resend-otp` - Generates and sends new OTP

### Frontend Components

1. **OTP Verification Page** (`pages/OTPVerificationPage.tsx`)
   - 6-digit input fields with auto-focus
   - Paste support for convenience
   - Resend OTP button
   - Error and success messaging

2. **Updated Login Flow** (`pages/LoginPage.tsx`)
   - Detects 403 response for verification required
   - Redirects to OTP verification page

## Configuration

### Email Service Setup

Add these environment variables to your `.env` file:

```bash
# For Gmail (recommended for testing)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password_here
FROM_EMAIL=your_email@gmail.com
```

#### Gmail Setup Instructions

1. Enable 2-Factor Authentication on your Google account
2. Go to https://myaccount.google.com/apppasswords
3. Generate an "App Password" for "Mail"
4. Use the generated 16-character password as `SMTP_PASSWORD`

#### Other Email Providers

- **Outlook/Hotmail**: `smtp.office365.com:587`
- **Yahoo**: `smtp.mail.yahoo.com:587`
- **Custom SMTP**: Configure your server's SMTP settings

### Development Mode

If SMTP credentials are not configured, the system operates in development mode:
- OTP codes are printed to the server console
- Email "sending" succeeds without actual delivery
- Verification flow works normally

## User Flow

### 1. Login
```
User enters email and password
  ↓
System validates credentials
  ↓
If NOT verified → Generate OTP → Send email → Redirect to verification
If verified → Generate tokens → Login success
```

### 2. Email Verification
```
User receives email with 6-digit code
  ↓
User enters code in verification page
  ↓
System validates code and expiry
  ↓
Mark email as verified → Generate tokens → Login success
```

### 3. OTP Expiry
```
OTP expires after 10 minutes
  ↓
User can request new OTP via "Resend" button
  ↓
New OTP generated and sent
```

## API Reference

### POST /auth/login

**Request:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response (Not Verified):**
```json
{
  "msg": "Email verification required",
  "requires_verification": true,
  "email": "user@example.com",
  "otp_sent": true
}
```
Status: 403

**Response (Verified):**
```json
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "role": "admin",
  "email": "user@example.com"
}
```
Status: 200

### POST /auth/verify-otp

**Request:**
```json
{
  "email": "user@example.com",
  "otp_code": "123456"
}
```

**Response (Success):**
```json
{
  "msg": "Email verified successfully",
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "role": "admin",
  "email": "user@example.com"
}
```
Status: 200

**Response (Invalid OTP):**
```json
{
  "msg": "Invalid OTP code"
}
```
Status: 401

**Response (Expired OTP):**
```json
{
  "msg": "OTP expired. Please request a new one."
}
```
Status: 400

### POST /auth/resend-otp

**Request:**
```json
{
  "email": "user@example.com"
}
```

**Response:**
```json
{
  "msg": "OTP sent successfully",
  "otp_sent": true
}
```
Status: 200

## Testing

### Unit Tests

Run the OTP verification tests:

```bash
cd backend
python test_otp.py
```

Tests cover:
- OTP generation and storage
- OTP verification logic
- OTP expiry handling
- Email service initialization

### Integration Tests

Start the auth service:
```bash
cd backend
python auth_app.py
```

In another terminal:
```bash
cd backend
python test_otp_api.py
```

### Manual Testing

1. **Start Backend:**
   ```bash
   cd backend
   python auth_app.py
   ```

2. **Start Frontend:**
   ```bash
   cd frontend
   npm run dev
   ```

3. **Test Flow:**
   - Navigate to login page
   - Enter credentials (admin@cyber.in / Admintest123)
   - Check server console for OTP code (in dev mode)
   - Enter OTP on verification page
   - Verify successful login

## Security Considerations

1. **OTP Expiration**: 10-minute window prevents replay attacks
2. **Single Use**: OTP is cleared after successful verification
3. **Database Storage**: OTP stored securely with expiry timestamp
4. **HTTPS Required**: Use HTTPS in production for secure transmission
5. **Rate Limiting**: Consider adding rate limiting to prevent brute force

## Database Migration

The system automatically creates new columns on startup. For existing databases:

```python
from auth_models import init_db
init_db()
```

This safely adds:
- `is_email_verified` (default: False)
- `otp_code` (nullable)
- `otp_expiry` (nullable)

## Troubleshooting

### Email Not Sending

1. **Check SMTP credentials** in `.env`
2. **Verify SMTP port** (587 for TLS, 465 for SSL)
3. **Check firewall** settings
4. **Review server logs** for error messages
5. **Test with Gmail** app password first

### OTP Not Working

1. **Check OTP expiry** (10 minutes)
2. **Verify email matches** login email
3. **Case sensitivity** in email addresses
4. **Database state** using sqlite3 or test script

### Development Mode

If you see "OTP for user@example.com: 123456" in logs:
- SMTP is not configured
- System is in development mode
- Use the printed OTP for testing

## Production Deployment

1. **Configure SMTP** with production email service
2. **Enable HTTPS** for secure communication
3. **Set secure cookies** (`JWT_COOKIE_SECURE=True`)
4. **Add rate limiting** on OTP endpoints
5. **Monitor email delivery** rates
6. **Implement Redis** for token blocklist
7. **Add logging** for security events

## Future Enhancements

- SMS-based OTP as alternative
- Backup codes for recovery
- Remember device functionality
- Configurable OTP length/expiry
- Email verification on registration
- Multi-factor authentication (MFA)

## Support

For issues or questions:
- Check logs in backend console
- Review database state with test scripts
- Verify email configuration
- Test with development mode first
