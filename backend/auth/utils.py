"""Utility helpers for auth."""
from __future__ import annotations

from datetime import timedelta
from typing import Set

from flask import Flask
from passlib.hash import bcrypt

TOKEN_BLOCKLIST: Set[str] = set()


def configure_app_defaults(app: Flask) -> None:
    app.config.setdefault("JWT_SECRET_KEY", "dev-secret-change-me")
    app.config.setdefault("JWT_ACCESS_TOKEN_EXPIRES", timedelta(minutes=20))
    app.config.setdefault("JWT_REFRESH_TOKEN_EXPIRES", timedelta(days=7))
    app.config.setdefault("JWT_TOKEN_LOCATION", ["headers", "cookies"])
    app.config.setdefault("JWT_REFRESH_COOKIE_NAME", "refresh_token")
    app.config.setdefault("JWT_COOKIE_SECURE", False)
    app.config.setdefault("JWT_COOKIE_SAMESITE", "Lax")
    app.config.setdefault("JWT_COOKIE_CSRF_PROTECT", False)


def hash_password(password: str) -> str:
    return bcrypt.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.verify(password, password_hash)


def block_token(jti: str) -> None:
    TOKEN_BLOCKLIST.add(jti)


def is_token_blocked(jti: str) -> bool:
    return jti in TOKEN_BLOCKLIST
