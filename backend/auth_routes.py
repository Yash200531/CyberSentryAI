"""Auth blueprint with JWT-based login/logout/refresh/me endpoints.

Access tokens are returned in the JSON payload; refresh tokens are set as
HTTP-only cookies. Blocklist is in-memory by default; swap to persistent
storage for production.
"""
from __future__ import annotations

from datetime import timedelta, datetime
import os
import secrets
from typing import Callable, Iterable

from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    create_refresh_token,
    get_jti,
    get_jwt,
    get_jwt_identity,
    jwt_required,
)

from auth_models import SessionLocal, User, Role, init_db
from email_service import email_service
from sqlalchemy import func

jwt = JWTManager()
auth_bp = Blueprint("auth", __name__)

# Simple in-memory blocklist; replace with Redis in production.
TOKEN_BLOCKLIST = set()


def generate_otp() -> str:
    """Generate a 6-digit OTP code."""
    return str(secrets.randbelow(1000000)).zfill(6)


def configure_jwt_callbacks(app) -> None:
    @jwt.token_in_blocklist_loader
    def is_token_revoked(jwt_header, jwt_payload):  # noqa: ANN001
        return jwt_payload.get("jti") in TOKEN_BLOCKLIST

    @jwt.additional_claims_loader
    def add_claims(identity):  # noqa: ANN001
        with SessionLocal() as session:
            user = session.get(User, identity)
            roles = [r.name for r in user.roles] if user else []
            scopes = (user.scopes or "").split()
            return {"roles": roles, "scopes": scopes}

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):  # noqa: ANN001
        return jsonify({"msg": "Token has been revoked"}), 401

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):  # noqa: ANN001
        return jsonify({"msg": "Token has expired"}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error_string):  # noqa: ANN001
        return jsonify({"msg": f"Invalid token: {error_string}"}), 422

    @jwt.unauthorized_loader
    def missing_token_callback(error_string):  # noqa: ANN001
        return jsonify({"msg": f"Missing token: {error_string}"}), 401


@auth_bp.post("/login")
def login():
    data = request.get_json(force=True)
    email = (data.get("email") or "").strip()
    password = data.get("password") or ""

    admin_email = (os.environ.get("ADMIN_EMAIL") or "admin@cyber.in").strip().lower()
    admin_password = os.environ.get("ADMIN_PASSWORD") or "Admintest123"
    analyst_email = (os.environ.get("ANALYST_EMAIL") or "analyst@co.in").strip().lower()
    analyst_password = os.environ.get("ANALYST_PASSWORD") or "Sw@gtm!1"

    normalized_email = email.lower()
    if normalized_email == admin_email and password == admin_password:
        matched_role = "admin"
        matched_email = admin_email
        scopes = ["alerts:read", "alerts:write"]
    elif normalized_email == analyst_email and password == analyst_password:
        matched_role = "analyst"
        matched_email = analyst_email
        scopes = ["alerts:read", "reports:read"]
    else:
        return jsonify({"msg": "Invalid credentials"}), 401

    current_app.logger.info("Auth matched role: %s", matched_role)

    with SessionLocal() as session:
        role_record = session.query(Role).filter_by(name=matched_role).one_or_none()
        user = session.query(User).filter(func.lower(User.email) == matched_email).one_or_none()
        if not user:
            user = User(email=matched_email, scopes=" ".join(scopes), is_active=True, is_email_verified=False)
            user.set_password(password)
            if role_record:
                user.roles = [role_record]
            session.add(user)
            session.flush()
        else:
            if not user.verify_password(password):
                user.set_password(password)
            user.scopes = " ".join(scopes)
            user.is_active = True
            if role_record:
                user.roles = [role_record]

        session.commit()
        
        # Check if email is verified
        if not user.is_email_verified:
            # Generate and send OTP
            otp_code = generate_otp()
            user.otp_code = otp_code
            user.otp_expiry = datetime.utcnow() + timedelta(minutes=10)
            session.commit()
            
            # Send OTP email
            email_sent = email_service.send_otp_email(matched_email, otp_code)
            
            return jsonify({
                "msg": "Email verification required",
                "requires_verification": True,
                "email": matched_email,
                "otp_sent": email_sent
            }), 403

        access_token = create_access_token(identity=user.id, additional_claims=None)
        refresh_token = create_refresh_token(identity=user.id)

        resp = jsonify({
            "token": access_token,
            "role": matched_role,
            "email": matched_email,
        })
        resp.set_cookie(
            "refresh_token",
            refresh_token,
            httponly=True,
            secure=current_app.config.get("JWT_COOKIE_SECURE", False),
            samesite=current_app.config.get("JWT_COOKIE_SAMESITE", "Lax"),
            path="/auth/refresh",
            max_age=int(current_app.config["JWT_REFRESH_TOKEN_EXPIRES"].total_seconds()),
        )
        return resp


@auth_bp.post("/logout")
@jwt_required()
def logout():
    jti = get_jwt()["jti"]
    TOKEN_BLOCKLIST.add(jti)

    refresh_token = request.cookies.get("refresh_token")
    if refresh_token:
        try:
            refresh_jti = get_jti(refresh_token)
            TOKEN_BLOCKLIST.add(refresh_jti)
        except Exception:
            pass

    resp = jsonify({"msg": "Logged out"})
    resp.delete_cookie("refresh_token", path="/auth/refresh")
    return resp


@auth_bp.post("/refresh")
@jwt_required(refresh=True, locations=["cookies"])
def refresh():
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    return jsonify({"access_token": access_token})


@auth_bp.get("/me")
@jwt_required()
def me():
    identity = get_jwt_identity()
    claims = get_jwt()
    with SessionLocal() as session:
        user = session.get(User, identity)
        if not user:
            return jsonify({"msg": "User not found"}), 404
        return jsonify({
            "id": user.id,
            "email": user.email,
            "roles": claims.get("roles", []),
            "scopes": claims.get("scopes", []),
        })


@auth_bp.post("/verify-otp")
def verify_otp():
    """Verify OTP code and complete email verification."""
    data = request.get_json(force=True)
    email = (data.get("email") or "").strip().lower()
    otp_code = (data.get("otp_code") or "").strip()
    
    if not email or not otp_code:
        return jsonify({"msg": "Email and OTP code are required"}), 400
    
    with SessionLocal() as session:
        user = session.query(User).filter(func.lower(User.email) == email).one_or_none()
        
        if not user:
            return jsonify({"msg": "User not found"}), 404
        
        if user.is_email_verified:
            return jsonify({"msg": "Email already verified"}), 400
        
        if not user.otp_code or not user.otp_expiry:
            return jsonify({"msg": "No OTP requested. Please login again."}), 400
        
        if datetime.utcnow() > user.otp_expiry:
            return jsonify({"msg": "OTP expired. Please request a new one."}), 400
        
        if user.otp_code != otp_code:
            return jsonify({"msg": "Invalid OTP code"}), 401
        
        # Mark email as verified and clear OTP
        user.is_email_verified = True
        user.otp_code = None
        user.otp_expiry = None
        session.commit()
        
        # Generate tokens for the verified user
        access_token = create_access_token(identity=user.id, additional_claims=None)
        refresh_token = create_refresh_token(identity=user.id)
        
        role_name = user.roles[0].name if user.roles else "user"
        
        resp = jsonify({
            "msg": "Email verified successfully",
            "token": access_token,
            "role": role_name,
            "email": user.email,
        })
        resp.set_cookie(
            "refresh_token",
            refresh_token,
            httponly=True,
            secure=current_app.config.get("JWT_COOKIE_SECURE", False),
            samesite=current_app.config.get("JWT_COOKIE_SAMESITE", "Lax"),
            path="/auth/refresh",
            max_age=int(current_app.config["JWT_REFRESH_TOKEN_EXPIRES"].total_seconds()),
        )
        return resp


@auth_bp.post("/resend-otp")
def resend_otp():
    """Resend OTP code to user's email."""
    data = request.get_json(force=True)
    email = (data.get("email") or "").strip().lower()
    
    if not email:
        return jsonify({"msg": "Email is required"}), 400
    
    with SessionLocal() as session:
        user = session.query(User).filter(func.lower(User.email) == email).one_or_none()
        
        if not user:
            return jsonify({"msg": "User not found"}), 404
        
        if user.is_email_verified:
            return jsonify({"msg": "Email already verified"}), 400
        
        # Generate new OTP
        otp_code = generate_otp()
        user.otp_code = otp_code
        user.otp_expiry = datetime.utcnow() + timedelta(minutes=10)
        session.commit()
        
        # Send OTP email
        email_sent = email_service.send_otp_email(email, otp_code)
        
        return jsonify({
            "msg": "OTP sent successfully" if email_sent else "Failed to send OTP",
            "otp_sent": email_sent
        }), 200 if email_sent else 500


# Decorators for downstream services

def require_roles(*required_roles: str) -> Callable:
    def wrapper(fn: Callable) -> Callable:
        @jwt_required()
        def decorated(*args, **kwargs):
            claims = get_jwt()
            roles = set(claims.get("roles", []))
            if not roles.intersection(required_roles):
                return jsonify({"msg": "Forbidden: missing role"}), 403
            return fn(*args, **kwargs)

        decorated.__name__ = fn.__name__
        return decorated

    return wrapper


def require_scopes(*required_scopes: str) -> Callable:
    required = set(required_scopes)

    def wrapper(fn: Callable) -> Callable:
        @jwt_required()
        def decorated(*args, **kwargs):
            scopes = set(get_jwt().get("scopes", []))
            if not required.issubset(scopes):
                return jsonify({"msg": "Forbidden: missing scope"}), 403
            return fn(*args, **kwargs)

        decorated.__name__ = fn.__name__
        return decorated

    return wrapper


__all__ = [
    "auth_bp",
    "jwt",
    "configure_jwt_callbacks",
    "require_roles",
    "require_scopes",
    "TOKEN_BLOCKLIST",
    "init_db",
]
