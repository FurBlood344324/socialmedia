from flask import Blueprint, request, jsonify
from api.services.comment_service import CommentService
from api.middleware.jwt import token_required

comment_bp = Blueprint('comment', __name__)
comment_service = CommentService()


@comment_bp.route('/posts/<int:post_id>/comments', methods=['POST'])
@token_required
def create_comment(post_id):
    """Create a new comment on a post"""
    data = request.get_json()
    
    if not data or 'content' not in data:
        return jsonify({"success": False, "error": "Content is required"}), 400
    
    result = comment_service.create_comment(
        post_id=post_id,
        user_id=request.user_id,
        content=data.get('content')
    )
    
    if result['success']:
        return jsonify(result), 201
    return jsonify(result), 400


@comment_bp.route('/posts/<int:post_id>/comments', methods=['GET'])
@token_required
def get_post_comments(post_id):
    """Get all comments for a specific post"""
    limit = request.args.get('limit', 100, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    result = comment_service.get_post_comments(post_id, limit, offset)
    return jsonify({"success": True, **result}), 200


@comment_bp.route('/comments/<int:comment_id>', methods=['GET'])
@token_required
def get_comment(comment_id):
    """Get a specific comment by ID"""
    comment = comment_service.get_comment(comment_id)
    
    if comment:
        return jsonify({"success": True, "comment": comment}), 200
    return jsonify({"success": False, "error": "Comment not found"}), 404


@comment_bp.route('/comments/<int:comment_id>', methods=['PUT'])
@token_required
def update_comment(comment_id):
    """Update a comment (only owner can update)"""
    data = request.get_json()
    
    if not data or 'content' not in data:
        return jsonify({"success": False, "error": "Content is required"}), 400
    
    result = comment_service.update_comment(
        comment_id=comment_id,
        user_id=request.user_id,
        content=data.get('content')
    )
    
    if result['success']:
        return jsonify(result), 200
    
    # Return 403 for permission errors, 404 for not found
    status_code = 403 if "only" in result.get('error', '').lower() else 404
    return jsonify(result), status_code


@comment_bp.route('/comments/<int:comment_id>', methods=['DELETE'])
@token_required
def delete_comment(comment_id):
    """Delete a comment (only owner can delete)"""
    result = comment_service.delete_comment(comment_id, request.user_id)
    
    if result['success']:
        return jsonify(result), 200
    
    # Return 403 for permission errors, 404 for not found
    status_code = 403 if "only" in result.get('error', '').lower() else 404
    return jsonify(result), status_code
