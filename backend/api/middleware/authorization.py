from functools import wraps
from flask import jsonify, g
from api.middleware.jwt import decode_auth_token


def token_required(f):
    """Decorator to protect routes that require authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        payload = decode_auth_token()

        if not payload:
            return jsonify({"error": "Unauthorized"}), 401

        user_id = payload.get("user_id")
        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        # Store user info in flask g object for access in route
        g.current_user_id = user_id
        g.current_username = payload.get("username")

        return f(*args, **kwargs)
    return decorated


def get_user_id():
    """Decorator to get user_id from token and return it directly"""
    def wrapper(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            payload = decode_auth_token()

            if not payload:
                return jsonify({"error": "Unauthorized"}), 401

            user_id = payload.get("user_id")
            if not user_id:
                return jsonify({"error": "Unauthorized"}), 401

            return jsonify({"user_id": user_id}), 200
        return decorated
    return wrapper
