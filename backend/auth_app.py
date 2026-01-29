"""Standalone auth service for CyberSentryAI.
Run with `python backend/auth_app.py`. Configure secrets via env vars.
"""
from __future__ import annotations

import os
from datetime import timedelta

from flask import Flask
from flask_cors import CORS

from auth_models import init_db
from auth_routes import auth_bp, configure_jwt_callbacks, jwt


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.update(
        JWT_SECRET_KEY=os.environ.get("JWT_SECRET_KEY", "dev-secret-change-me"),
        JWT_ACCESS_TOKEN_EXPIRES=timedelta(minutes=20),
        JWT_REFRESH_TOKEN_EXPIRES=timedelta(days=7),
        JWT_TOKEN_LOCATION=["headers", "cookies"],
        JWT_REFRESH_COOKIE_NAME="refresh_token",
        JWT_COOKIE_CSRF_PROTECT=False,  # enable if you manage CSRF tokens on the client
        JWT_COOKIE_SECURE=os.environ.get("JWT_COOKIE_SECURE", "false").lower() == "true",
        JWT_COOKIE_SAMESITE=os.environ.get("JWT_COOKIE_SAMESITE", "Lax"),
    )

    CORS(app, supports_credentials=True)
    jwt.init_app(app)
    configure_jwt_callbacks(app)

    init_db()
    app.register_blueprint(auth_bp, url_prefix="/auth")
    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("AUTH_PORT", 5003)), debug=True)
