from sqlalchemy import text
from api.extensions import db
from typing import Optional, List, Dict


class FeaturesRepository:
    """Repository layer for features-related database operations"""
    
    def __init__(self):
        self.db = db

    def get_popular_posts(self, limit: int = 20) -> List[Dict]:
        """Get popular posts from the materialized view"""
        query = text("SELECT * FROM popular_posts_view LIMIT :limit")
        result = self.db.session.execute(query, {"limit": limit})
        
        posts = []
        for row in result:
            posts.append({
                "post_id": row.post_id,
                "author_id": row.user_id,
                "author_username": row.username,
                "author_profile_picture": row.profile_picture_url,
                "content": row.content,
                "media_url": row.media_url,
                "community_id": row.community_id,
                "community_name": row.community_name,
                "created_at": row.created_at.isoformat() if row.created_at else None,
                "like_count": row.like_count,
                "comment_count": row.comment_count,
                "engagement_score": row.engagement_score
            })
        
        return posts

    def get_active_users(self, limit: int = 20) -> List[Dict]:
        """Get most active users from the view"""
        query = text("SELECT * FROM active_users_view LIMIT :limit")
        result = self.db.session.execute(query, {"limit": limit})
        
        users = []
        for row in result:
            users.append({
                "user_id": row.user_id,
                "username": row.username,
                "profile_picture_url": row.profile_picture_url,
                "posts_last_7_days": row.posts_last_7_days,
                "total_activity": row.total_activity
            })
        
        return users

    def get_community_stats(self, community_id: int) -> Optional[Dict]:
        """Get detailed statistics for a community"""
        query = text("SELECT * FROM community_statistics_view WHERE community_id = :cid")
        result = self.db.session.execute(query, {"cid": community_id}).fetchone()
        
        if not result:
            return None
        
        return {
            "community_id": result.community_id,
            "community_name": result.community_name,
            "total_members": result.total_members,
            "total_posts": result.total_posts,
            "posts_last_7_days": result.posts_last_7_days,
            "activity_level": result.activity_level,
            "roles": {
                "admins": result.admin_count,
                "moderators": result.moderator_count,
                "regular_members": result.regular_member_count
            },
            "engagement": {
                "total_likes": result.total_likes,
                "total_comments": result.total_comments
            }
        }

    def get_advanced_friend_recommendations(self, user_id: int, limit: int = 20) -> List[Dict]:
        """Get friend recommendations using friend-of-friend logic"""
        query = text("SELECT * FROM advanced_friend_recommendations WHERE user_id = :uid LIMIT :limit")
        result = self.db.session.execute(query, {"uid": user_id, "limit": limit})
        
        recommendations = []
        for row in result:
            recommendations.append({
                "suggested_user_id": row.user_id,
                "username": row.suggested_username,
                "mutual_count": row.mutual_count,
                "score": row.recommendation_score
            })
        
        return recommendations
