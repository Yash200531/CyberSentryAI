"""Route decorators for role and scope enforcement."""
from __future__ import annotations

from functools import wraps
from typing import Callable

from flask import jsonify
from flask_jwt_extended import get_jwt, jwt_required


def require_roles(*required_roles: str) -> Callable:
    def wrapper(fn: Callable) -> Callable:
        @wraps(fn)
        @jwt_required()
        def decorated(*args, **kwargs):
            roles = set(get_jwt().get("roles", []))
            if not roles.intersection(required_roles):
                return jsonify({"msg": "Forbidden: missing role"}), 403
            return fn(*args, **kwargs)

        return decorated

    return wrapper


def require_scopes(*required_scopes: str) -> Callable:
    needed = set(required_scopes)

    def wrapper(fn: Callable) -> Callable:
        @wraps(fn)
        @jwt_required()
        def decorated(*args, **kwargs):
            scopes = set(get_jwt().get("scopes", []))
            if not needed.issubset(scopes):
                return jsonify({"msg": "Forbidden: missing scope"}), 403
            return fn(*args, **kwargs)

        return decorated

    return wrapper
