from flask import Blueprint, jsonify, request, g
from api.services.features_service import FeaturesService
from api.middleware.authorization import token_required

features_bp = Blueprint('features', __name__, url_prefix='/features')

# Initialize service
features_service = FeaturesService()


@features_bp.route('/posts/popular', methods=['GET'])
def get_popular_posts():
    """Get popular posts from the materialized view like query"""
    try:
        limit = request.args.get('limit', 20, type=int)
        
        result = features_service.get_popular_posts(limit)
        
        if result["success"]:
            return jsonify({
                "posts": result["posts"],
                "count": result["count"]
            }), 200
        
        return jsonify({"error": result.get("error", "Unknown error")}), 500
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@features_bp.route('/users/active', methods=['GET'])
def get_active_users():
    """Get most active users"""
    try:
        limit = request.args.get('limit', 20, type=int)
        
        result = features_service.get_active_users(limit)
        
        if result["success"]:
            return jsonify({
                "users": result["users"],
                "count": result["count"]
            }), 200
        
        return jsonify({"error": result.get("error", "Unknown error")}), 500
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@features_bp.route('/communities/<int:community_id>/stats', methods=['GET'])
def get_community_stats(community_id):
    """Get detailed statistics for a community"""
    try:
        result = features_service.get_community_stats(community_id)
        
        if result["success"]:
            return jsonify(result["stats"]), 200
        
        return jsonify({"error": result.get("error", "Community stats not found")}), 404
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@features_bp.route('/users/advanced-recommendations', methods=['GET'])
@token_required
def get_advanced_recommendations():
    """Get friend recommendations using friend-of-friend logic"""
    try:
        user_id = g.current_user_id
        
        result = features_service.get_advanced_recommendations(user_id)
        
        if result["success"]:
            return jsonify({
                "recommendations": result["recommendations"]
            }), 200
        
        return jsonify({"error": result.get("error", "Unknown error")}), 500
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
