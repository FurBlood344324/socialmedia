from flask import Blueprint, request, jsonify
from api.services.post_service import PostService
from api.middleware.jwt import token_required

post_bp = Blueprint('post', __name__)
post_service = PostService()


@post_bp.route('/posts', methods=['POST'])
@token_required
def create_post():
    """Create a new post"""
    data = request.get_json()
    
    result = post_service.create_post(
        user_id=request.user_id,
        content=data.get('content'),
        media_url=data.get('media_url'),
        community_id=data.get('community_id')
    )
    
    if result['success']:
        return jsonify(result), 201
    return jsonify(result), 400


@post_bp.route('/posts/<int:post_id>', methods=['GET'])
@token_required
def get_post(post_id):
    """Get a specific post by ID"""
    post = post_service.get_post(post_id, request.user_id)
    
    if post:
        return jsonify({"success": True, "post": post}), 200
    return jsonify({"success": False, "error": "Post not found"}), 404


@post_bp.route('/posts/user/<int:user_id>', methods=['GET'])
@token_required
def get_user_posts(user_id):
    """Get all posts by a specific user"""
    limit = request.args.get('limit', 50, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    result = post_service.get_user_posts(user_id, limit, offset)
    return jsonify({"success": True, **result}), 200


@post_bp.route('/posts/<int:post_id>', methods=['PUT'])
@token_required
def update_post(post_id):
    """Update a post (only owner can update)"""
    data = request.get_json()
    
    result = post_service.update_post(
        post_id=post_id,
        user_id=request.user_id,
        updates=data
    )
    
    if result['success']:
        return jsonify(result), 200
    
    # Return 403 for permission errors, 404 for not found
    status_code = 403 if "only" in result.get('error', '').lower() else 404
    return jsonify(result), status_code


@post_bp.route('/posts/<int:post_id>', methods=['DELETE'])
@token_required
def delete_post(post_id):
    """Delete a post (only owner can delete)"""
    result = post_service.delete_post(post_id, request.user_id)
    
    if result['success']:
        return jsonify(result), 200
    
    # Return 403 for permission errors, 404 for not found
    status_code = 403 if "only" in result.get('error', '').lower() else 404
    return jsonify(result), status_code


@post_bp.route('/posts/feed', methods=['GET'])
@token_required
def get_feed():
    """Get authenticated user's feed (posts from followed users)"""
    limit = request.args.get('limit', 50, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    result = post_service.get_feed(request.user_id, limit, offset)
    return jsonify({"success": True, **result}), 200


@post_bp.route('/posts/<int:post_id>/like', methods=['POST'])
@token_required
def like_post(post_id):
    """Like a post"""
    result = post_service.like_post(post_id, request.user_id)
    
    if result['success']:
        return jsonify(result), 200
    
    # Return 400 for validation errors (own post, already liked), 404 for not found
    status_code = 404 if "not found" in result.get('error', '').lower() else 400
    return jsonify(result), status_code


@post_bp.route('/posts/<int:post_id>/like', methods=['DELETE'])
@token_required
def unlike_post(post_id):
    """Unlike a post"""
    result = post_service.unlike_post(post_id, request.user_id)
    
    if result['success']:
        return jsonify(result), 200
    
    # Return 400 for validation errors (not liked), 404 for not found
    status_code = 404 if "not found" in result.get('error', '').lower() else 400
    return jsonify(result), status_code


@post_bp.route('/posts/<int:post_id>/likes', methods=['GET'])
@token_required
def get_post_likes(post_id):
    """Get users who liked a post"""
    result = post_service.get_post_likes(post_id)
    
    if result['success']:
        return jsonify(result), 200
    return jsonify(result), 404
