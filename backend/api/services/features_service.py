from api.repositories.features_repository import FeaturesRepository
from typing import Optional, Dict, Any, List


class FeaturesService:
    """Service layer for features - business logic and coordination"""
    
    def __init__(self):
        self.features_repository = FeaturesRepository()

    def get_popular_posts(self, limit: int = 20) -> Dict[str, Any]:
        """Get popular posts with business logic"""
        # Validate limit
        if limit < 1:
            limit = 1
        elif limit > 100:
            limit = 100
        
        posts = self.features_repository.get_popular_posts(limit)
        
        return {
            "success": True,
            "posts": posts,
            "count": len(posts)
        }

    def get_active_users(self, limit: int = 20) -> Dict[str, Any]:
        """Get most active users with business logic"""
        # Validate limit
        if limit < 1:
            limit = 1
        elif limit > 100:
            limit = 100
        
        users = self.features_repository.get_active_users(limit)
        
        return {
            "success": True,
            "users": users,
            "count": len(users)
        }

    def get_community_stats(self, community_id: int) -> Dict[str, Any]:
        """Get detailed statistics for a community"""
        stats = self.features_repository.get_community_stats(community_id)
        
        if not stats:
            return {
                "success": False,
                "error": "Community stats not found"
            }
        
        return {
            "success": True,
            "stats": stats
        }

    def get_advanced_recommendations(self, user_id: int, limit: int = 20) -> Dict[str, Any]:
        """Get friend recommendations using friend-of-friend logic"""
        # Validate limit
        if limit < 1:
            limit = 1
        elif limit > 50:
            limit = 50
        
        recommendations = self.features_repository.get_advanced_friend_recommendations(user_id, limit)
        
        return {
            "success": True,
            "recommendations": recommendations,
            "count": len(recommendations)
        }
