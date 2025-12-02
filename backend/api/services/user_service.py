from api.repositories.user_repository import UserRepository
from api.entities.entities import User
from werkzeug.security import generate_password_hash, check_password_hash
from typing import Optional, Dict, Any


class UserService:
    def __init__(self):
        self.user_repository = UserRepository()

    def register(self, username: str, email: str, password: str, 
                 bio: str = None, profile_picture_url: str = None, 
                 is_private: bool = False) -> Dict[str, Any]:
        """Register a new user"""
        # Check if username already exists
        if self.user_repository.get_by_username(username):
            return {"success": False, "error": "Username already exists"}
        
        # Check if email already exists
        if self.user_repository.get_by_email(email):
            return {"success": False, "error": "Email already exists"}
        
        # Hash the password
        password_hash = generate_password_hash(password)
        
        # Create user entity
        user = User(
            username=username,
            email=email,
            password_hash=password_hash,
            bio=bio,
            profile_picture_url=profile_picture_url,
            is_private=is_private
        )
        
        # Save to database
        created_user = self.user_repository.create(user)
        
        return {
            "success": True,
            "user": self._user_to_dict(created_user)
        }

    def get_user(self, user_id: int = None, username: str = None, 
                 email: str = None) -> Optional[Dict[str, Any]]:
        """Get user by ID, username, or email"""
        user = None
        
        if user_id:
            user = self.user_repository.get_by_id(user_id)
        elif username:
            user = self.user_repository.get_by_username(username)
        elif email:
            user = self.user_repository.get_by_email(email)
        
        if user:
            return self._user_to_dict(user)
        return None

    def update_profile(self, user_id: int, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update user profile"""
        # Get existing user
        user = self.user_repository.get_by_id(user_id)
        if not user:
            return {"success": False, "error": "User not found"}
        
        # Check username uniqueness if being updated
        if "username" in updates and updates["username"] != user.username:
            existing = self.user_repository.get_by_username(updates["username"])
            if existing:
                return {"success": False, "error": "Username already exists"}
            user.username = updates["username"]
        
        # Check email uniqueness if being updated
        if "email" in updates and updates["email"] != user.email:
            existing = self.user_repository.get_by_email(updates["email"])
            if existing:
                return {"success": False, "error": "Email already exists"}
            user.email = updates["email"]
        
        # Update password if provided
        if "password" in updates:
            user.password_hash = generate_password_hash(updates["password"])
        
        # Update other fields
        if "bio" in updates:
            user.bio = updates["bio"]
        if "profile_picture_url" in updates:
            user.profile_picture_url = updates["profile_picture_url"]
        if "is_private" in updates:
            user.is_private = updates["is_private"]
        
        # Save updates
        updated_user = self.user_repository.update(user)
        
        return {
            "success": True,
            "user": self._user_to_dict(updated_user)
        }

    def delete_account(self, user_id: int) -> Dict[str, Any]:
        """Delete a user account"""
        # Check if user exists
        user = self.user_repository.get_by_id(user_id)
        if not user:
            return {"success": False, "error": "User not found"}
        
        # Delete user
        deleted = self.user_repository.delete(user_id)
        
        if deleted:
            return {"success": True, "message": "Account deleted successfully"}
        return {"success": False, "error": "Failed to delete account"}

    def authenticate(self, email: str, password: str) -> Dict[str, Any]:
        """Authenticate user with email and password"""
        user = self.user_repository.get_by_email(email)
        
        if not user:
            return {"success": False, "error": "Invalid email or password"}
        
        if not check_password_hash(user.password_hash, password):
            return {"success": False, "error": "Invalid email or password"}
        
        return {
            "success": True,
            "user": self._user_to_dict(user)
        }

    def _user_to_dict(self, user: User) -> Dict[str, Any]:
        """Convert User entity to dictionary (excluding password_hash)"""
        return {
            "user_id": user.user_id,
            "username": user.username,
            "email": user.email,
            "bio": user.bio,
            "profile_picture_url": user.profile_picture_url,
            "is_private": user.is_private,
            "created_at": user.created_at.isoformat() if user.created_at else None
        }
