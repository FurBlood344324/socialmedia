from api.repositories.user_repository import UserRepository
from api.entities.entities import User
from werkzeug.security import generate_password_hash, check_password_hash
from typing import Optional, Dict, Any, List


class UserService:
    def __init__(self):
        self.user_repository = UserRepository()

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
            return user.to_dict()
        return None

    def get_user_entity(self, user_id: int) -> Optional[User]:
        """Get user entity by ID"""
        return self.user_repository.get_by_id(user_id)

    def update_profile(self, user_id: int, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update user profile"""
        user = self.user_repository.get_by_id(user_id)

        if not user:
            return {"success": False, "error": "User not found"}

        if "username" in updates and updates["username"] != user.username:
            existing = self.user_repository.get_by_username(updates["username"])
            if existing:
                return {"success": False, "error": "Username already exists"}
            user.username = updates["username"]

        if "email" in updates and updates["email"] != user.email:
            existing = self.user_repository.get_by_email(updates["email"])
            if existing:
                return {"success": False, "error": "Email already exists"}
            user.email = updates["email"]

        if "password" in updates:
            user.password_hash = generate_password_hash(updates["password"])

        if "bio" in updates:
            user.bio = updates["bio"]

        if "profile_picture_url" in updates:
            user.profile_picture_url = updates["profile_picture_url"]

        if "is_private" in updates:
            user.is_private = updates["is_private"]

        updated_user = self.user_repository.update(user)

        return {
            "success": True,
            "user": updated_user.to_dict()
        }

    def delete_account(self, user_id: int) -> Dict[str, Any]:
        """Delete a user account"""
        user = self.user_repository.get_by_id(user_id)
        if not user:
            return {"success": False, "error": "User not found"}

        deleted = self.user_repository.delete(user_id)

        if deleted:
            return {"success": True, "message": "Account deleted successfully"}
        return {"success": False, "error": "Failed to delete account"}

    def search_users(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search users by username"""
        users = self.user_repository.search(query, limit)
        return [user.to_dict() for user in users]

    def get_all_users(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get all users with pagination"""
        users = self.user_repository.get_all(limit, offset)
        return [user.to_dict() for user in users]
