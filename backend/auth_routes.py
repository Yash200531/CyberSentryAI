"""Auth blueprint with JWT-based login/logout/refresh/me endpoints.

Access tokens are returned in the JSON payload; refresh tokens are set as
HTTP-only cookies. Blocklist is in-memory by default; swap to persistent
storage for production.
"""
from __future__ import annotations

from datetime import timedelta
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

from auth_models import SessionLocal, User, init_db

jwt = JWTManager()
auth_bp = Blueprint("auth", __name__)

# Simple in-memory blocklist; replace with Redis in production.
TOKEN_BLOCKLIST = set()


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
    email = (data.get("email") or "").lower().strip()
    password = data.get("password") or ""

    with SessionLocal() as session:
        user = session.query(User).filter(User.email == email).one_or_none()
        if not user or not user.verify_password(password) or not user.is_active:
            return jsonify({"msg": "Invalid credentials"}), 401

        access_token = create_access_token(identity=user.id, additional_claims=None)
        refresh_token = create_refresh_token(identity=user.id)

        roles = [r.name for r in user.roles]
        scopes = (user.scopes or "").split()

        resp = jsonify({
            "access_token": access_token,
            "user": {
                "id": user.id,
                "email": user.email,
                "roles": roles,
                "scopes": scopes,
            },
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
