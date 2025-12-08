import jwt
import os
from datetime import datetime, timedelta
from flask import request, jsonify
from functools import wraps
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt-secret-key")


def encode_token(payload: dict) -> str:
    """Encode payload to JWT token"""
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def decode_token(token: str) -> dict:
    """Decode JWT token to payload, returns None if invalid"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def decode_auth_token():
    """Extract and decode token from Authorization header"""
    try:
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return None
        token = auth_header.replace("Bearer ", "")
        return decode_token(token)
    except Exception:
        return None


def generate_token(user_id: int, username: str) -> str:
    """Generate JWT token for authenticated user"""
    payload = {
        "user_id": user_id,
        "username": username,
        "exp": datetime.utcnow() + timedelta(hours=24),
        "iat": datetime.utcnow()
    }
    return encode_token(payload)


def token_required(f):
    """Decorator to protect routes with JWT authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Extract and decode token
        payload = decode_auth_token()
        
        if not payload:
            return jsonify({"error": "Invalid or missing token"}), 401
        
        # Attach user_id to request object
        request.user_id = payload.get("user_id")
        request.username = payload.get("username")
        
        return f(*args, **kwargs)
    
    return decorated_function
