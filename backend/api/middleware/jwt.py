import jwt
import os
from datetime import datetime, timedelta
from flask import request
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
