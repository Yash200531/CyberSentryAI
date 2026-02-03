"""Email service for sending OTP verification codes.

Supports SMTP-based email delivery for user verification.
"""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional


class EmailService:
    """Service for sending verification emails via SMTP."""

    def __init__(self):
        self.smtp_host = os.environ.get("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.environ.get("SMTP_PORT", "587"))
        self.smtp_user = os.environ.get("SMTP_USER", "")
        self.smtp_password = os.environ.get("SMTP_PASSWORD", "")
        self.from_email = os.environ.get("FROM_EMAIL", self.smtp_user)
        self.enabled = bool(self.smtp_user and self.smtp_password)

    def send_otp_email(self, to_email: str, otp_code: str) -> bool:
        """Send OTP verification code via email.
        
        Args:
            to_email: Recipient email address
            otp_code: 6-digit OTP code
            
        Returns:
            True if email sent successfully, False otherwise
        """
        if not self.enabled:
            print(f"[EMAIL] SMTP not configured. OTP for {to_email}: {otp_code}")
            return True  # Return True in dev mode to allow testing
        
        try:
            message = MIMEMultipart("alternative")
            message["Subject"] = "CyberSentry AI - Email Verification Code"
            message["From"] = self.from_email
            message["To"] = to_email

            text = f"""
CyberSentry AI - Email Verification

Your verification code is: {otp_code}

This code will expire in 10 minutes.

If you didn't request this code, please ignore this email.

Best regards,
CyberSentry AI Team
"""

            html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #06b6d4 0%, #0891b2 100%); padding: 30px; text-align: center; }}
        .header h1 {{ color: white; margin: 0; font-size: 24px; }}
        .content {{ background: #f9fafb; padding: 30px; }}
        .otp-code {{ background: white; border: 2px solid #06b6d4; border-radius: 8px; padding: 20px; text-align: center; margin: 20px 0; }}
        .otp-code .code {{ font-size: 32px; font-weight: bold; color: #0891b2; letter-spacing: 5px; }}
        .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🛡️ CyberSentry AI</h1>
        </div>
        <div class="content">
            <h2>Email Verification</h2>
            <p>Your verification code is:</p>
            <div class="otp-code">
                <div class="code">{otp_code}</div>
            </div>
            <p>This code will expire in <strong>10 minutes</strong>.</p>
            <p>If you didn't request this code, please ignore this email.</p>
        </div>
        <div class="footer">
            <p>Best regards,<br>CyberSentry AI Team</p>
        </div>
    </div>
</body>
</html>
"""

            part1 = MIMEText(text, "plain")
            part2 = MIMEText(html, "html")
            message.attach(part1)
            message.attach(part2)

            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(message)

            print(f"[EMAIL] OTP sent successfully to {to_email}")
            return True

        except Exception as e:
            print(f"[EMAIL] Failed to send OTP to {to_email}: {e}")
            return False


# Global email service instance
email_service = EmailService()


__all__ = ["email_service", "EmailService"]
