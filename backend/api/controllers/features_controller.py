from flask import Blueprint, jsonify, request, g
from sqlalchemy import text
from api.extensions import db
from api.middleware.authorization import token_required

features_bp = Blueprint('features', __name__, url_prefix='/features')

@features_bp.route('/posts/popular', methods=['GET'])
def get_popular_posts():
    """Get popular posts from the materialized view like query"""
    try:
        limit = request.args.get('limit', 20, type=int)
        
        # Using the view we reinstated
        query = text("SELECT * FROM popular_posts_view LIMIT :limit")
        result = db.session.execute(query, {"limit": limit})
        
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
            
        return jsonify({"posts": posts, "count": len(posts)}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@features_bp.route('/users/active', methods=['GET'])
def get_active_users():
    """Get most active users"""
    try:
        limit = request.args.get('limit', 20, type=int)
        
        query = text("SELECT * FROM active_users_view LIMIT :limit")
        result = db.session.execute(query, {"limit": limit})
        
        users = []
        for row in result:
            users.append({
                "user_id": row.user_id,
                "username": row.username,
                "profile_picture_url": row.profile_picture_url,
                "posts_last_7_days": row.posts_last_7_days,
                "total_activity": row.total_activity
            })
            
        return jsonify({"users": users, "count": len(users)}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@features_bp.route('/communities/<int:community_id>/stats', methods=['GET'])
def get_community_stats(community_id):
    """Get detailed statistics for a community"""
    try:
        query = text("SELECT * FROM community_statistics_view WHERE community_id = :cid")
        result = db.session.execute(query, {"cid": community_id}).fetchone()
        
        if not result:
            return jsonify({"error": "Community stats not found"}), 404
            
        stats = {
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
        
        return jsonify(stats), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@features_bp.route('/users/advanced-recommendations', methods=['GET'])
@token_required
def get_advanced_recommendations():
    """Get friend recommendations using friend-of-friend logic"""
    try:
        user_id = g.current_user_id
        
        query = text("SELECT * FROM advanced_friend_recommendations WHERE user_id = :uid LIMIT 20")
        result = db.session.execute(query, {"uid": user_id})
        
        recommendations = []
        for row in result:
            recommendations.append({
                "suggested_user_id": row.user_id,
                "username": row.suggested_username,
                "mutual_count": row.mutual_count,
                "score": row.recommendation_score
            })
            
        return jsonify({"recommendations": recommendations}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
