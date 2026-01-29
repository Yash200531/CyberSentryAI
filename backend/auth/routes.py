"""Auth blueprint with JWT endpoints."""
from __future__ import annotations

from flask import Blueprint, current_app, jsonify, request
import os
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    create_refresh_token,
    get_jti,
    get_jwt,
    get_jwt_identity,
    jwt_required,
)

from .models import SessionLocal, User, Role
from sqlalchemy import func
from .utils import TOKEN_BLOCKLIST, block_token, is_token_blocked

jwt = JWTManager()
auth_bp = Blueprint("auth", __name__)


def configure_jwt_callbacks(app) -> None:
    @jwt.token_in_blocklist_loader
    def is_token_revoked(jwt_header, jwt_payload):  # noqa: ANN001
        return is_token_blocked(jwt_payload.get("jti"))

    @jwt.additional_claims_loader
    def add_claims(identity):  # noqa: ANN001
        with SessionLocal() as session:
            user = session.get(User, identity)
            roles = [r.name for r in user.roles] if user else []
            scopes = (user.scopes or "").split() if user else []
            return {"roles": roles, "scopes": scopes}

    @jwt.revoked_token_loader
    def revoked_token(jwt_header, jwt_payload):  # noqa: ANN001
        return jsonify({"msg": "Token has been revoked"}), 401

    @jwt.expired_token_loader
    def expired_token(jwt_header, jwt_payload):  # noqa: ANN001
        return jsonify({"msg": "Token has expired"}), 401

    @jwt.invalid_token_loader
    def invalid_token(reason):  # noqa: ANN001
        return jsonify({"msg": f"Invalid token: {reason}"}), 422

    @jwt.unauthorized_loader
    def missing_token(reason):  # noqa: ANN001
        return jsonify({"msg": f"Missing token: {reason}"}), 401


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
            user = User(email=matched_email, scopes=" ".join(scopes), is_active=True)
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

        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)

        resp = jsonify({
            "token": access_token,
            "role": matched_role,
            "email": matched_email,
        })
        resp.set_cookie(
            current_app.config.get("JWT_REFRESH_COOKIE_NAME", "refresh_token"),
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
    block_token(jti)

    refresh_token = request.cookies.get(current_app.config.get("JWT_REFRESH_COOKIE_NAME", "refresh_token"))
    if refresh_token:
        try:
            block_token(get_jti(refresh_token))
        except Exception:
            pass

    resp = jsonify({"msg": "Logged out"})
    resp.delete_cookie(current_app.config.get("JWT_REFRESH_COOKIE_NAME", "refresh_token"), path="/auth/refresh")
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


__all__ = [
    "auth_bp",
    "jwt",
    "configure_jwt_callbacks",
]
