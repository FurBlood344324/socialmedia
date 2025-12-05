from api.repositories.user_repository import UserRepository
from api.middleware.jwt import generate_token
from werkzeug.security import generate_password_hash, check_password_hash
from typing import Optional, Dict, Any
from api.entities.entities import User


class AuthService:
    def __init__(self):
        self.user_repository = UserRepository()

    def register(self, username: str, email: str, password: str,
                 bio: str = None, profile_picture_url: str = None,
                 is_private: bool = False) -> Dict[str, Any]:
        """Register a new user"""
        if self.user_repository.get_by_username(username):
            return {"success": False, "error": "Username already exists"}

        if self.user_repository.get_by_email(email):
            return {"success": False, "error": "Email already exists"}

        password_hash = generate_password_hash(password)

        user = User(
            username=username,
            email=email,
            password_hash=password_hash,
            bio=bio,
            profile_picture_url=profile_picture_url,
            is_private=is_private
        )

        created_user = self.user_repository.create(user)

        if not created_user:
            return {"success": False, "error": "Failed to create user"}

        return {
            "success": True,
            "user": created_user.to_dict()
        }

    def login(self, username: str, password: str) -> Dict[str, Any]:
        """Authenticate user and return JWT token"""
        user = self.user_repository.get_by_username(username)

        if not user:
            return {"success": False, "error": "Invalid username or password"}

        if not check_password_hash(user.password_hash, password):
            return {"success": False, "error": "Invalid username or password"}

        token = generate_token(user.user_id, user.username)

        return {
            "success": True,
            "token": token,
            "user": user.to_dict()
        }

    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        user = self.user_repository.get_by_id(user_id)

        if user:
            return user.to_dict()
        return None
