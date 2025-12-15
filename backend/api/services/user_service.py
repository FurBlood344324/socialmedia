from api.repositories.user_repository import UserRepository
from api.repositories.follow_repository import FollowRepository
from api.entities.entities import User
from werkzeug.security import generate_password_hash, check_password_hash
from typing import Optional, Dict, Any, List


class UserService:
    def __init__(self):
        self.user_repository = UserRepository()
        self.follow_repository = FollowRepository()

    def get_user(self, user_id: int = None, username: str = None,
                 email: str = None, current_user_id: int = None) -> Optional[Dict[str, Any]]:
        """Get user by ID, username, or email with privacy controls"""
        user = None

        if user_id:
            user = self.user_repository.get_by_id(user_id)
        elif username:
            user = self.user_repository.get_by_username(username)
        elif email:
            user = self.user_repository.get_by_email(email)

        if user:
            user_dict = user.to_dict()
            # Add privacy info if current_user_id is provided
            if current_user_id and current_user_id != user.user_id:
                # Check follow status
                follow = self.follow_repository.get_by_ids(current_user_id, user.user_id)
                is_following = follow is not None and follow.status_id == 2
                has_pending_request = follow is not None and follow.status_id == 1
                user_dict['is_following'] = is_following
                user_dict['has_pending_request'] = has_pending_request
                
                can_view = self.can_view_profile(user.user_id, current_user_id)
                user_dict['can_view_profile'] = can_view
                
                if user.is_private and not can_view:
                    # Return limited info, with stats hidden (0) as requested
                    # Do NOT include bio for privacy
                    return {
                        "user_id": user.user_id,
                        "username": user.username,
                        "profile_picture_url": user.profile_picture_url,
                        "is_private": user.is_private,
                        "can_view_profile": False,
                        "is_following": is_following,
                        "has_pending_request": has_pending_request,
                        "created_at": user.created_at.isoformat() if user.created_at else None,
                        "stats": {
                            "followers_count": 0,
                            "following_count": 0,
                            "posts_count": 0
                        }
                    }
            elif current_user_id == user.user_id:
                 user_dict['is_following'] = False # Cannot follow self
                 user_dict['can_view_profile'] = True

            return user_dict
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

    def search_users(self, query: str, limit: int = 20, only_following_for_user_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Search users by username"""
        users = self.user_repository.search(query, limit, only_following_for_user_id)
        return [user.to_dict() for user in users]

    def get_all_users(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get all users with pagination"""
        users = self.user_repository.get_all(limit, offset)
        return [user.to_dict() for user in users]

    def can_view_profile(self, target_user_id: int, current_user_id: int) -> bool:
        """Check if current user can view target user's profile"""
        # User can always view their own profile
        if target_user_id == current_user_id:
            return True
        
        # Get target user
        target_user = self.user_repository.get_by_id(target_user_id)
        if not target_user:
            return False
        
        # If user is public, everyone can view
        if not target_user.is_private:
            return True
        
        # If user is private, check if current user is an accepted follower
        follow = self.follow_repository.get_by_ids(current_user_id, target_user_id)
        # status_id = 2 means 'accepted'
        return follow is not None and follow.status_id == 2

    def get_profile_visibility(self, target_user_id: int, current_user_id: int) -> Dict[str, Any]:
        """Get what current user can see of target user's profile"""
        can_view = self.can_view_profile(target_user_id, current_user_id)
        target_user = self.user_repository.get_by_id(target_user_id)
        
        if not target_user:
            return {"can_view": False, "reason": "User not found"}
        
        result = {
            "user_id": target_user_id,
            "can_view_profile": can_view,
            "is_private": target_user.is_private
        }
        
        if target_user_id == current_user_id:
            result["reason"] = "Own profile"
        elif not target_user.is_private:
            result["reason"] = "Public profile"
        elif can_view:
            result["reason"] = "Accepted follower"
        else:
            result["reason"] = "Private profile - not following"
        
        return result
    
    def get_friend_recommendations(self, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Get friend recommendations"""
        return self.user_repository.get_recommendations(user_id, limit)
