from api.repositories.follow_repository import FollowRepository
from api.repositories.user_repository import UserRepository
from api.entities.entities import Follow
from typing import Dict, Any, List


class FollowService:
    def __init__(self):
        self.follow_repository = FollowRepository()
        self.user_repository = UserRepository()
    
    def follow_user(self, follower_id: int, following_id: int) -> Dict[str, Any]:
        """Follow a user - auto accept if public, pending if private"""
        # Check if trying to follow self
        if follower_id == following_id:
            return {"success": False, "error": "Cannot follow yourself"}
        
        # Check if following user exists
        following_user = self.user_repository.get_by_id(following_id)
        if not following_user:
            return {"success": False, "error": "User not found"}
        
        # Check if already following
        existing = self.follow_repository.get_by_ids(follower_id, following_id)
        if existing:
            if existing.status_id == 2:  # accepted
                return {"success": False, "error": "Already following this user"}
            elif existing.status_id == 1:  # pending
                return {"success": False, "error": "Follow request already pending"}
            elif existing.status_id == 3:  # rejected
                # Allow re-requesting after rejection
                updated = self.follow_repository.update_status(follower_id, following_id, 1)
                return {
                    "success": True,
                    "message": "Follow request sent",
                    "status": "pending",
                    "follow": updated.to_dict()
                }
        
        # All follow requests go to pending state (LinkedIn-style)
        # status_id: 1=pending, 2=accepted
        status_id = 1
        
        follow = Follow(
            follower_id=follower_id,
            following_id=following_id,
            status_id=status_id
        )
        
        created_follow = self.follow_repository.create(follow)
        
        return {
            "success": True,
            "message": "Follow request sent" if status_id == 1 else "Now following",
            "status": "pending" if status_id == 1 else "accepted",
            "follow": created_follow.to_dict()
        }

    def unfollow_user(self, follower_id: int, following_id: int) -> Dict[str, Any]:
        """Unfollow a user (breaks mutual connection - LinkedIn-style)"""
        existing = self.follow_repository.get_by_ids(follower_id, following_id)
        if not existing:
            return {"success": False, "error": "Not following this user"}
        
        # Delete the primary follow relationship
        deleted = self.follow_repository.delete(follower_id, following_id)
        
        # Also delete the reverse follow relationship (mutual unfollow)
        reverse_existing = self.follow_repository.get_by_ids(following_id, follower_id)
        if reverse_existing:
            self.follow_repository.delete(following_id, follower_id)
        
        if deleted:
            return {"success": True, "message": "Unfollowed successfully"}
        return {"success": False, "error": "Failed to unfollow"}

    def accept_follow_request(self, follower_id: int, following_id: int) -> Dict[str, Any]:
        """Accept a follow request (only the followed user can accept)"""
        existing = self.follow_repository.get_by_ids(follower_id, following_id)
        
        if not existing:
            return {"success": False, "error": "Follow request not found"}
        
        if existing.status_id == 2:
            return {"success": False, "error": "Follow request already accepted"}
        
        if existing.status_id != 1:
            return {"success": False, "error": "Invalid follow request status"}
        
        # Update status to accepted (2)
        updated = self.follow_repository.update_status(follower_id, following_id, 2)
        
        # Create mutual follow (LinkedIn-style connection)
        # The person accepting now also follows the requester
        reverse_existing = self.follow_repository.get_by_ids(following_id, follower_id)
        if not reverse_existing:
            reverse_follow = Follow(
                follower_id=following_id,
                following_id=follower_id,
                status_id=2  # Auto-accept the reverse
            )
            self.follow_repository.create(reverse_follow)
        elif reverse_existing.status_id != 2:
            # If reverse exists but not accepted, update it to accepted
            self.follow_repository.update_status(following_id, follower_id, 2)
        
        return {
            "success": True,
            "message": "Follow request accepted",
            "follow": updated.to_dict()
        }

    def reject_follow_request(self, follower_id: int, following_id: int) -> Dict[str, Any]:
        """Reject a follow request (only the followed user can reject)"""
        existing = self.follow_repository.get_by_ids(follower_id, following_id)
        
        if not existing:
            return {"success": False, "error": "Follow request not found"}
        
        if existing.status_id != 1:
            return {"success": False, "error": "Can only reject pending requests"}
        
        # Update status to rejected (3)
        updated = self.follow_repository.update_status(follower_id, following_id, 3)
        
        return {
            "success": True,
            "message": "Follow request rejected",
            "follow": updated.to_dict()
        }

    def get_followers(self, user_id: int, current_user_id: int = None, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get all followers of a user"""
        followers = self.follow_repository.get_followers(user_id, current_user_id, limit, offset)
        return followers

    def get_following(self, user_id: int, current_user_id: int = None, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get all users that a user is following"""
        following = self.follow_repository.get_following(user_id, current_user_id, limit, offset)
        return following

    def get_pending_requests(self, user_id: int, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get pending follow requests for a user"""
        requests = self.follow_repository.get_pending_requests(user_id, limit, offset)
        return requests

    def get_follow_stats(self, user_id: int) -> Dict[str, Any]:
        """Get follow statistics for a user"""
        followers_count = self.follow_repository.count_followers(user_id)
        following_count = self.follow_repository.count_following(user_id)
        
        return {
            "user_id": user_id,
            "followers_count": followers_count,
            "following_count": following_count
        }
