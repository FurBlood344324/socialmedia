from flask import Blueprint, request, jsonify, make_response, g
from api.services.auth_service import AuthService
from api.services.user_service import UserService
from api.middleware.authorization import token_required, get_user_id

user_bp = Blueprint('auth', __name__, url_prefix='/auth')
auth_service = AuthService()
user_service = UserService()


@user_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()

        username = data.get("username")
        email = data.get("email")
        password = data.get("password")
        bio = data.get("bio")
        profile_picture_url = data.get("profile_picture_url")
        is_private = data.get("is_private", False)

        if not username or not email or not password:
            return make_response(jsonify({"error": "Username, email and password are required"}), 400)

        result = auth_service.register(
            username=username,
            email=email,
            password=password,
            bio=bio,
            profile_picture_url=profile_picture_url,
            is_private=is_private
        )

        if not result["success"]:
            return make_response(jsonify({"error": result["error"]}), 400)

        return make_response(jsonify(result), 201)

    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 500)


@user_bp.route('/login', methods=['POST'])
def login():
    """Login and get JWT token"""
    try:
        data = request.get_json()

        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return make_response(jsonify({"error": "Username and password are required"}), 400)

        result = auth_service.login(username=username, password=password)

        if not result["success"]:
            return make_response(jsonify({"error": result["error"]}), 401)

        return make_response(jsonify({
            "token": result["token"],
            "user": result["user"]
        }), 200)

    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 500)


@user_bp.route('/getuserid', methods=['GET'])
@get_user_id()
def get_id():
    """Get user_id from token - handled by decorator"""
    return make_response(jsonify({"error": "Error"}), 500)


@user_bp.route('/me', methods=['GET'])
@token_required
def get_current_user():
    """Get current authenticated user's profile"""
    try:
        user = auth_service.get_user_by_id(g.current_user_id)

        if not user:
            return make_response(jsonify({"error": "User not found"}), 404)

        return make_response(jsonify({"user": user}), 200)

    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 500)


@user_bp.route('/me', methods=['PUT'])
@token_required
def update_current_user():
    """Update current authenticated user's profile"""
    try:
        data = request.get_json()

        result = user_service.update_profile(g.current_user_id, data)

        if not result["success"]:
            return make_response(jsonify({"error": result["error"]}), 400)

        return make_response(jsonify(result), 200)

    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 500)


@user_bp.route('/me', methods=['DELETE'])
@token_required
def delete_current_user():
    """Delete current authenticated user's account"""
    try:
        result = user_service.delete_account(g.current_user_id)

        if not result["success"]:
            return make_response(jsonify({"error": result["error"]}), 400)

        return make_response(jsonify(result), 200)

    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 500)


# ============================================
# Public User Endpoints (for viewing other users)
# ============================================

@user_bp.route('/users', methods=['GET'])
@token_required
def get_all_users():
    """Get all users with pagination"""
    try:
        limit = request.args.get('limit', 100, type=int)
        offset = request.args.get('offset', 0, type=int)

        users = user_service.get_all_users(limit=limit, offset=offset)

        return make_response(jsonify({"users": users, "count": len(users)}), 200)

    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 500)


@user_bp.route('/users/search', methods=['GET'])
@token_required
def search_users():
    """Search users by username"""
    try:
        query = request.args.get('q', '')
        limit = request.args.get('limit', 20, type=int)

        if not query:
            return make_response(jsonify({"error": "Search query 'q' is required"}), 400)

        users = user_service.search_users(query=query, limit=limit)

        return make_response(jsonify({"users": users, "count": len(users)}), 200)

    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 500)


@user_bp.route('/users/<int:user_id>', methods=['GET'])
@token_required
def get_user_by_id(user_id):
    """Get a specific user by ID"""
    try:
        user = user_service.get_user(user_id=user_id)

        if not user:
            return make_response(jsonify({"error": "User not found"}), 404)

        return make_response(jsonify({"user": user}), 200)

    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 500)


@user_bp.route('/users/username/<string:username>', methods=['GET'])
@token_required
def get_user_by_username(username):
    """Get a specific user by username"""
    try:
        user = user_service.get_user(username=username)

        if not user:
            return make_response(jsonify({"error": "User not found"}), 404)

        return make_response(jsonify({"user": user}), 200)

    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 500)
